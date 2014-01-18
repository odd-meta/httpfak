import sys
import time
import zlib
import binascii
import socket, ssl, pprint
#import argparse
import optparse
import time

import headerimport

class CookiePile():

    def __init__(self, cookies):
        self.time_format = "%a, %d-%b-%Y %H:%M:%S %Z"
        self.cookies = []
        self.cookies += cookies

    def add_cookie(cookie):
        self.cookies.append(cookie)

    def get_cookies_for(self, domain, give_all = False, give_only_expired = False):
        gotten_cookies = []
        for cookie in self.cookies:
            if cookie.cookie_items.has_key("domain"):
                if cookie.cookie_items['domain'] in domain:
                    
                    if cookie.cookie_items.has_key("expires"):
                        cookie_expiry = time.strptime(cookie.cookie_items['expires'],self.time_format)
                    
                    
                    
                    gotten_cookies.append(cookie)


class Cookie():

    def __init__(self, raw_data):
        self.cookie_items = {}
        self.cookie_data = ""
        
        if raw_data.index("Set-Cookie: ") == 0:
            parsing_cookie = raw_data[12:]

            parsing_cookie = parsing_cookie.split("; ")

            self.cookie_data = parsing_cookie.pop(0)

            for item in parsing_cookie:
                broken_item = item.split("=",1)
                if len(broken_item) > 1:
                    self.cookie_items[broken_item[0]] = broken_item[1]
                else:
                    self.cookie_items[broken_item[0]] = broken_item[0]
                
                                    
            #print parsing_cookie

    def print_status(self):
        print "Cookie Data: " + self.cookie_data
        print self.cookie_items
    


class HttpFawk():

    def __init__(self, url, port, verb, header_ident, referrer=None, cookie=None):
        self.url = url
        self.port = port
        self.verb = verb
        self.header_ident = header_ident
        self.referrer = referrer
        self.cookie = cookie
        
        


        #url = "http://airborne.gogoinflight.com"



        self.header_ident = self.header_ident.split(":")

        self.header_os = self.header_ident[0]
        self.header_os_version = self.header_ident[1]
        self.header_browser = self.header_ident[2]
        self.header_browser_version = self.header_ident[3]

        self.split_url = self.url.split("://")
        self.hostname = self.split_url[1]


        self.hostname = self.hostname.partition("/")

        
        self.path = self.hostname[1]+self.hostname[2]

        if self.hostname[2] == "":
                        self.path = "/"



        self.hostname = self.hostname[0]

        #print self.path
        #print self.hostname


        self.protocol = self.split_url[0]

        
        self.header_store = headerimport.HeaderStore()
        #dem_headers = header_store.get_headers_for( ("windows","7"), ("firefox", "7"), "www.google.com" )
        #print dem_headers
        self.header_store.import_headers_from_file()
        self.dem_headers = self.header_store.get_headers_for(
            (self.header_os,self.header_os_version),
            (self.header_browser, self.header_browser_version),
            self.hostname,
            self.referrer,
            self.cookie
        )

        #print dem_headers
        #print split_url

        self.header_string = ""
        for header in self.dem_headers:
                        self.header_string += header + "\r\n"

        self.header_string += "\r\n"

        
        

    def get_data(self):        
        self.prot_map = {"http": self.http_connection, "https": self.https_connection}

        # Send data
        message = self.verb + ' ' + self.path + ' HTTP/1.1\r\n'+self.header_string
        #print 'sending "%s"' % message

        page_data = None
        data_received = None
        try:
                data_received = self.prot_map[self.protocol](message)
        except Exception as inst:
                print inst
        finally:
            
            processed_data = data_received.split("\r\n\r\n")
            rec_headers = processed_data[0]
            page_data = processed_data[1]

            print "HEADERS**********************"
            #print rec_headers
            rec_headers_parsed = rec_headers.split("\r\n")
            #print rec_headers_parsed


            for rec_head in rec_headers_parsed:
                if "Set-Cookie: " in rec_head:
                    cookie = Cookie(rec_head)
                    cookie.print_status()

            
            print "PAGEDATA*********************"
            hexd_page_data = binascii.hexlify(page_data)
            
            #print hexd_page_data.find("1f8b0800000000000")
            if hexd_page_data.find("1f8b0800000000000") == 0:
                            d = zlib.decompressobj(16+zlib.MAX_WBITS)
                            page_data = d.decompress(page_data)
            
            
            
            
            #print page_data
        return page_data
                    
            



        

    def http_connection(self, message):
        data_received = ""
        if self.port == None:
                        self.port = 80
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.settimeout(2)

        # Connect the socket to the port where the server is listening
        server_address = (self.hostname, self.port)
        print 'connecting to %s port %s' % server_address
        sock.connect(server_address)

        

        sock.sendall(message)

        # Look for the response


        get_dem_datas = True

        while get_dem_datas:
                
                        
            try:
                data = sock.recv(4096)
            except:
                print "closing socket"
                sock.close()
                get_dem_datas = False
            if len(data) != 0:
                print "got some data"
                data_received += data
            else:
                get_dem_datas = False

        return data_received

    

    def https_connection(self, message):
        data_received = ""
        print "attempting to establish https connection"
        if self.port == None:
                        self.port = 443
        
        CA_STORE_FILENAME = "ca_store.pem"

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        # require a certificate from the server
        ssl_sock = ssl.wrap_socket(s,ca_certs=CA_STORE_FILENAME, cert_reqs=ssl.CERT_OPTIONAL)#, cert_reqs=ssl.CERT_REQUIRED)
        print("Attempting to connect...")
        server_address = (self.hostname, self.port)
        ssl_sock.connect(server_address)
        print("Connected!")
        
        print repr(ssl_sock.getpeername())
        print ssl_sock.cipher()
        dat_cert = ssl_sock.getpeercert(binary_form = True)
        #help(ssl_sock)

        #print pprint.pformat(ssl_sock.getpeercert())
        #dat_cert = ssl.DER_cert_to_PEM_cert(dat_cert)
        # printing out the raw certificate breaks sublimerepl and freaks out the terminal
        #print(dat_cert)
        #exit()
        # Set a simple HTTP request -- use httplib in actual code. -- FUCK YOU NO
        
        ssl_sock.write(message)
        
        get_dem_datas = True

        while get_dem_datas:
            try:
                data = ssl_sock.recv(4096)
            except:
                print "closing socket"
                ssl_sock.close()
                get_dem_datas = False
            if len(data) != 0:
                print "got some data"
                data_received += data
            else:
                get_dem_datas = False
                

        return data_received     

        

    def print_stats(self):
            print "Current Connection:"
            print "url: " + self.url
            print "protocol: "+self.protocol
            print "port: " + str(self.port)
            print "hostname: " + self.hostname
            print "path: " + self.path
            print "HEADERS USED:"
            print self.header_string
    
    
    
if __name__ == '__main__':
    url = "https://www.yahoo.com"

    port = None

    

    verb = "GET"

    header_ident = "windows:7:firefox:7"

    referrer = "http://www.yahoo.com/"
    
    fawk = HttpFawk(url, port, verb, header_ident, referrer)

    fawk.print_stats()

    fawk.get_data()




