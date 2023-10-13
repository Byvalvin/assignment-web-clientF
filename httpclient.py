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

from calendar import c
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

import os

#defined globals
encoding = 'utf-8'
newline = "\n"

root = "./" #the current dir, with just want ot access our custom htmls
http = "HTTP/1.1 "

status_codes = {200:"200 OK", 301:"301 Moved Permanently", 403:"403 Forbidden", 404:"404 Not Found", 405:"405 Method Not Allowed"}

headers_list=["Content-Type: ", "Content-Size: ", "Location: ", "Connection: "]
headers_default=["text/plain", "0", "", "close"]

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
        return None

    def get_headers(self, ext):
        # return None
        #0
        
        cont_type_header = headers_list[0]
        file_type = "text/html" #tell the user whats up with our own html
        headers = (cont_type_header + file_type + newline)

        #1
        cont_size_header = headers_list[1]
        content_bytesize = os.path.getsize(root+ext) #PROBLEMS FOR 405 LINE
        headers += (cont_size_header + str(content_bytesize) + newline)
        
        #3
        connection_header = headers_list[3]
        headers += (connection_header + headers_default[3] + newline)

        return headers

    def get_body(self, ext):
        # return None
        body = ""
        file = open(root+ext, 'r')
        filelines = file.readlines()
        for line in filelines:
            body += line
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

        print("says him")
        print(parse_url(url))
        #need the host and path from the url to make request
        scheme, host, port, path = self.parseUrl(url)

        if scheme not in {"http","https"}:
            return self.Not_Found()
        
        if host==None:
            host=path
            path='/'
        
        print(scheme)
        print(host)
        print(port)
        print(path)

        host = socket.gethostbyname(host)
        #First build the request. Just the first lien and host
        first_line = "GET " + path + " HTTP/1.1"
        header_line = "Host: " + host
        header_line += newline + "Accept: */*"
        header_line += newline + "Connection: close"
        request_body = ""

   
        request = first_line + newline + header_line + newline + request_body + newline
        #show request 
        print(request)
        

        #sent request to sserver, we act as a proxy client and want a reponse as end result
        response = b""

        #CONNECT TO WEB SERVER
        if port==None:
            if scheme == "http":
                port = 80
            elif scheme == "https":
                port = 443
        print(host,port)
        self.connect(host, port)

        #assuming connected.. SEND REQUEST TO WEBSERVER
        self.sendall(request)
        # self.endheaders() 
        

        #TELL WEB SERVER THIS SERVER CLIENT IS DONE WRITING DATA
        done = socket.SHUT_WR
        self.socket.shutdown(done)

        #RECIEVED REPOSNSE FROM WEB SERVER AND SEND TO PROXY CLIENT
        #RECEIVE RESPONSE FROM WEB SERVER
        response = self.recvall(self.socket)
        
        #We have a response, we determine the status code and response body and sent them back as int and string respectively
        self.close()
        #show response
        print("RESPONSE WAS WAS")
        print(response)
        

        
        # set the values need for a HTTPResponse
        code = int(response.split()[1])
        

        client_error = False
        if client_error:
            return self.Not_Found()
        else:
            response_parts = response.encode().split(b"\r\n\r\n")
            # print("THE PARTS:",response_parts)
            if len(response_parts) > 1:
                body = response_parts[1].decode(encoding)
            else:
                body = b"" #No Body haha wasnt funny first time either

            return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        

        #need the host and path from the url to make request
        scheme, host, port, path = self.parseUrl(url)

        if scheme not in {"http","https"}:
            return self.Not_Found()
        
        if host==None:
            host=path
            path='/'

        print(host)
        print(path)
        host = socket.gethostbyname(host)

        #First build the request. Just the first lien and host
        first_line = "POST " + path + " HTTP/1.1"
        header_line = "Host: " + host
        header_line += newline + "Accept: */*"

        if args != None: #convert to long ass name
            header_line += newline + "Content-Type: application/x-www-form-urlencoded"
            print("hey args")
            urlencoding = urllib.parse.urlencode(args)
            print(urlencoding,"as is")
            urlencoding = urlencoding[:-3] + "\r" #remove last ampersand
            header_line += newline + "Content-length: " + str(len(urlencoding))
            request_body = urlencoding
            # print("-------------------")
            # print(args)
            # print(urlencoding)
        else:
            header_line += newline + "Content-length: 0"
            request_body = ""
        
        header_line += newline + "Connection: close"


# Content-Length: 23
      
# key1=value1&key2=value2
        ##add content type and body

        
   
        request = first_line + newline + header_line + newline + newline + request_body + newline
        #show request 
        print(request)


        #sent request to sserver, we act as a proxy client and want a reponse as end result
        response = b""
        #CREATE REQUEST TO WEB SERVER

        #CONNECT TO WEB SERVER
        if port==None:
            port = 80
        self.connect(host, port)

        #assuming connected.. SEND REQUEST TO WEBSERVER
        self.sendall(request)
        

        #TELL WEB SERVER THIS SERVER CLIENT IS DONE WRITING DATA
        done = socket.SHUT_WR
        self.socket.shutdown(done)

        #RECIEVED REPOSNSE FROM WEB SERVER AND SEND TO PROXY CLIENT
        #RECEIVE RESPONSE FROM WEB SERVER
        response = self.recvall(self.socket)


        
        #We have a response, we determine the status code and response body and sent them back as int and string respectively
        self.close()
        #show response
        print("RESPONSE WAS")
        print(response)

        # set the values need for a HTTPResponse
        code = int(response.split()[1])

        client_error = code>=400
        if client_error:
            return self.Not_Found()
        else:
            print("here")
            response_parts = (response.encode()).split(b"\r\n\r\n")
            # print("THE PARTS:",response_parts)
            if len(response_parts) > 1:
                body = response_parts[1].decode(encoding)
                # print("the bosy is ",body)
            else:
                body = b"" #No Body haha wasnt funny first time either
            return HTTPResponse(code, body)
        
    
    def Method_Not_Allowed(self): #method to give our own 405 Response
        code = 405
        #make a personal 405
        # print("NOT GETTING")
        
        resp_firstline =  http  + status_codes[code]

        file_ext = "400html files/405.html" #to show them why
        resp_headers = self.get_headers(file_ext)
        resp_body = self.get_body(file_ext)

        response = resp_firstline + newline + resp_headers + newline + resp_body + newline
        print(response)

        body = resp_body
        return HTTPResponse(code, body)
    
    def Not_Found(self): #method to give our own 404 Response
        code = 404
        #make a personal 404
        # print("NOT GETTING")
        
        resp_firstline =  http  + status_codes[code]

        file_ext = "400html files/404.html" # to show them why
        resp_headers = self.get_headers(file_ext)
        resp_body = self.get_body(file_ext)

        response = resp_firstline + newline + resp_headers + newline + resp_body + newline
        print(response)
    
        body = resp_body
        return HTTPResponse(code, body)
    
    def parseUrl(self, URL): #method to get the hostname and path
        parsed = urllib.parse.urlparse(URL)

        print(parsed)
        scheme = parsed.scheme
        hostname = parsed.hostname
        port = parsed.port
        path = parsed.path

        return scheme, hostname, port, path
    
    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        elif (command == "GET"):
            return self.GET( url, args )
        else:
            return self.Method_Not_Allowed()
        

def parse_url(url):
    # Split the URL into host and path
    parts = url.split('/', 3)
    host = parts[2]
    path = '/' + parts[3] if len(parts) > 3 else '/'
    return host, path
            
    
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




######REFERENCES##########
'''
https://docs.python.org/3/library/urllib.parse.html
'''

