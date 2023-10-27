# Translator Linux Hardening - Linux systemd, nftables
Following is proposal how to harden Unicast To Multicast Translator, tested on Debian Linux 12
- use systemd security features to vastly reduce privileges of translator systemd service 
- use nftables Linux in-kernel firewall to harden host-OS and translator, allowing to block sources
- nftables does collect possibly handy overall and per stream statistics (DOS/DDoS aspects)

# systemd 
Create user for running unicast to multicast translator:
```
useradd --system u2mt
```

Deploy translator to /srv/u2mt directory, ownership and write only by root (all over the place)

Copy u2mt.service to /etc/systemd/system/

Enable service:
```
systemctl enable u2mt
```
If no nftables firewall is desired, then start:
```
systemctl start u2mt
```
Review status:
```
systemctl status u2mt
```
Analyze security settings:
```
systemd-analyze security u2mt
```
Explanations of the settings can be found here: https://docs.arbitrary.ch/security/systemd.html

# nftables
Review sample nftables.conf:
- adjust MGMT and MGMT6 sets with permitted SSH hosts
- add system DNS resolver addresses to DNS set
- add default IP of multicast menu to MENU set (hostname->IP will be looked after separate service)
- has sets for blacklisting/whitelisting of certain streaming sources 

Deploy nftables.conf to /etc/nftables.conf
Check syntax:
```
nft -c -f /etc/nftables
```
Finally:
```
systemctl enable nftables
systemctl restart nftables
```
List ruleset, includes overall streaming and per streaming source stats:
```
nft list ruleset
```

# nftables mutlicast menu IP update
If there is a potential for multicast menu IP to change (e.g., cloud service hosted menu), then small script executed as systemd service can periodically resolve hostname of multicast menu in use by translator script (MULTICASTMENU_ADD_URL in /srv/u2mt/constants.py). In case of change of host's IP address, the MENU nftables set is refreshed accordingly.

deploy u2mt-nftables.service to /etc/systemd/system/\
deploy u2mt-nftables.sh to /srv/u2mt-nftables
enable and start:
```
systemctl enable u2mt-nftables.service
systemctl start u2mt-nftables.service
```
review logs:
```
journalctl --unit u2mt-nftables
```

# cheat sheet
For quick hints how to deal with translator services and other related tasks, copy HOWTO.TXT to your ~ and feel free to put into .bashrc
```
cat ~/HOWTO.TXT
