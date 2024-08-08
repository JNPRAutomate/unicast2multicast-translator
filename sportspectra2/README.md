Mobile App for OffNet Sourcing Requirements and Functionality

High level description:

Goals of this project is to develop a mobile app that makes it very simple for anyone to source and receive multicast video using the TreeDN architecture. At a high level, a sourcing user will open app and send video from device camera as a unicast data stream to a Multicast Translator sitting in a TreeDN network. The Translator receives a video stream and translates the destination addresses to a multicast address. Then the stream can be received natively by receivers connected natively to the TreeDN network (OnNet receivers), or via AMT by receivers on unicast-only networks (OffNet Receivers). Receiving users will be able to select active multicast streams and view, ideally through the browser, or via some other video app. Ideal use case for this app would be niche sports, along with nature cams.

Low Level Description

Multicast Translator Details

There is currently one Translator deployed at GWU/CAAREN at 162.250.138.12. An earlier version of the Translator was previously deployed at 162.250.138.11, but that should no longer be used at this time. The Translator was developed by Janus Varmarken and hardened by Karel Hendrych. The Translator simply listens for any unicast traffic destined to it with port 9001 and then translates the source address to itself (so that RPF functions properly), the destination address to a multicast group chosen randomly from 232/8 (to avoid L2 address collisions) and the destination port address to 9002. Today, there is only one translator, but assume there will be more. DNS is probably the best option to support multiple translators, so the well-known fqdn for the Translators will be xlator.treedn.net. As more Translators come online, an A record will be added for each new IP. To select the optimal Translator, the app should lookup xlator.treedn.net when sourcing is about to start, get the list of IPs from all the A records, ping each IP and select the one with the lowest RTT. Another approach would be to use anycast, but route flaps might cause traffic to be sent to a different Translator midstream, and it would require global address coordination and make DoS attacking much easier by simply advertising reachability to a non-existent Translator. So we will not use anycast here.

When traffic is sent to the Translator, in addition to translating the SA/DA/DP, the Translator alerts the Multicast Menu (https://menu.treedn.net) of the new stream with the translated SA/Group/DP. It should also include the original source so the MM can include that in the description the SA. The app can leverage the existing MM for a single source of truth or can develop a new one. Further details on the Multicast Translator can be found here:

https://github.com/JNPRAutomate/unicast2multicast-translator

AMT Relay Details

There are currently four public AMT relays, all mapped to the well-known FQDN of amt-relay.treedn.net:

% nslookup amt-relay.treedn.net Server: 100.64.0.1 Address: 100.64.0.1#53

Non-authoritative answer: Name: amt-relay.treedn.net Address: 198.38.23.145 Name: amt-relay.treedn.net Address: 162.250.137.254 Name: amt-relay.treedn.net Address: 164.113.199.110 Name: amt-relay.treedn.net Address: 162.250.136.101

When the app launches, it should discover the AMT Relays by sending AMT Relay Discovery messages to all relays listed with A records for amt-relay.treedn.net. The app should then maintain an ordered list of all relays based on shortest delay received by the AMT Relay Advertisement messages. This is a crude method for determining the nearest relay. See RFC7450 sect 4.2.1 for details on the Relay Discovery messaging and sequence.

The app will list all known sources on the Internet, both from OffNet and OnNet sources. The Multicast Menu will initially act as the single source of truth, but a newer, better portal can be developed if necessary. The challenge will be developing a clean, intuitive UI listing all the stream in a world where there could be thousands or more. Hence, some type of tagging or dir service may be needed here.

When a receiving user selects a stream to watch, it will first attempt to join the traffic natively with an IGMPv3 source-include report. That will likely fail, so the native timeout should have an aggressive timeout (1s default), and be configurable in the settings from 0 (skip native attempt, initiate AMT tunnel immediately) to 5s. If no traffic is received natively before the timeout, should switch to AMT. Select the first relay from the previously ordered list, and no traffic arrives after a configurable timeout (3-5s, default at 3s), select the next relay in the list. Repeat until traffic is received.

Sourcing Details

When sourcing user wants to send, user should have to specify some sort of description/tags pertaining to the stream so that can be listed by the MM/portal.

Receiver Details

Receiver will see all streams listed (with afore-mentioned UI to cleanly, and intuitively find a desired stream). After selecting a stream, receiver will be able to view the video. The ideal tool for viewing the video will be a browser, but browsers prohibit UDP traffic. This leaves several options:

-Leveraging DVB-MABR/MAUD-type L’ interface to allow multicast to be received in the browser. See those specs for details: https://www.etsi.org/deliver/etsi_ts/103700_103799/103769/01.01.01_60/ts_103769v010101p.pdf https://www.ibc.org/technical-papers/ibc2023-tech-papers-multicast-assisted-unicast-delivery/10235.article

-Leverage approach that Lauren took in support multicast to the browser, which is similar to above: https://www.youtube.com/watch?v=5Lgpgq0Aj88&t=4921s https://datatracker.ietf.org/meeting/115/materials/slides-115-mboned-amt-to-the-browser-in-the-multicast-menu-00

-use a video app that supports multicast. VLC4 is one option, but very clunky and fragile

-try to get Multicast Extensions to QUIC to work in a browser. May require dev of chromium: https://datatracker.ietf.org/doc/draft-jholland-quic-multicast/

Diagnostics

Should have a rich set of details for nerds available, as well as diagnostics for troubleshooting when problems arise

Platform Support

-should work on iOS devices (iPhone, iPad), Android devices, Amazon Firestick, MacOS, and Windows. Roku player is a stretch goal

Use cases

-niche sports, nature cams, distance learning for underserved communities

-high bitrate streams- Augmented Reality (AR) livestreaming

Stretch Goals:

-tokenization for incentivizing relay deployment (see Helium, Pollen)

References

To add more stuff here