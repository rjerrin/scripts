#!/usr/local/bin/python 
# Goofile v1.5
# My Website: http://www.g13net.com
# Project Page: http://code.google.com/p/goofile
#
# TheHarvester used for inspiration
# A many thanks to the Edge-Security team!           
# 

import string
import requests
import sys
import re
import getopt

print "\n-------------------------------------"
print "|Goofile v1.5	                    |"
print "|Coded by Thomas (G13) Richards     |"
print "|www.g13net.com                     |"
print "|code.google.com/p/goofile          |"
print "-------------------------------------\n\n"

result =[]

def usage():
 print "usage: goofile options \n"
 print "       -d: domain to search\n"
 print "       -f: filetype (ex. pdf)\n"
 print "example:./goofile.py -d test.com -f txt\n" 
 sys.exit()

def run(dmn,file):
 google_domain = 'www.google.com'
 search_query = "/search?&q=site:"+ dmn + "+filetype:" + file + "&filter=0"
 url = 'http://' + google_domain + search_query
 data = requests.get(url)
 print data.text
 buf = [ url for url  in  re.findall('url\?q=(.+?)&',data.text) ]
 return buf

def search(argv):
	if len(sys.argv) < 2: 
		usage() 
	try :
	      opts, args = getopt.getopt(argv,"d:f:")
 
	except getopt.GetoptError:
  	     	usage()
                print "opt error\n"
		sys.exit()
	
	for opt,arg in opts :
    	   	if opt == '-f' :
			file=arg
		elif opt == '-d':
			dmn=arg
	
	print "Searching in "+dmn+" for "+ file
	print "========================================"
        data = run(dmn,file)
	for x in data:
         if re.search("\.%s$" % file, x,re.UNICODE ):
          print x
	  if result.count(x) == 0:
           result.append(x)
	
			

        print "\nFiles found:"
	print "====================\n"
	if result==[]:
		print "No results were found"
	else:
         for x in result:
          print x
	  print "====================\n"
	

if __name__ == "__main__":
        print sys.argv[1:]
        search(sys.argv[1:])
	
