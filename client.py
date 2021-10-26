import socket
import pandas as pd
from cpbank import cd
from cpbank import msg
from cpbank import raw
from cpbank import nameTok

#################################################################

# servAddr = ('69.254.137.197', 26143)
servAddr = ('127.0.0.1', 26143)

# Function definitions

def openAccount():
    """Open a new account"""

    global servAddr

    # Get user input
    fname = input("\nEnter first name: ")
    lname  = input("Enter last name: ")
    name = nameTok(fname, lname).encode()
    while True:
        pin1 = int(input("\nPlease create a 4-9 digit PIN #: "))
        if ((pin1 < 1000) or (pin1 > 999999999)):
            print("Invalid PIN length, please try again")
            continue
        pin2 = int(input("Verify PIN #: "))
        if pin1 == pin2:
            break
        else:
            print("Pins do not match, please try again")
    amt = getAmount("starting balance")

    # One connection per account creation
    request = msg(cd.opn, 0, amt, pin1)
    sock = socket.socket(family=socket.AF_INET,
                         type=socket.SOCK_STREAM,
                         proto=0)
    retval = sock.connect(servAddr)
    
    # Convert user input to request message and send
    numSent = sock.send(request.encode())
    _ = sock.recv(32)
    numSent = sock.send(name)

    # Recv receipt
    receiptRaw = sock.recv(32)
    receipt = raw(receiptRaw).decode()
    sock.close()
    print("\nWelcome to CPBANK, ", fname)
    return receipt

def login():
    """Login to existing account"""
    acct = int(input("\nEnter acct #: "))
    pin = int(input("Enter PIN #: "))
    return msg(cd.lgn, acct, 0, pin)

def getAmount(kind):
    """Get amount for deposit or withdrawal"""
    while True:
        amt = float(input(f"Enter {kind} amount: "))
        if amt <= 0:
            print("Please enter amount greater than 0\n")
            continue
        amt *= 100
        if amt.is_integer() == False:
            print("Please enter at most two decimals\n")
            continue
        else:
            break
    return int(amt)

def printReceipt(receipt):
    """Display receipt"""
    
    print("\nReceipt:\nAcct #: ", receipt.acct)
    if receipt.code == cd.dep:
        print("Deposit amount: ", receipt.amt/100)
    elif receipt.code == cd.wth:
        if receipt.amt == 0:
            print("Insufficient funds")
        else:
            print("Withdrawal amount: ", receipt.amt/100)
    print("Current balance: ", receipt.last/100)

#################################################################

# MAIN PROGRAM LOOP

print("Welcome to CPBANK\n")

# Outer loop (login security, open account)

while True: 
    print("\nWhat would you like to do today?\n\n \
            \"1\"\t-> Open a new account\n \
            \"2\"\t-> Transaction for existing account\n \
            \"close\"\t-> Close program\n")
    option = input("Enter selection: ")
    if option == "1":
        receipt = openAccount()
        printReceipt(receipt)
        continue
    elif option == "2":
        request = login()
        acct = request.acct # Save user state (acct #)
    elif option == "close":
        exit()
    else:
        print("Invalid selection, please try again\n")
        continue

    # One connection per login attempt
    sock = socket.socket(family=socket.AF_INET,
                         type=socket.SOCK_STREAM,
                         proto=0)
    retval = sock.connect(servAddr)
    numSent = sock.send(request.encode())
    
    if numSent <= 0:
        printf("send() failed, please try again\n")
        continue

    # Receive initial request
    receiptRaw = sock.recv(16)

    # Decode raw object using .decode() method
    receipt = raw(receiptRaw).decode()
    if receipt.code == cd.rej:
        print("Invalid credentials\n")
        sock.close()
        continue
    elif receipt.code != cd.pas:
        print("Invalid request\n")
        sock.close()
        continue
    
    # Inner loop (balance, withdrawals, deposits)
    
    while True: 
        print ("\nWhat transaction would you like to perform?\n\n \
            \"1\"\t-> Check current balance\n \
            \"2\"\t-> Make a deposit\n \
            \"3\"\t-> Make a withdrawal\n \
            \"logout\"\t-> Logout\n")
        option = input("Enter selection: ")

        # For each request type you'll build a msg object
        if option == "1":
            request = msg(cd.bal, acct, 0, 0)
        elif option == "2":
            amt = getAmount("deposit")
            request = msg(cd.dep, acct, amt, 0)
        elif option == "3":
            amt = getAmount("withdrawal")
            request = msg(cd.wth, acct, amt, 0)
        elif option == "logout":
            sock.close()
            break
        else:
            print("Invalid selection\n")
            continue

        # Encode and send request
        numSent = sock.send(request.encode())
        if numSent <= 0:
            print("send() failed\n")
            continue

        # Recv and handle receipt
        receipt = sock.recv(32)
        printReceipt(raw(receipt).decode())
