# unicast2multicast-translator

## Background & Goal
This project is part of a larger effort called 
[Multicast to the Grandma](https://datatracker.ietf.org/meeting/104/materials/slides-104-mboned-mttg-01) (MTTG).
Put briefly, the goal of MTTG is to bring applications that rely on multicast infrastructure to users in networks that 
do not support multicast.
The key idea is to automatically translate unicast traffic to multicast traffic as the traffic enters a 
multicast-enabled network from a unicast-only network, and vice versa when the traffic enters a unicast-only network 
from a multicast-enabled network.
So far, the latter (multicast to unicast translation) has been achieved using 
[Automatic Multicast Tunneling](https://datatracker.ietf.org/doc/html/rfc7450) (AMT), which, as the name suggests, 
essentially tunnels multicast traffic by wrapping it in unicast packets when the traffic leaves the multicast-enabled 
network, such that the traffic can travel across the unicast-only network and ultimately be unwrapped by the receiving 
end host.

While AMT allows for delivery of content originating from (and sent as multicast) a host in a multicast-enabled network
(e.g., the [Multicast Backbone](https://en.wikipedia.org/wiki/Mbone) (Mbone)) to receivers in unicast-only networks, it
does not provide unicast-to-multicast translation, as stated in the February 2015 revision of the
[RFC](https://datatracker.ietf.org/doc/html/rfc7450#section-2):

> This document does not describe any methods for sourcing multicast traffic from isolated sites, as this topic is out 
> of scope.

A different solution is therefore needed to enable a host in a unicast-only network to source content intended for 
multiple recipients in multicast-enabled networks (and/or in unicast-only networks where there is a multicast-enabled 
transit network with AMT support between the source and the receiver).
The goal of this project is to develop a service that performs unicast-to-multicast translation to enable such 
unicast-only sources to utilize the multicast capabilities of the (transit) multicast-enabled networks between the 
source and its receivers.
