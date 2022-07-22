import ipaddress

# =============================================== DEFAULT CONFIGURATION ================================================
# Default port to bind the translator's unicast server socket to.
DEFAULT_UNICAST_SRV_PORT = 9001
# Default address space to pick multicast destination addresses (groups) from for the translated unicast streams.
DEFAULT_MULTICAST_ADDR_SPACE = ipaddress.IPv4Network('232.0.0.0/8')
# Default port to use when forwarding payload received on the translator's unicast server socket as multicast.
DEFAULT_MULTICAST_PORT = 9002
# URL to use when submitting stream information to the Multicast Menu
MULTICASTMENU_ADD_URL = 'https://menu.treedn.net/api/add/'
# URL to use when removing stream information from the Multicast Menu
MULTICASTMENU_REMOVE_URL = 'https://menu.treedn.net/api/remove/'
# Number of worker threads dedicated to submitting stream information to the Multicast Menu.
MULTICASTMENU_THREADS = 10
# IPv4 address of Multicast Menu server used to identify streams that originate there.
MULTICASTMENU_SENDER_IP = '54.234.212.72'
# ======================================================================================================================
