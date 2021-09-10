import ipaddress
import socket


def argname_to_attr(argname):
    """
    Converts an option name in long-form POSIX style to the corresponding Python attribute name.

    :param argname: An option name in long-form POSIX style, without the leading double dashes.

    :return: The corresponding Python attribute name.
    """
    return argname.replace('-', '_')


def get_ipv4(dst_ip=ipaddress.IPv4Address('8.8.8.8')):
    """
    Get the IPv4 address of the network interface on this machine that packets destined for the provided destination IP
    address dst_ip will be sent out on (i.e., determine the network interface that packets destined for dst_ip are
    routed through). Note that the result may NOT be a public IP address if you are behind NAT or connected to a VPN.

    Courtesy of https://stackoverflow.com/a/28950776

    :param dst_ip: A destination IP address. Used to specify that the returned IP address should be the IP address of
    the network interface that routes packets to this destination.

    :return: The IPv4 address of the network interface on this machine that routes packets to dst_ip.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if isinstance(dst_ip, ipaddress.IPv4Address):
        dst_ip = str(dst_ip)
    if not isinstance(dst_ip, str):
        raise ValueError(f'dst_ip must be an ipaddress.IPv4Address or a str, but was a {type(dst_ip)}')
    try:
        # doesn't even have to be reachable
        s.connect((dst_ip, 53))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ipaddress.IPv4Address(ip)
