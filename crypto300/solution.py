import os
from Crypto.Cipher import AES
from socket import socket

PORT = 8765

    
def send(s):
    global stream
    stream.write(s.encode("base64").replace("\n", "") + "\n")
      
def recv():
    global encrypted_mode, stream, running
    s = stream.readline()
    if not s:
        print "disconnect"        
        raise SystemExit()
    s = s.strip()
    if s == "-=noenc=-":
        print "Hacked! Great"       
        print recv()
        send("secret")
        print recv()
        raise SystemExit()
    if s == "-=lastmessage=-":
        print "Sorry, I accidentally 'quit' command"
        raise SystemExit()
    s = s.decode("base64")
    return s       

if len(os.sys.argv) != 3:
    print "Usage: solution.py <username> <server>"
    raise SystemExit()
    
user = os.sys.argv[2]
server = os.sys.argv[1]
soc = socket()
soc.connect((server, PORT))
stream = soc.makefile('r+', bufsize=0)

send(user)
recv()
recv()
recv()

def no_semicolons_full(suf, sec):
    global ch
    for i in xrange(0, 10):
        send(chr(i)+suf+sec)
        r = recv()
        if len(r) > 100:
            return False
    return True

def no_semicolons_sec(suf, sec):
    global ch
    for i in xrange(0, 10):
        send(chr(i)+suf+sec)
        r = recv()
        if len(r) < 100:
            return True
    return False
            
print "Finding two blocks without semicolons at all"            
while True:
    suf = os.urandom(15)
    sec = os.urandom(16)
    if no_semicolons_full(suf, sec):
        break
print "Done"
        
deltas = []
for i in xrange(7):
    print "Bruting character",i
    for ch in xrange(256):
       sn = suf[:i] + chr(ord(suf[i]) ^ ch) + suf[i+1:]
       if not no_semicolons_sec(sn, sec):
            deltas.append(ch)
            print "Found"
            break
    if len(deltas) != i + 1:
        print "Something went wrong, can't find next char"
        raise SystemExit()

cmd = ";noenc;"
snl = []
for i in xrange(7):
    snl.append(chr(ord(suf[i]) ^ deltas[i] ^ ord(";") ^ ord(cmd[i])))
send("0" + "".join(snl) + "0" * 8 + sec)
print "Something got wrong: " + recv()
