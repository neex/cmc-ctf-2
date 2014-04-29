import os
from Crypto.Cipher import AES
from socket import socket

PORT = 8765

users = {"guest": 
            {"client_key" : "0" * 32, 
             "server_key" : "1" * 32}
        }
    
def send(s):
    global encrypted_mode, stream
    if encrypted_mode:
        s += " " * ((-len(s)) % 16)
        s = client_aes.encrypt(s)
    stream.write(s.encode("base64").replace("\n", "") + "\n")
      
def recv():
    global encrypted_mode, stream, running
    s = stream.readline()
    if not s:
        print "disconnect"        
        raise SystemExit()
    s = s.strip()
    if s == "-=noenc=-":
        encrypted_mode = False
        return recv()
    if s == "-=lastmessage=-":
        running = False
        return recv()
    s = s.decode("base64")
    if encrypted_mode:
        s = server_aes.decrypt(s)
    return s       

if len(os.sys.argv) != 3:
    print "Usage: client.py <username> <server>"
    raise SystemExit()
    
user = os.sys.argv[2]
if not user in users:
    print "No keys for user", user
    raise SystemExit()   
 
server = os.sys.argv[1]
soc = socket()
soc.connect((server, PORT))
stream = soc.makefile('r+', bufsize=0)

running = True
encrypted_mode = False
send(user)
server_aes = AES.new(users[user]["server_key"], AES.MODE_CBC, recv())
client_aes = AES.new(users[user]["client_key"], AES.MODE_CBC, recv())
encrypted_mode = True

print recv().strip(),
while running:
    command_str = raw_input()    
    send(command_str.strip())
    print recv().strip(),
