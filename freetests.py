#!/usr/bin/env python3
# coding: utf-8
# Copyright 2013 Abram Hindle
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
#
# run python freetests.py

import unittest
import httpclient
import http.server
import threading
import socketserver
import random
import time
import urllib.parse
import json

BASEHOST = '127.0.0.1'
BASEPORT = 27600 + random.randint(1,100)


httpclass = httpclient
#import mysolution
#httpclass = mysolution

# Sorry but in Python this comes out of the box!
class MyHTTPHandler(http.server.BaseHTTPRequestHandler):
    post = None 
    get = None
    def do_POST(self):
        try:
            if (self.post == None):
                return None
            else:
                return self.post()
        except Exception as e:
            print("Exception %s\n" % e)
            raise e

    def do_GET(self):
        try:
            print("GET %s\n" % self.path)
            if (self.get == None):
                return None
            else:
                return self.get()
        except Exception as e:
            print("Exception %s\n" % e)
            raise e

def make_http_server(host = BASEHOST, port = BASEPORT):
    return http.server.HTTPServer( (host, port) , MyHTTPHandler)

# always returns 404
def nothing_available(self):
    self.send_error(404, "File not found")
    self.end_headers()
    self.wfile.write(bytes("","utf-8"))

# repeats your path back
def echo_path_get(self):
    self.send_response(200)
    self.send_header("Content-type", "text/plain")
    self.end_headers()
    self.wfile.write(bytes("%s\n" % self.path,"utf-8"))

# repeats your post back as json
def echo_post(self):
    length = int(self.headers['Content-Length'])
    post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    self.wfile.write(bytes(json.dumps(post_data),"utf-8"))

def header_check(self):
    response = 200
    errors = []
    if 'Host' not in self.headers:
        response = 400
        errors.append("No Host header found")
    self.send_response(response)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    self.wfile.write(bytes(json.dumps(errors),"utf-8"))

def die_on_method(self):
    response = 405
    errors = []
    errors.append("Method Not Allowed")
    if 'Host' not in self.headers:
        errors.append("No Host header found")
    self.send_response(response)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    self.wfile.write(bytes(json.dumps(errors),"utf-8"))

def post_header_check(self):
    response = 200
    errors = []
    if 'Host' not in self.headers:
        response = 400
        errors.append("No Host header found")
    if 'Content-length' not in self.headers:
        response = 400
        errors.append("No Content-Length header found")
    self.send_response(response)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    self.wfile.write(bytes(json.dumps(errors),"utf-8"))




