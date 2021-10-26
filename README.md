# CPBank
An online banking client-server application, modeled after HTTP; implemented in Python.

client.py - the client application
server.py - the server application
cpbank.py - to be imported to the client and server programs

The program is intended to implement an application-level protocol that could be implemented on any platform.

The client and server communicate through "request"/"receipt" pairs using comma-delimited 4-tuples:

Client -> (msg_code,account_num,transaction_amount,pin_num) -> Server
Server -> (msg_code,account_num,transaction_amount,balance) -> Client

msg_code           - unique three-byte message type identifier in UTF-8

account_num        - the account number

transaction_amount - how much is being deposited or withdrawn

pin_num            - the pin number

balance            - the available balance

Client opens a new TCP connection for every login attempt.
The client may open an account ('OPN'), make a deposit  ('DEP'), withdrawal ('WTH'), or check their balance ('BAL').
Client need only provide a pin on login attempts and account creation.
On login attempt, server will reject ('REJ') or pass ('PAS') client.
