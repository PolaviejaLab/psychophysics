#!/bin/bash

# First bless the rEFInd boot loader, otherwise Windows will start by default
mkdir /Volumes/esp &&
mount -t msdos /dev/disk0s1 /Volumes/esp &&
bless --mount /Volumes/esp --setBoot --file /Volumes/esp/EFI/refind/refind_x64.efi --shortform &&
umount /Volumes/esp &&
echo "rEFInd blessed successfully"

rmdir /Volumes/esp


# Defaults
hostname="Psychophysics-Unknown"
trackpad=""

# Fill parameters based on MAC address
mac=$(ifconfig en0 | grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}')
ip=$(ifconfig en0 | awk '/inet /{print $2}')

echo $mac

case "$mac" in
	'ac:87:a3:22:e1:0d' )
		hostname="Psychophysics-180"
		trackpad="88-63-DF-ED-7E-8A"
		;;
	'ac:87:a3:18:36:7a' )
		hostname="Psychophysics-179"
		trackpad="88-63-DF-EE-04-2D"
		;;
	'ac:87:a3:22:e0:48' )
		hostname="Psychophysics-155"
		trackpad="88-63-DF-ED-97-D2"
		;;
	'ac:87:a3:1d:f3:66' )
		hostname="Psychophysics-154"
		trackpad="88-63-DF-F1-00-45"
		;;
	'ac:87:a3:18:4e:cd' )
		hostname="Psychophysics-137"
		trackpad="88-63-DF-F1-13-AA"
		;;
	'ac:87:a3:18:36:b6' )
		hostname="Psychophysics-140"
		trackpad="88-63-DF-EE-02-EC"
		;;
esac

# Set hostname
scutil --set HostName $hostname &&
echo "Host name set to $hostname"

# Set trackpad ID
plutil -replace BRPairedDevices -xml "<array><string>$trackpad</string></array>" /Library/Preferences/com.apple.Bluetooth.plist &&
echo "Trackpad $trackpad setup"

# Set name in DNS
hostnamelc=$(echo $hostname | tr '[:upper:]' '[:lower:]')

cat <<EOF | nsupdate
server pdc.champalimaud.pt
zone champalimaud.pt
update delete $hostnamelc.champalimaud.pt. A
update add $hostnamelc.champalimaud.pt 86400 A $ip
send
EOF

