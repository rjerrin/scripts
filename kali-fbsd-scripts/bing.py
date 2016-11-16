#!/usr/local/bin/python



import requests
import argparse
import re
import socket
import sys


http_print = None
csv=None

def get_results(rmt):
    global http_print
    global csv
    results = []
    if re.match('^\w',rmt):
        rmt = socket.gethostbyname(rmt)

    query = "http://www.bing.com/search?q=ip%3A"+ rmt + "&go=&qs=n&first=${page}0&FORM=PERE" 
    r = requests.get(query)
    count = re.findall('<span class="sb_count">(\d+)\sresults</span>',r.text)
    if len(count) == 0:
        print "No results found"
        exit(0)
    else:
        buf = re.findall('<a\s?href="https?://(.+?)/.+?\s?h=".+?">',r.text)
        for result in buf:
            if re.match('go.microsoft.com',result):
                continue
            else:
                if result not in results:
                    results.append(result)
    for url in results:
        if http_print == 1 and csv ==1:
            print rmt + "," 'http://' + url
        elif http_print == 1 and csv == None:
            print  'http://' + url
        elif http_print == None and csv ==1:
            print rmt + "," + url
        else:
            print url
            

def main():
    global http_print
    global Host
    global csv
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pout",  help="add http to output",action="store_true")
    parser.add_argument("-c", "--csv",  help="csv output",action="store_true")
    parser.add_argument("-i", "--host", help="ip/host address to be searched for",
                        dest="host")
    psr  = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)

    if not psr.host:
        parser.print_help()
        exit(1)
        
    if  psr.pout: http_print = 1
    if  psr.csv:  csv = 1
    
    Host = psr.host
    get_results(Host)


if __name__ == '__main__':
    main()

        

            
    
    
    
    
    



