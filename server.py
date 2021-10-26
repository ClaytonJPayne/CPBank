# CPBANK Server Program

import socket
import pandas as pd
from cpbank import cd
from cpbank import msg
from cpbank import raw
from cpbank import nameUni
import os
    
###############################################################################    

# Function definitions
    
def handleRequest(requestRaw):
    """Decode request and return receipt"""
    global clntSock
    request = raw(requestRaw).decode()
    
    if request.code == cd.opn:
        numSent = clntSock.send(msg(cd.pas,0,0,0).encode())
        nameRaw = clntSock.recv(32)
        print("Name:    ", nameRaw)
        fname, lname = nameUni(nameRaw).decode()
        return request.openAccount(fname, lname)
    elif request.code == cd.lgn:
        return request.login()
    elif request.code == cd.dep or request.code == cd.wth or request.code == cd.bal:
        return request.transaction()
    else:
        return msg(cd.bad, 0, 0, 0)
    
###############################################################################

# Import customer dataframe

if os.path.exists("customers.csv"):
    cust = pd.read_csv("customers.csv", index_col="acct")
else:
    custdict = {"acct":[10000],
                "fname":["Sterling"], "lname":["Archer"],
                "pin":[3232], "balance":[4500000]}
    cust = pd.DataFrame(custdict).set_index("acct")
    pd.to_csv("customers.csv")

# Create/bind socket

servSock = socket.socket(family=socket.AF_INET,
                         type=socket.SOCK_STREAM,
                         proto=0)

retval = servSock.bind(("", 26143))

# Main program loop
try:
    while True: # Listen
        print("\nListening for client")
        retval = servSock.listen(5)
        clntSock, clntAddr = servSock.accept()
        #hostName, aliases, IPs = socket.gethostbyaddr(clntAddr[0])
    
        print("Handling client: ", str(clntAddr))
        #print("Host name: ",hostName,", Aliases: ",aliases,", IPs: ",IPs)
    
        while True: # Handle client
            request = clntSock.recv(32)
            if len(request) == 0:
                clntSock.close()
                print("Client connection closed")
                break
            print("Request: ", request)
            receipt = handleRequest(request)
            print("Receipt: ", receipt.encode())
            sentBytes = clntSock.send(receipt.encode())
            if sentBytes <= 0:
                print("\nsend() failed")
except KeyboardInterrupt:
    print("Exiting, closing listening socket")
    servSock.close()
