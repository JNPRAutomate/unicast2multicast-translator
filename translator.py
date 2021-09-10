import argparse
import concurrent.futures as cf
import ipaddress
import random
import socket
import threading

import requests

import constants
import utils


class Translator:
    """
    Translates unicast UDP to multicast UDP.
    """

    def __init__(self, ucast_srv_ip, ucast_srv_port, mcast_addr_space, mcast_port, read_buffer_size=1514,
                 read_timeout_s=5.0, mcast_ttl=32):
        """
        Create a new Translator instance.

        The created Translator instance will be configured to listen for unicast UDP on the IPv4 address and port you
        specify here. However, note that the Translator will not start listening for UDP packets until you call start().

        :param ucast_srv_ip: IPv4 address to listen for unicast UDP on.
        :param ucast_srv_port: Port to listen for unicast UDP on.
        :param mcast_addr_space: Address space to pick multicast groups (IP addresses) from. Each unicast stream will be
        translated to a multicast group in this address space.
        :param mcast_port: Port number to use as the destination port when forwarding unicast flows as multicast flows.
        :param read_buffer_size: Size of the receive buffer (when receiving unicast packets).
        :param read_timeout_s: Timeout when reading from the unicast socket. A lower timeout will make a call to stop()
        more responsive, at the cost of more CPU cycles spent on busy waiting.
        :param mcast_ttl: TTL to use for the translated packets (i.e., the forwarded multicast packets).
        """
        if isinstance(ucast_srv_ip, ipaddress.IPv4Address):
            # The socket API expects IP addresses in string form, so convert to str if IPv4Address provided.
            ucast_srv_ip = str(ucast_srv_ip)
        if not isinstance(ucast_srv_ip, str):
            raise ValueError(f'ucast_srv_ip must be an ipaddress.IPv4Address or a str, but was a {type(ucast_srv_ip)}')
        self._srv_ip = ucast_srv_ip
        self._srv_port = ucast_srv_port
        if mcast_addr_space.prefixlen >= 31:
            errmsg = f'The address space {str(mcast_addr_space)} only contains a network address and a broadcast ' \
                     f'address, but no host addresses.'
            raise ValueError(errmsg)
        self._addr_space = mcast_addr_space
        # We'll use the same destination port number across all multicast groups.
        self._mcast_dst_port = mcast_port
        self._buffer_size = read_buffer_size
        self._read_timeout_s = read_timeout_s
        self._mcast_ttl = mcast_ttl
        # The Translator's Forwarding Information Base: maps a src ip and src port to its respective multicast group.
        self._fib = dict()
        # Currently allocated multicast addresses (addresses that we are translating to for current clients).
        self._allocated_mcast_addrs = set()
        # For synchronizing access to properties that are used by multiple threads.
        self._lock = threading.Lock()
        # Flag indicating if the translator has been started.
        self._started = threading.Event()
        # Flag indicating that termination of the translator has been initiated.
        self._termination_initiated = threading.Event()
        # Flag indicating if termination of the translator has concluded.
        self._terminated = threading.Event()
        # Create a new thread that will read from the unicast socket and write to the multicast socket.
        self._translation_thread = threading.Thread(target=self._translation_loop)
        # Create a pool of worker threads that will handle submission of stream information to the Multicast Menu.
        self._mcastmenu_threadpool = cf.ThreadPoolExecutor(max_workers=constants.MULTICASTMENU_THREADS,
                                                           thread_name_prefix='multicastmenu_thread')
        # Determine the IP of the interface that multicast packets are sent out on (i.e., determine the source address
        # for outbound multicast).
        self._mcast_src_ip = utils.get_ipv4(self._addr_space[1])

    def start(self):
        """
        Start this Translator.

        This method should only be called once. A Translator is use-once-then-throw-away, i.e., a Translator cannot be
        restarted.

        :return:  None.
        """
        # Checking and then setting the _started Event instance could produce a TOCTOU bug if multiple threads call
        # start() concurrently and make it past the is_set() call before any of them call set(), so we need locking here
        # as well.
        self._lock.acquire()
        if self._started.is_set():
            raise RuntimeError('Translator already started.')
        self._started.set()
        self._lock.release()
        # Prepare the input (unicast) socket and the output (multicast) socket.
        self._init_srv_sckt()
        self._init_mcast_sckt()
        # Start the translation loop in a separate, dedicated thread.
        self._translation_thread.start()

    def terminate(self, blocking=False, blocking_timeout_s=None):
        """
        Terminate this Translator.

        Note that termination does not happen instantaneously and thus may not have materialized at the time this call
        returns (unless you set blocking=True and blocking_timeout_s=None, which will make this method block until the
        termination concludes). Specifically, if the Translator is currently in the process of translating a UDP packet,
        termination happens after that translation concludes. If the Translator is currently waiting for a UDP packet to
        translate, termination either happens when such a packet has been received and translated, or when the read
        timeout (as defined in __init__) expires, whichever of the two occurs first.

        :param blocking: If set to True, block until termination has concluded or the blocking_timeout_s (if any)
        expires, whichever occurs first.
        :param blocking_timeout_s: Maximum time (in seconds, or fractions thereof) to wait for termination. Set to None
        to wait indefinitely. Only considered when blocking=True.

        :return: None.
        """
        print('Termination initiated...')
        # Signal to the translation loop that it should terminate.
        self._termination_initiated.set()
        if blocking:
            # Wait until the translation loop has set the terminated flag to indicate that it has exited.
            self._terminated.wait(timeout=blocking_timeout_s)

    def _init_srv_sckt(self):
        """
        Prepare the unicast server socket (the socket that will receive unicast UDP from unicast-only clients).

        :return: None
        """
        sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sckt.bind((self._srv_ip, self._srv_port))
        sckt.settimeout(self._read_timeout_s)
        self._srv_sckt = sckt

    def _init_mcast_sckt(self):
        """
        Prepare the multicast socket (the socket on which all payload received from the unicast server socket will be
        forwarded as multicast UDP packets).

        :return: None
        """
        sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sckt.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self._mcast_ttl)
        self._mcast_sckt = sckt

    def _clean_up(self):
        """
        Perform clean up at termination time (close sockets etc.).

        :return: None
        """
        # TODO free all resources.
        self._srv_sckt.close()
        self._mcast_sckt.close()
        self._mcastmenu_threadpool.shutdown(wait=True, cancel_futures=True)

    def _translation_loop(self):
        """
        Initiate this Translator's work loop. Reads from the unicast socket and writes to the multicast socket.

        :return: None.
        """
        try:
            while not self._termination_initiated.is_set():
                try:
                    payload, src_addr = self._srv_sckt.recvfrom(self._buffer_size)
                    # Look up the multicast address allocated for this client, if any.
                    mcast_addr = self._fib.get(src_addr, None)
                    if mcast_addr is None:
                        # No multicast address currently allocated for this client. Allocate one.
                        mcast_addr = self._alloc_mcast_addr(src_addr)
                        if mcast_addr is not None:
                            # Publish the new stream on the Multicast Menu if we successfully allocated a multicast
                            # address. We'll let a worker thread handle the communication with the multicast menu
                            # s.t. the I/O does not block translation of any ongoing streams (i.e., it is important we
                            # do not block the thread that runs the translation loop).
                            desc = f'Translated stream originating from {src_addr[0]}'
                            self._mcastmenu_threadpool.submit(self._add_to_multicast_menu, mcast_addr,
                                                              constants.MULTICASTMENU_EMAIL, desc)
                    if mcast_addr is not None:
                        # Forward the payload to the multicast address allocated for this client.
                        self._mcast_sckt.sendto(payload, (str(mcast_addr), self._mcast_dst_port))
                    else:
                        # mcast_addr will be None if we've run out of addresses.
                        # TODO silently discard the packet or communicate this to the client?
                        print(f'WARNING: run out of multicast addresses, cannot serve {src_addr}')
                except socket.timeout:
                    # No data available to read during this iteration.
                    print('read timeout: nothing to be translated this iteration')
        finally:
            # Free all resources (close all sockets etc.)
            self._clean_up()
            # Signal that we have terminated the translation loop.
            self._terminated.set()

    def _alloc_mcast_addr(self, client_addr):
        try:
            self._lock.acquire()
            assert client_addr not in self._fib, f'A multicast address ({self._fib[client_addr]}) has already been ' \
                                                 f'allocated for this client address ({client_addr}).'
            # Check if we've already used up all addresses in the address space (-2 is to exclude the network address
            # and the broadcast address).
            # TODO: only allow use of up to X% of the available addresses (to reduce address selection workload below)?
            if len(self._allocated_mcast_addrs) == self._addr_space.num_addresses - 2:
                # All addresses in the address space are currently in use by other clients.
                return None
            # Randomly generate an index that will be used to pick an address in the address space at random:
            # - use min index = 1 to exclude the network address from consideration;
            # - use max index = self._addr_space.num_addresses - 2 to exclude the broadcast address from consideration.
            min_idx = 1
            max_idx = self._addr_space.num_addresses - 2
            addr_idx = random.randint(min_idx, max_idx)
            attempts = 1
            max_attempts = 10
            # If the address we picked is already in use, allow up to max_attempts attempts at picking a new address at
            # random. If we did not cap the number of attempts, we could (theoretically) end up looping for a very long
            # time ("indefinitely") if the address space is very large and only has a single usable address left.
            while self._addr_space[addr_idx] in self._allocated_mcast_addrs and attempts < max_attempts:
                addr_idx = random.randint(min_idx, max_idx)
                attempts += 1
            # If we were unsuccessful at picking an address at random (within the allowed number of attempts), we
            # instead try addresses linearly, starting from the last address we picked at random that was already in
            # use. As a result, the address selection is not truly (pseudo) random as any address that is an immediate
            # neighbor of any (continuous block of) address(es) that is (are) already in use has a greater chance of
            # being selected. However, this "imbalance" is acceptable for our purposes.
            while self._addr_space[addr_idx] in self._allocated_mcast_addrs:
                addr_idx += 1
                addr_idx = min_idx if addr_idx > max_idx else addr_idx
            # Add information about the newly allocated address to the FIB and set of multicast addresses in use.
            mcast_addr = self._addr_space[addr_idx]
            assert mcast_addr not in self._allocated_mcast_addrs, f'picked a multicast address ({mcast_addr}) that ' \
                                                                  f'was already allocated'
            self._fib[client_addr] = mcast_addr
            self._allocated_mcast_addrs.add(mcast_addr)
            print(f'Multicast address ({mcast_addr}, {self._mcast_dst_port}) allocated for {client_addr}.')
            return mcast_addr
        finally:
            self._lock.release()

    def _add_to_multicast_menu(self, mcast_dst_ip, email, description):
        """
        Publish information about a new stream (that is now being translated) on the Multicast Menu by submitting the
        form at constants.MULTICASTMENU_ADD_URL.

        :param mcast_dst_ip: The multicast destination IP (multicast group) used for the new stream.
        :param email: Contact email (currently a required field on the form, to be removed)
        :param description: A description of the stream.

        :return: None
        """
        errmsg = f'Attempt to add amt://{self._mcast_src_ip}@{mcast_dst_ip}:{self._mcast_dst_port} to the Multicast ' \
                 f'Menu failed (email={email}; description={description}): '
        try:
            # To create an entry for the stream in the Multicast Menu, we're going to programmatically submit the form
            # at constants.MULTICASTMENU_ADD_URL since there is currently no API for the Multicast Menu. However, we
            # cannot simply do a single, one-shot POST request to that URL as the Multicast Menu uses Django's CSRF
            # protection. To get around this, we must first establish a session with the Multicast Menu and send a GET
            # request to the form's webpage to get our hands on a CSRF protection token.
            sess = requests.session()
            resp_get = sess.get(constants.MULTICASTMENU_ADD_URL)
            if resp_get.status_code != 200:
                errmsg += f'GET resulted in status code {resp_get.status_code}. Response body:\n{resp_get.text}'
                print(errmsg)
                return
            csrftoken = sess.cookies.get('csrftoken')
            if csrftoken is None:
                errmsg += 'no csrftoken found in session.'
                print(errmsg)
                return
            # We can now submit the form using a POST request. In doing so, we must provide the CSRF protection token
            # alongside the other form parameters (the form has a hidden input tag that contains the CSRF protection
            # token) and as a cookie (but the requests module takes care of this part automatically because we're using
            # a session). Also note that we must set the Referer header field (to the same URL we're submitting the form
            # to) as otherwise we'll get rejected by the server.
            form_params = {'csrfmiddlewaretoken': csrftoken, 'source': self._mcast_src_ip, 'group': str(mcast_dst_ip),
                           'udp_port': str(self._mcast_dst_port), 'email': email, 'description': str(description),
                           'Add': 'Add'}
            header_fields = {'Referer': constants.MULTICASTMENU_ADD_URL}
            resp_post = sess.post(constants.MULTICASTMENU_ADD_URL, data=form_params, headers=header_fields)
            if resp_post.status_code != 200:
                errmsg += f'POST resulted in status code {resp_post.status_code}. Response body:\n{resp_post.text}'
                print(errmsg)
                return
            msg = f'Added amt://{self._mcast_src_ip}@{mcast_dst_ip}:{self._mcast_dst_port} to the Multicast Menu ' \
                  f'(email={email}; description={description}).'
            print(msg)
        except Exception as e:
            errmsg += f'encountered a {type(e)} with message "{e}".'
            print(errmsg)

    # TODO add functionality that evicts addresses from the FIB when they've been inactive for a while.


