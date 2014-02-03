#!/usr/bin/env python
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    def __str__(self):
        return "Code:"+str(self.code)+"\nbody:\n"+self.body+"\nEND"
class HTTPClient(object):
    def get_host_info(self,url):
        from urlparse import urlparse
        o = urlparse(url)
        #to get the port number
        t = o.netloc.split(":")
        port = 80
        home = "/"
        if len(t)==2:
            port = int(t[1])
        home = t[0]
        return port,home,o.path,o.query
    def connect(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #default port 80
        if port is None:
            port = "80"
        #to get ip address
        ip_address = socket.gethostbyname(host)
        self.s.connect((ip_address,port))
        return None
#to retrive the return code
    def get_code(self, data):
        tmp = data.split()
        #print tmp
        if len(tmp)>=3:
            return int(tmp[1])
        else:
            raise NameError('Unknown header')
#to retrive the header
    def get_headers(self,data):
        if data is None:
            return None;
        tmp = data.split("\r\n")
        return tmp[0]
    def get_body(self, data):
        if data is None:
            return None;
        n = data.find("\r\n\r\n")
        #to get rid of "\r\n\rn"
        return data[n+4:]

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
        return str(buffer)
    #to do HTTP GET by given URL
    def GET(self, url, args=None):
        #print "Url:"+url
        port,host_name,path,query = self.get_host_info(url)
        #print "GETTTTTT:"+host_name+" "+str(port)
        self.connect(host_name,port)
        send = ""
        if query !='':
            query='?'+urllib.quote(query)
        if host_name !='':
            send ="GET %s%s HTTP/1.1\r\nHost:%s:%d\r\nAccept: */*\r\nConnection:close\r\n\r\n"%(path,query,host_name,port)
            self.s.sendall(send.encode("ascii"))
        else:
            send ="GET %s%s HTTP/1.1\r\nAccept: */*\r\nConnection:close\r\n\r\n"%(path,query)
            self.s.sendall(send.encode("ascii"))
        print "send:"+send
        code = 500
        body = ""
        data = self.recvall(self.s)
        code = self.get_code(data)
        body = self.get_body(data)
        #print "Data:"+data
        return HTTPRequest(code,body )
    #to do HTTP post by given URL
    def POST(self, url, args=None):
        port,host_name,path,query = self.get_host_info(url)
        #print host_name+" "+str(port)+" Path:"+path
        length = 0
        param = ""
        if args is not None:
            param = urllib.urlencode(args)
            length = len(param)
        self.connect(host_name,port)
        if port is None:
            port =""
        else:
            port = str(port)
        self.s.sendall("POST %s HTTP/1.1\r\n"%(path))
        #print"POST %s HTTP/1.1\r\n"%(path)
        self.s.sendall("Host: %s:%s\r\n"%(host_name,port))
        self.s.sendall("Content-Type: application/x-www-form-urlencoded; charset=UTF-8\r\n")
        if length != 0:
            self.s.sendall("Content-Length:%d\r\n"%(length))
        self.s.sendall("\r\n")
        if param !="":
            self.s.sendall(param)
        code = 500
        body = ""
        data = self.recvall(self.s);
#print "Data:"+data
        code = self.get_code(data);
        body = self.get_body(data)
        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (url[:7] != "http://"):
            url = "http://" + url
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
        #print sys.argv[1]+" "+sys.argv[2]
        print client.command(sys.argv[2],sys.argv[1] )