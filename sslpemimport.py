# this script gathers up all the certificates in the roots directory and concatinates them into the CA_STORE_FILENAME file
# this is used by httpfak.py for ssl connection validation
import os

CA_STORE_FILENAME = "ca_store.pem"
ERROR_CODE = -1

ca_store = None

if os.path.isfile(CA_STORE_FILENAME):
    ca_store = open(CA_STORE_FILENAME, "r+")
else:
    ca_store = open(CA_STORE_FILENAME, "w")
    ca_store.close()
    ca_store = open(CA_STORE_FILENAME, "r+")

    
if ca_store == None:
    exit(ERROR_CODE,"ca_store.pem is freaking out, exiting...") 

ca_store_contents = ca_store.read()

all_certs = ca_store.read()

for root, dirs, files in os.walk('roots'):
    #print "root********"
    #print root
    #print "dirs********"
    #print dirs
    #print "files*******"
    #print files
    
    
    for filename in files:
        if filename[-4:] == ".pem":
            pem_path = root + "/" + filename
            print pem_path
            f = open(pem_path, 'r')
            pemfile = f.read()
            
            if ca_store_contents.find(pemfile) == -1:
                print "Adding %s to %s" % (pem_path, CA_STORE_FILENAME)
                ca_store.write(pemfile+"\n")
            else:
                print "Certificate %s already exists in %s" % (pem_path, CA_STORE_FILENAME)
            
            f.close()
            
ca_store.close()
