import socket
import pandas as pd

class cd:
    opn = "OPN" # new acct msg
    lgn = "LGN" # login request
    dep = "DEP" # deposit msg
    wth = "WTH" # withdrawal msg
    bal = "BAL" # balance msg
    rej = "REJ" # invalid login
    pas = "PAS" # valid login
    bad = "BAD" # invalid request

class msg:
    def __init__(self, kind, account, amount, var):
        self.code = kind
        self.acct = account
        self.amt = amount
        self.last = var
    def encode(self):
        msgStr = self.code+','+str(self.acct)+','+str(self.amt)+','+str(self.last)
        msgUni = msgStr.encode('utf-8')
        return msgUni
    def login(self):
        try:
            custs = pd.read_csv("customers.csv", index_col="acct")
            if self.acct not in custs.index:
                return msg(cd.rej, 0, 0, 0)
            cust = custs.loc[self.acct]
            if self.last == cust.pin:
                return msg(cd.pas, 0, 0, 0)
            else:
                return msg(cd.rej, 0, 0, 0)
        except OSError:
            print("Customer database does not exist")
        except IndexError:
            print("Customer acct does not exist")
        except KeyError:
            print("KeyError")

    def transaction(self):
        try:
            custs = pd.read_csv("customers.csv", index_col="acct")
            cust = custs.loc[self.acct]
            if self.code == "WTH":
                if self.amt > cust.balance:
                    self.last = cust.balance
                    receipt = msg("WTH", self.acct, 0, self.last)
                else:
                    custs.loc[self.acct, "balance"] -= self.amt
                    receipt = msg("WTH", self.acct, self.amt, custs.loc[self.acct, "balance"])
            elif self.code == "DEP":
                custs.loc[self.acct, "balance"] += self.amt
                receipt = msg("DEP", self.acct, self.amt, custs.loc[self.acct, "balance"])
            elif self.code == "BAL":
                bal = cust.balance
                receipt = msg("BAL", self.acct, 0, bal)
            custs.to_csv("customers.csv")
            return receipt
        except OSError:
            print("Customer database does not exist")
        except IndexError:
            print("Customer acct does not exist")
        except KeyError:
            print("KeyError")
    def openAccount(self, fname, lname):
        try:
            custs = pd.read_csv("customers.csv", index_col="acct")
            self.acct = custs.index.max() + 1
            newCustDict = {"acct":[self.acct],
                           "fname":[fname], "lname":[lname],
                           "pin":[self.last], "balance":[self.amt]}
            newCust = pd.DataFrame(newCustDict).set_index("acct")
            custs = custs.append(newCust)
            custs.to_csv("customers.csv")
            return msg("OPN", self.acct, 0, self.amt)
        except OSError:
            print("Customer database does not exist")

class raw:
    def __init__(self, unicode):
        self.uni = unicode
    def decode(self):
        msgStr = self.uni.decode('utf-8')
        msgTok = msgStr.split(',')
        code = msgTok[0]
        acct = int(msgTok[1])
        amt = int(msgTok[2])
        var = int(msgTok[3])
        return msg(code, acct, amt, var)

class nameTok:
    def __init__(self, first, last):
        self.first = first
        self.last = last
    def encode(self):
        nameStr = self.first+','+self.last
        nameUni = nameStr.encode('utf-8')
        return nameUni

class nameUni:
    def __init__(self, unicode):
        self.uni = unicode
    def decode(self):
        msgStr = self.uni.decode('utf-8')
        msgTok = msgStr.split(',')
        first = msgTok[0]
        last = msgTok[1]
        return first, last