class TestHTTPClient(unittest.TestCase):
    httpd = None
    running = False

    @classmethod
    def setUpClass(self):
        '''Cache the httpd server and run it as a thread'''
        if (TestHTTPClient.httpd == None):
            try:
                self.thread = threading.Thread(target=self.run_server).start()
                time.sleep(1)
            except Exception as e:
                print(e)
                print("setUP: Thread died")
                raise(e)

    @classmethod
    def run_server(self):
        '''run the httpd server in a thread'''
        try:    
            socketserver.TCPServer.allow_reuse_address = True
            http.server.HTTPServer.allow_reuse_address = True
            TestHTTPClient.httpd = make_http_server()
            print("HTTP UP!\n")
            TestHTTPClient.httpd.serve_forever()
            print("HTTP has been shutdown!\n")
        except Exception as e:
            print(e)
            print("run_server: Thread died")



    def test404GET(self):
        '''Test against 404 errors'''
        MyHTTPHandler.get = nothing_available
        http = httpclass.HTTPClient()
        req = http.GET("http://%s:%d/49872398432" % (BASEHOST,BASEPORT) )
        self.assertTrue(req != None, "None Returned!")
        self.assertTrue(req.code == 404)

    def test404POST(self):
        '''Test against 404 errors'''
        MyHTTPHandler.post = nothing_available
        http = httpclass.HTTPClient()
        req = http.POST("http://%s:%d/49872398432" % (BASEHOST,BASEPORT) )
        self.assertTrue(req != None, "None Returned!")
        self.assertTrue(req.code == 404)

    def testGET(self):
        '''Test HTTP GET'''
        MyHTTPHandler.get = echo_path_get
        http = httpclass.HTTPClient()
        path = "abcdef/gjkd/dsadas"
        url = "http://%s:%d/%s" % (BASEHOST,BASEPORT, path)
        req = http.GET( url )
        self.assertTrue(req != None, "None Returned!")
        self.assertTrue(req.code == 200)
        self.assertTrue(req.body.find(path)>=0, "Data: [%s] " % req.body)

    def testGETHeaders(self):
        '''Test HTTP GET Headers'''
        MyHTTPHandler.get = header_check
        MyHTTPHandler.post = die_on_method
        http = httpclass.HTTPClient()
        path = "abcdef/gjkd/dsadas"
        url = "http://%s:%d/%s" % (BASEHOST,BASEPORT, path)
        req = http.GET( url )
        self.assertTrue(req != None, "None Returned!")
        self.assertTrue(req.code == 200)

    def testPOSTHeaders(self):
        '''Test HTTP POST Headers'''
        MyHTTPHandler.post = post_header_check
        MyHTTPHandler.get  = die_on_method
        http = httpclass.HTTPClient()
        path = "abcdef/gjkd/dsadas"
        url = "http://%s:%d/%s" % (BASEHOST,BASEPORT, path)
        req = http.POST( url )
        self.assertTrue(req != None, "None Returned!")
        self.assertTrue(req.code == 200,"Code is %s but I wanted a 200 OK" % req.code)

        
        
    # consider disabling this test until everything else works
    def testInternetGets(self):
        '''Test HTTP Get in the wild, these webservers are far less
           forgiving'''
        MyHTTPHandler.get = echo_path_get
        http = httpclass.HTTPClient()        
        urls = [
            "http://www.cs.ualberta.ca/",
            "http://softwareprocess.es/static/SoftwareProcess.es.html",
            "http://c2.com/cgi/wiki?CommonLispHyperSpec",
            "http://slashdot.org"
            ]
        for url in urls:
            try:
                req = http.GET( url )
            except Exception as e:
                print("An Exception was thrown for %s" % url)
                self.assertTrue( False, "An Exception was thrown for %s %s" % (url,e))
            self.assertTrue(req != None, "None Returned! %s" % url)
            self.assertTrue(req.code == 200 or 
                            req.code == 301 or
                            req.code == 302,
                            "Code: %s for %s" % (req.code, url))
            if (req.code == 200):
                self.assertTrue(req.body.find("DOCTYPE")>=0 or 
                                req.body.find("<body")>=0 , 
                                "%s Data: [%s] " % (url,req.body))
    
    def testPOST(self):
        '''Test HTTP POST with an echo server'''
        MyHTTPHandler.post = echo_post
        http = httpclass.HTTPClient()
        path = "post_echoer"
        url = "http://%s:%d/%s" % (BASEHOST,BASEPORT, path)
        args = {'a':'aaaaaaaaaaaaa',
                'b':'bbbbbbbbbbbbbbbbbbbbbb',
                'c':'c',
                'd':'012345\r67890\n2321321\n\r'}
        print("Sending POST!")
        req = http.POST( url, args=args )
        self.assertTrue(req != None, "None Returned!")
        self.assertTrue(req.code == 200)
        print("Test Post Body: [%s]" % req.body)
        outargs = json.loads(req.body)
        print(outargs.__class__)
        for key in args:
            self.assertTrue(args[key] == outargs[key][0], "Key [%s] not found" % key)
        for key in outargs:
            self.assertTrue(args[key] == outargs[key][0], "Key [%s] not found" % key)

    @classmethod
    def tearDownClass(self):        
        if (TestHTTPClient.httpd!=None):
            print("HTTP Shutdown in tearDown\n")
            TestHTTPClient.httpd.shutdown()
            TestHTTPClient.httpd.server_close()
            time.sleep(1)

def test_test_webserver():
    print("http://%s:%d/dsadsadsadsa\n" % (BASEHOST,BASEPORT) )
    MyHTTPHandler.get = echo_path_get
    MyHTTPHandler.post = echo_post
    httpd = make_http_server()
    try:
        httpd.serve_forever()
    finally:
        httpd.shutdown()

if __name__ == '__main__':
    unittest.main()
