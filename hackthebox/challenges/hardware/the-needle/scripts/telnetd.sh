#!/bin/sh
sign=`cat /etc/config/sign`
TELNETD=`rgdb
TELNETD=`rgdb -g /sys/telnetd`
if [ "$TELNETD" = "true" ]; then
	echo "Start telnetd ..." > /dev/console
	if [ -f "/usr/sbin/login" ]; then
		lf=`rgbd -i -g /runtime/layout/lanif`
		telnetd -l "/usr/sbin/login" -u Device_Admin:$sign	-i $lf &
	else
		telnetd &
	fi
fi