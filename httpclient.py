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

##Implementation provided by Daniel Asimiakwini

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

newline = "\r\n"
http = "HTTP/1.1"

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        resp_parts = data.split("\r\n\r\n")
        code = int(resp_parts[0].split()[1])
        return code

    def get_headers(self,data):
        resp_parts = data.split("\r\n\r\n")
        headers = resp_parts[0]
        return headers

    def get_body(self, data):
        resp_parts = data.split("\r\n\r\n")
        body = resp_parts[1]
        return body
    
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
        code = 500
        body = ""

        url_parts = urllib.parse.urlparse(url)

        scheme = url_parts.scheme
        host = url_parts.hostname
        port = url_parts.port
        if not port:
            port = 80
        path = url_parts.path
        if not path:
            path = "/"


        self.connect(host, port)

        first_line = "GET " + path + " HTTP/1.1\r\n"
        req_headers = "Host: "+host + newline + "Connection: Close\r\n"
        req_body = "\r\n"

        request = first_line + req_headers + req_body

        # print(request)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        # print("response was")
        print(response)

        code = self.get_code(response)
        body = self.get_body(response)
        
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        url_parts = urllib.parse.urlparse(url)
        # print(url_parts)

        scheme = url_parts.scheme
        host = url_parts.hostname
        port = url_parts.port
        if port==None:
            if scheme=="https":
                port = 443
            else:
                port = 80
        path = url_parts.path

        # print("HOST PORT")
        # print(host, port)
        self.connect(host, port)

        first_line = "POST " + path + " HTTP/1.1\r\n"

        #NEED ARGS for both request headers and body
        if args == None:
            req_body = ""
            req_body_length = "0\r\n"
        else:
            req_body = urllib.parse.urlencode(args)
            req_body_length = str(len(req_body))

        req_headers = "Host: "+host+newline + "Content-Type: application/x-www-form-urlencoded\r\n" + "Content-Length: "+req_body_length+newline + "Connection: close\r\n"

        request = first_line + req_headers + newline + req_body

        # print(request)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        # print("response was")
        print(response)

        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        elif (command == "GET"):
            return self.GET( url, args )
        else:
            return HTTPResponse(404, "404 NOT FOUND")
    
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






#####REFERENCES##########
'''
https://www.tutorialspoint.com/http/http_requests.htm
https://stackoverflow.com/questions/9626535/get-protocol-host-name-from-url
https://reqbin.com/req/zvtstmpb/post-request-example
https://ioflood.com/blog/python-url-encode/#:~:text=To%20encode%20a%20URL%20in,for%20transport%20over%20the%20internet.
https://docs.python.org/3/library/urllib.parse.html
https://www.geeksforgeeks.org/what-does-s-mean-in-a-python-format-string/
https://www.w3schools.com/python/ref_string_replace.asp
https://dev.to/sidthesloth92/understanding-html-form-encoding-url-encoded-and-multipart-forms-3lpa
https://www.geeksforgeeks.org/python-program-to-remove-last-character-from-the-string/
'''
