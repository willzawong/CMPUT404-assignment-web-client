#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

# Acknowledgements:
# https://docs.python.org/3/library/urllib.parse.html
# https://uofa-cmput404.github.io/cmput404-slides/04-HTTP.html#/
# https://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html
# https://www.rfc-editor.org/rfc/rfc9110.html#name-header-fields
# https://docs.python.org/3/library/urllib.parse.html
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST
# https://docs.python.org/3/library/urllib.parse.html
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        if(port==None):
            port=80
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        lines = data.split("\n")
        first = lines[0].split(" ")
        return  int(first[1])

    def get_headers(self,data):
        lines = data.split("\n")

        # find amount of headers
        lines = data.split("\n")
        i = 1
        for line in lines[1:]:
            if(line==''):
                break
            i=i+1
            
        return "\n".join(lines[1:i])

    def get_body(self, data):
        lines = data.split("\r\n")
        i = 1
        for line in lines[1:]:
            if(line==''):
                break
            i=i+1
            
        return "\n".join(lines[i+1:])
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        parsed = urllib.parse.urlparse(url)
        #new_url = parsed.scheme+'://'+parsed.hostname+parsed.path+parsed.query+parsed.fragment
        #print("Connecting to %s port %s\n" % (new_url,parsed.port))
        self.connect(parsed.hostname, parsed.port)

        # from lab2 client.py
        parsedpath=parsed.path
        if parsedpath=='':
            parsedpath='/'
        payload = f'GET {parsedpath} HTTP/1.1\r\nHost: {parsed.hostname}\r\nConnection:close\r\n\r\n'
        self.sendall(payload)
        data = self.recvall(self.socket)
        self.close()

        returner_code = self.get_code(data)
        returner_body = self.get_body(data)
        #print("code = %s" % (returner_code))
        return HTTPResponse(returner_code, returner_body)

    def POST(self, url, args=None):
        # 
        parsed = urllib.parse.urlparse(url)
        #new_url = parsed.scheme+'://'+parsed.hostname+parsed.path+parsed.query+parsed.fragment
        #print("Connecting to %s port %s\n" % (new_url,parsed.port))
        self.connect(parsed.hostname, parsed.port)

        # from lab2 client.py
        parsedpath=parsed.path
        if parsedpath=='':
            parsedpath='/'
        payload = f'POST {parsedpath} HTTP/1.1\r\nHost: {parsed.hostname}\r\n'
        payload+="Content-Type: application/x-www-form-urlencoded\r\n" 
        content_length_size = 0
        content_length = ""
        if args:
            for arg in args:
                content_length+= f"{arg}={args[arg]}&"
            content_length=content_length[:-1]
            content_length_size=len(content_length.encode('utf-8'))
            payload +="Content-Length: " + str(content_length_size) + "\r\n\r\n"
            payload +=content_length
        else:
            payload+="Content-Length: 0\r\n"
        payload+="\r\n\r\n"
        #print(payload)
        self.sendall(payload)
        data = self.recvall(self.socket)
        self.close()

        returner_code = self.get_code(data)
        returner_body = self.get_body(data)
        #print("code = %s" % (returner_code))
        return HTTPResponse(returner_code, returner_body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
