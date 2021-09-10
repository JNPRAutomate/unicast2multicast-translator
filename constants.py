import ipaddress

# =============================================== DEFAULT CONFIGURATION ================================================
# Default port to bind the translator's unicast server socket to.
DEFAULT_UNICAST_SRV_PORT = 9001
# Default address space to pick multicast destination addresses (groups) from for the translated unicast streams.
DEFAULT_MULTICAST_ADDR_SPACE = ipaddress.IPv4Network('232.0.0.0/8')
# Default port to use when forwarding payload received on the translator's unicast server socket as multicast.
DEFAULT_MULTICAST_PORT = 9002
# URL to use when submitting stream information to the Multicast Menu
MULTICASTMENU_ADD_URL = 'https://multicastmenu.herokuapp.com/add/'
# Email address to use when submitting stream information to the Multicast Menu. Lenny has OK'ed using his email address
# until we have a group email.
MULTICASTMENU_EMAIL = 'lenny@juniper.net'
# Number of worker threads dedicated to submitting stream information to the Multicast Menu.
MULTICASTMENU_THREADS = 10
# ======================================================================================================================
