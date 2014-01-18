class HeaderStore:
    def __init__(self):
        
        self.HEADER_STORE = {}
        
        """FORMAT FOR STORAGE AND ACCESS
        {"windows" :
            {"7" :
                { "firefox" :
                    { "7" :
                        [
                            ["Host","hostname_placeholder"],
                            ["User-Agent","Mozilla/5.0 (Windows NT 6.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1"],
                            ["Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"],
                            ["Accept-Language", "en-us,en;q=0.5"],
                            ["Accept-Encoding", "gzip, deflate"],
                            ["Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7"],
                            ["Connection", "keep-alive"]
                        ]
                    }
                }
            }
        }"""
    
    def import_headers_from_file(self, filename="headers.store"):
        hfile = open(filename, "r")
        headersfile = hfile.read()
        hfile.close()
        
        split_headers = headersfile.split("\n\n")
        #print split_headers
        clean_split_headers = []
        for dirty_header in split_headers:
            if dirty_header != "":
                clean_split_headers += [dirty_header]
        
        processed_headers = {}
        
        for h in clean_split_headers:
            
            clean_hlines = []
            hlines = h.split("\n")
            for dirty_hline in hlines:
                if dirty_hline != "":
                    clean_hlines += [dirty_hline]
            
            ident = clean_hlines[0].split(":")
            if len(ident) != 4:
                print "improper format in header set identifier: " + clean_hlines[0] + " skipping..."
                continue
            else:
                #First we check if the OS is in the header store yet
                if self.HEADER_STORE.has_key(ident[0]) is not True:
                    #if it's not, then we create the dict chain to store the headers
                    #and then the same for the rest of them
                    self.HEADER_STORE[ident[0]] = {}
                    self.HEADER_STORE[ident[0]][ident[1]] = {}
                    self.HEADER_STORE[ident[0]][ident[1]][ident[2]] = {}
                    self.HEADER_STORE[ident[0]][ident[1]][ident[2]][ident[3]] = {}
                else:                                   
                    #then the OS version
                    if self.HEADER_STORE[ident[0]].has_key(ident[1]) is not True:
                        self.HEADER_STORE[ident[0]][ident[1]] = {}
                        self.HEADER_STORE[ident[0]][ident[1]][ident[2]] = {}
                        self.HEADER_STORE[ident[0]][ident[1]][ident[2]][ident[3]] = {}
                    else:                                           
                        #then the browser name
                        if self.HEADER_STORE[ident[0]][ident[1]].has_key(ident[2]) is not True:
                            self.HEADER_STORE[ident[0]][ident[1]][ident[2]] = {}
                            self.HEADER_STORE[ident[0]][ident[1]][ident[2]][ident[3]] = {}
                        else:                                                   
                            #then the browser version
                            if self.HEADER_STORE[ident[0]][ident[1]][ident[2]].has_key(ident[3]) is not True:
                                self.HEADER_STORE[ident[0]][ident[1]][ident[2]][ident[3]] = {}
                            
                self.HEADER_STORE[ident[0]][ident[1]][ident[2]][ident[3]] = clean_hlines[1:]
            
        
        #print headersfile
        
    
    def get_headers_for(self, os_name, browser_name, hostname, referrer = None, cookie = None):
        
        dem_headers = None
        
        if os_name[0] in self.HEADER_STORE:
            
            os_store = self.HEADER_STORE[os_name[0]]
            
            if os_name[1] in os_store:
                browsers_store = os_store[os_name[1]]
                
                if browser_name[0] in browsers_store:
                    versions_store = browsers_store[browser_name[0]]
                    
                    if browser_name[1] in versions_store:
                        dem_headers = versions_store[browser_name[1]][:]
                        
                        for i in range(len(dem_headers)):
                            if "hostname_placeholder" in dem_headers[i]:
                                dem_headers[i] = dem_headers[i].replace("hostname_placeholder", hostname)
                            if "referrer_placeholder" in dem_headers[i]:
                                if referrer != None:
                                    dem_headers[i] = dem_headers[i].replace("referrer_placeholder", referrer)
                                else:
                                    dem_headers[i] = ""
                            if "cookie_placeholder" in dem_headers[i]:
                                if cookie != None:
                                    dem_headers[i] = dem_headers[i].replace("cookie_placeholder", cookie)
                                else:
                                    dem_headers[i] = ""
        while "" in dem_headers:
            dem_headers.remove("")
        return dem_headers
        
        
        
if __name__ == '__main__':
    
    header_store = HeaderStore()
    header_store.import_headers_from_file()
    dem_headers = header_store.get_headers_for( ("windows","7"), ("firefox", "7"), "www.google.com", "http://www.google.com" )
    print dem_headers
    
    
    
        
