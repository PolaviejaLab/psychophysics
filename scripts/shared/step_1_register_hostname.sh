#!/bin/bash

apt-get install dnsutils

RED="\033[0;32m"
NC="\033[0m"

HOSTNAME=$(hostname)
IP=$(hostname -i | cut -f 1 -d\ )

echo -e "About to register ${RED}$HOSTNAME${NC} with IP ${RED}$IP${NC}"

read -p "Are you sure?" -n 1 -r
echo -e "\n"

if [[ $REPLY =~ ^[Yy]$ ]]
then
cat <<EOF | nsupdate
server pdc.champalimaud.pt
zone champalimaud.pt
update delete $HOSTNAME.champalimaud.pt. A
update add $HOSTNAME.champalimaud.pt. 86400 A $IP
show
send
EOF
fi