if __name__ == '__main__':
    desc = 'Start a unicast-to-multicast translation service on this machine.'
    ap = argparse.ArgumentParser(description=desc)

    ucast_nif_ip_argname = 'unicast-nif-ip'
    h = 'IP address of the network interface to listen for unicast on. The default value is what was determined to ' \
        'be the primary network interface of this machine (i.e., the network interface that has a default route). ' \
        'Note that this address may not be a public address if this machine is behind NAT or a VPN. ' \
        'Default: %(default)s'
    ap.add_argument(f'--{ucast_nif_ip_argname}', type=ipaddress.IPv4Address, default=utils.get_ipv4(), help=h)

    ucast_port_argname = 'unicast-port'
    h = 'Port number to listen for unicast on. Default: %(default)d'
    ap.add_argument(f'--{ucast_port_argname}', type=int, default=constants.DEFAULT_UNICAST_SRV_PORT, help=h)

    mcast_addr_space_argname = 'multicast-addr-space'
    h = 'Address space to (randomly) pick destination multicast addresses (groups) from for the translated unicast ' \
        'flows. Default: %(default)s'
    ap.add_argument(f'--{mcast_addr_space_argname}', type=ipaddress.IPv4Network,
                    default=constants.DEFAULT_MULTICAST_ADDR_SPACE, help=h)

    mcast_port_argnmame = 'multicast-port'
    h = 'Port number to use as the destination port when forwarding unicast flows as multicast flows. The same port ' \
        'number will be used for all translated flows. Thus, a translated flow is identified solely by its assigned ' \
        'multicast IP address (group). Default: %(default)d'
    ap.add_argument(f'--{mcast_port_argnmame}', type=int, default=constants.DEFAULT_MULTICAST_PORT, help=h)

    args = ap.parse_args()
    ucast_ip = getattr(args, utils.argname_to_attr(ucast_nif_ip_argname))
    ucast_port = getattr(args, utils.argname_to_attr(ucast_port_argname))
    mcast_addr_space = getattr(args, utils.argname_to_attr(mcast_addr_space_argname))
    mcast_port = getattr(args, utils.argname_to_attr(mcast_port_argnmame))

    # Fire up the translator.
    t = Translator(ucast_srv_ip=ucast_ip, ucast_srv_port=ucast_port, mcast_addr_space=mcast_addr_space,
                   mcast_port=mcast_port)
    t.start()
    input('Press enter to terminate the translator...\n')
    t.terminate(blocking=True)
