# -*- coding: UTF-8 -*-
__author__ = "Powen Ko, www.powenko.com"
# http://127.0.0.1:8888?pin=12&on=1
# http://127.0.0.1:8888?pin=12&on=0
# http://127.0.0.1:8888?pin=10&on=1
# http://127.0.0.1:8888?pin=10&on=0

import sys
import time

t1=4
t2=b" input:"+str(t1).encode('utf-8')


import time, RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)



output_pin1 = 12  # BCM pin 12, BOARD pin 32
output_pin2 = 10  # BCM pin 10, BOARD pin 19
input_pin1 = 18   # BCM pin 18, BOARD pin


GPIO.setup(output_pin1, GPIO.OUT)
GPIO.setup(output_pin2, GPIO.OUT)
GPIO.setup(input_pin1, GPIO.IN)
GPIO.output(output_pin1, 1)
        
#if (sys.version_info > (3, 0)):    # python 3.x
import socketserver as socketserver
import http.server
from http.server import SimpleHTTPRequestHandler as RequestHandler
from urllib.parse import urlparse

#from urlparse import urlparse

class MyHandler(RequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        query = urlparse(self.path).query
        print(query)
        pin =b" "
        on =b" "
        if query!="":
           query_components = dict(qc.split("=") for qc in query.split("&"))
           pin = query_components["pin"]
           on = query_components["on"]
           print("pin",pin)  
           print("on",on)  
        self.do_HEAD()
        print(self.wfile)
        output = b""
        #output += b"<html><body>Hello name="+b(name) + b" password="+b(password) +b"</body></html>"
        output += b"<html><body>Hello pin="
		
        try:
            output +=pin
        except:
            output +=pin.encode('utf-8')
        output += b" on="
        try:
            output +=on
        except:
            output +=on.encode('utf-8')
        
        t=GPIO.input(input_pin1)
        output += b" input:"+str(t).encode('utf-8')
        output += b"</body></html>"
        inton=0
        intpin=output_pin2
        if (on=="1"):
            inton=1
        if (pin==output_pin1):
            intpin=output_pin1
        self.wfile.write(output)
        GPIO.output(intpin, inton)

if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8888

print('Server listening on port %s' % port)
socketserver.TCPServer.allow_reuse_address = True
#httpd = socketserver.TCPServer(('127.0.0.1', port), MyHandler)
httpd = socketserver.TCPServer(('0.0.0.0', port), MyHandler)
try:
    httpd.serve_forever()
except:
    print("Closing the server.")
    httpd.server_close()
    raise

