from scapy.all import (
    BitField,
    IPField,
    MACField,
    Packet,
    PacketListField,
    ShortField,
    XStrFixedLenField
)
from scapy.contrib.igmpv3 import IGMPv3
from scapy.layers.inet import IP

from constants import (
    AMT_MEM_QUERY,
    AMT_MEM_UPD,
    AMT_MULT_DATA,
    AMT_RELAY_ADV,
    AMT_RELAY_DISCO,
    AMT_REQUEST,
    AMT_TEARDOWN,
    MCAST_ANYCAST,
    MSG_TYPE_LEN,
    VERSION_LEN
)


class AMT_Discovery(Packet):
    name = "AMT_Discovery"
    fields_desc = [ 
        BitField("version", 0, VERSION_LEN),
        BitField("type", AMT_RELAY_DISCO, MSG_TYPE_LEN),
        BitField("rsvd", 0, 24),
        XStrFixedLenField("nonce", 0, 4)
    ]


class AMT_Relay_Advertisement(Packet):
    name = "AMT_Relay_Advertisement"
    fields_desc = [
        BitField("version", 0, VERSION_LEN),
        BitField("type", AMT_RELAY_ADV, MSG_TYPE_LEN),
        BitField("rsvd", 0, 24),
        XStrFixedLenField("nonce", 0, 4),
        IPField("relay_addr", MCAST_ANYCAST)
    ]


class AMT_Relay_Request(Packet):
    name = "AMT_Relay_Request"
    fields_desc = [ 
        BitField("version", 0, VERSION_LEN),
        BitField("type", AMT_REQUEST, MSG_TYPE_LEN),
        BitField("rsvd1", 0, 7),
        BitField("p_flag", 0, 1),
        BitField("rsvd2", 0, 16),
        XStrFixedLenField("nonce", 0, 4)
    ]


class AMT_Membership_Query(Packet):
    name = "AMT_Membership_Query"
    fields_desc = [
        BitField("version", 0, VERSION_LEN),
        BitField("type", AMT_MEM_QUERY, MSG_TYPE_LEN),
        BitField("rsvd1", 0, 6),
        BitField("l_flag", 0, 1),
        BitField("g_flag", 0, 1),
        MACField("response_mac", 0),
        XStrFixedLenField("nonce", 0, 4),
        PacketListField("amt_ip", None, IP),
        PacketListField("amt_igmpv3", None, IGMPv3)
    ]


class AMT_Membership_Update(Packet):
    name = "AMT_Membership_Update"

    fields_desc = [
        BitField("version", 0, VERSION_LEN),
        BitField("type", AMT_MEM_UPD, MSG_TYPE_LEN),
        BitField("rsvd1", 0, 8),
        MACField("response_mac", 0),
        XStrFixedLenField("nonce", 0, 4),
        PacketListField("amt_igmpv3", None, IGMPv3)
    ]


class AMT_Multicast_Data(Packet):
    name = "AMT_Multicast_Data"
    fields_desc = [
        BitField("version", 0, VERSION_LEN),
        BitField("type", AMT_MULT_DATA, 4),
        BitField("rsvd", 0, 8),
        PacketListField("amt_ip", None, IP)
    ]


class AMT_Teardown(Packet):
    name = "AMT_Teardown"
    fields_desc = [
        BitField("version", 0, VERSION_LEN),
        BitField("type", AMT_TEARDOWN, 4),
        BitField("rsvd", 0, 8),
        MACField("response_mac", 0),
        XStrFixedLenField("nonce", 0, 4),
        ShortField("gw_port_num", 0),
        IPField("gw_ip_addr", MCAST_ANYCAST)
    ]
