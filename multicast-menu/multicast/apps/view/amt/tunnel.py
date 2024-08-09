import socket
import struct
import sys
import logging
from scapy.all import send, IP, UDP, Packet
from scapy.contrib.igmpv3 import IGMPv3, IGMPv3gr, IGMPv3mr
import secrets
from datetime import datetime
import time
import psutil
import random

from constants import DEFAULT_MTU, LOCAL_LOOPBACK, MCAST_ALLHOSTS, MCAST_ANYCAST
from models import (
    AMT_Discovery,
    AMT_Relay_Request,
    AMT_Membership_Query,
    AMT_Membership_Update,
    AMT_Multicast_Data,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="amt_tunnel.log",
    filemode="a",
)
logger = logging.getLogger(__name__)

# Add a stream handler to also log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Define the default relay and its IP addresses
DEFAULT_RELAY = "amt-relay.m2icast.net"
DEFAULT_RELAY_IPS = ["162.250.137.254", "162.250.136.101", "164.113.199.110"]


def setup_socket(amt_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(("", amt_port))
    s.settimeout(60)  # Set a timeout for receiving data
    return s


def send_amt_discovery(ip_layer, udp_layer, nonce):
    amt_layer = AMT_Discovery()
    amt_layer.setfieldval("nonce", nonce)
    discovery_packet = ip_layer / udp_layer / amt_layer
    send(discovery_packet)
    logger.info(
        f"Sent AMT relay discovery to {ip_layer.dst}:2268 with nonce {nonce.hex()}"
    )


def send_amt_request(ip_layer, udp_layer, nonce):
    amt_layer = AMT_Relay_Request()
    amt_layer.setfieldval("nonce", nonce)
    request_packet = ip_layer / udp_layer / amt_layer
    send(request_packet)
    logger.info(
        f"Sent AMT relay request to {ip_layer.dst}:2268 with nonce {nonce.hex()}"
    )


def send_membership_update(ip_layer, udp_layer, nonce, response_mac, multicast, source):
    amt_layer = AMT_Membership_Update()
    amt_layer.setfieldval("nonce", nonce)
    amt_layer.setfieldval("response_mac", response_mac)

    options_pkt = Packet(b"\x00")
    ip_layer2 = IP(src=MCAST_ANYCAST, dst=MCAST_ALLHOSTS, options=[options_pkt])

    igmp_layer = IGMPv3()
    igmp_layer.type = 34

    igmp_layer2 = IGMPv3mr(records=[IGMPv3gr(maddr=multicast, srcaddrs=[source])])

    membership_update_packet = (
        ip_layer / udp_layer / amt_layer / ip_layer2 / igmp_layer / igmp_layer2
    )
    send(membership_update_packet)
    logger.info(
        f"Sent AMT multicast membership update to {ip_layer.dst}:2268 for group {multicast} from source {source}"
    )


def monitor_resources():
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    if cpu_percent > 90 or memory_percent > 90:
        logger.warning(
            f"High resource usage: CPU {cpu_percent}%, Memory {memory_percent}%"
        )
    return cpu_percent, memory_percent


def get_relay_ip(relay):
    if relay == DEFAULT_RELAY:
        return random.choice(DEFAULT_RELAY_IPS)
    return relay


def setup_amt_tunnel(relay, amt_port, multicast, source):
    logger.info(f"Attempting to set up AMT tunnel with relay {relay}")
    s = setup_socket(amt_port)
    logger.info(f"Socket set up on port {amt_port}")

    relay_ip = get_relay_ip(relay)
    ip_layer = IP(dst=relay_ip)
    udp_layer = UDP(sport=amt_port, dport=2268)
    nonce = secrets.token_bytes(4)

    logger.debug(f"Sending AMT discovery to relay {relay_ip}")
    send_amt_discovery(ip_layer, udp_layer, nonce)

    try:
        data, addr = s.recvfrom(8192)
        logger.info(f"Received {len(data)} bytes from relay {addr}")
    except socket.timeout:
        logger.error("Timeout: Did not receive any response from the relay")
        return False, None, None, None, None
    except Exception as e:
        logger.error(f"Failed to receive data from relay: {e}")
        return False, None, None, None, None

    logger.debug(f"Sending AMT request to relay {relay_ip}")
    send_amt_request(ip_layer, udp_layer, nonce)

    try:
        data, addr = s.recvfrom(DEFAULT_MTU)
        membership_query = AMT_Membership_Query(data)
        response_mac = membership_query.response_mac
        logger.info(
            f"Received AMT multicast membership query from {addr} with response MAC {response_mac.hex() if isinstance(response_mac, bytes) else response_mac}"
        )
    except Exception as e:
        logger.error(f"Failed to receive or process membership query: {e}")
        return False, None, None, None, None

    req = struct.pack("=4sl", socket.inet_aton(multicast), socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, req)

    logger.debug(f"Sending membership update to relay {relay_ip}")
    send_membership_update(ip_layer, udp_layer, nonce, response_mac, multicast, source)
    return True, s, ip_layer, udp_layer, nonce, response_mac


def main(relay, source, multicast, amt_port, udp_port):
    logger.info(f"Starting AMT tunnel - Relay: {relay}, Source: {source}, Multicast: {multicast}, AMT Port: {amt_port}, UDP Port: {udp_port}")

    packet_count = 0
    last_packet_time = time.time()
    local_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    relay_index = 0
    max_reconnect_attempts = 5
    reconnect_delay = 5

    while True:
        reconnect_attempts = 0
        while reconnect_attempts < max_reconnect_attempts:
            try:
                current_relay = DEFAULT_RELAY_IPS[relay_index] if relay == DEFAULT_RELAY else relay
                success, s, ip_layer, udp_layer, nonce, response_mac = setup_amt_tunnel(current_relay, amt_port, multicast, source)

                if not success:
                    logger.warning(f"Failed to set up AMT tunnel with relay {current_relay}. Trying next relay.")
                    relay_index = (relay_index + 1) % len(DEFAULT_RELAY_IPS)
                    reconnect_attempts += 1
                    time.sleep(reconnect_delay)
                    continue

                logger.info(f"AMT tunnel established with relay {current_relay}")

                while True:
                    try:
                        data, _ = s.recvfrom(DEFAULT_MTU)
                        amt_packet = AMT_Multicast_Data(data)
                        raw_udp = bytes(amt_packet[UDP].payload)
                        local_socket.sendto(raw_udp, (LOCAL_LOOPBACK, udp_port))

                        packet_count += 1
                        last_packet_time = time.time()

                        if packet_count % 1000 == 0:
                            logger.info(f"Received and forwarded {packet_count} packets")

                    except socket.timeout:
                        if time.time() - last_packet_time > 30:
                            logger.warning("No data received for 30 seconds, sending heartbeat")
                            try:
                                heartbeat_packet = ip_layer / udp_layer / AMT_Membership_Update()
                                send(heartbeat_packet)
                            except Exception as e:
                                logger.error(f"Failed to send heartbeat: {e}")
                                raise  # Re-raise to trigger reconnection

                    except Exception as err:
                        logger.error(f"Error occurred in processing packet: {err}")
                        raise  # Re-raise to trigger reconnection

            except Exception as e:
                logger.error(f"AMT tunnel error: {e}. Attempting to reconnect.")
                if s:
                    s.close()
                reconnect_attempts += 1
                time.sleep(reconnect_delay)

        logger.error(f"Failed to reconnect after {max_reconnect_attempts} attempts. Exiting.")
        break

    logger.info("Exiting AMT tunnel")
    if s:
        s.close()
    local_socket.close()


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(
            "Usage: python tunnel.py <relay> <source> <multicast> <amt_port> <udp_port>"
        )
        sys.exit(1)

    relay, source, multicast = sys.argv[1:4]
    amt_port, udp_port = map(int, sys.argv[4:6])

    main(relay, source, multicast, amt_port, udp_port)