################################################
# Various Lengths of Msgs or Hdrs
################################################
# DEFAULT_MTU = (1500 - (20 + 8))
DEFAULT_MTU = 8192
MSG_TYPE_LEN = 4           # length of msg type
VERSION_LEN = 4            # length of version in packet

################################################
# Different AMT Message Types
################################################
AMT_RELAY_DISCO = 1        # relay discovery
AMT_RELAY_ADV = 2          # relay advertisement
AMT_REQUEST = 3            # request
AMT_MEM_QUERY = 4          # memebership query
AMT_MEM_UPD = 5            # membership update
AMT_MULT_DATA = 6          # multicast data
AMT_TEARDOWN = 7           # teardown (not currently supported)

################################################
# Addresses
################################################
LOCAL_LOOPBACK = "127.0.0.1"
MCAST_ANYCAST = "0.0.0.0"
MCAST_ALLHOSTS = "224.0.0.22"
