#!/bin/bash
#daemon to update nftables named set MENU by translator menu host IP
#khendrych@juniper.net
#to list nftables named set: nft list set inet filter MENU

tmp=$( mktemp )

while true; do
  #retrieve hostname from translator settings 
  MENU_HOST=$( grep MULTICASTMENU_ADD_URL /srv/u2mt/constants.py | cut -f3 -d/ )

  if host $MENU_HOST > $tmp; then
    MENU_IP=$( cat $tmp | grep "has address" | cut -f4 -d" ")	

    if ! nft get element inet filter MENU { $MENU_IP } &>/dev/null; then
      #flush set and add new IP if not present in set MENU
      nft flush set inet filter MENU 
      echo "Updating nftables MENU set by $MENU_HOST IP $MENU_IP"
      nft add element inet filter MENU { $MENU_IP }

    else
      echo "Nothing to do, $MENU_HOST IP $MENU_IP already in nftables MENU set"
    fi

  else
    echo "Error resolving IP of $MENU_HOST"
  fi

  sleep 600

done

rm $tmp
