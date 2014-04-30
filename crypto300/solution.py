import os
from Crypto.Cipher import AES
from socket import socket
import thread
PORT = 8765

sended, recved = 0, 0

def quit(success = False):
    global sended, recved
    print "Sended %s, recved %s" % (sended, recved)    
    raise SystemExit(0 if success else 1)
    
    
buf = []
    
def send_buf(s):
    global stream, sended, buf
    to_send = s.encode("base64").replace("\n", "") + "\n"
    sended += len(to_send)
    buf.append(to_send)

def flush():
    global stream, buf
    thread.start_new_thread(stream.write, ("".join(buf),))
    buf = []
        
def recv():
    global stream, recved
    s = stream.readline()
    recved += len(s)
    if not s:
        print "disconnect"        
        quit()
    s = s.strip()
    if s == "-=noenc=-":
        print "Hacked! Great"       
        recv()
        send_buf("secret")
        flush()
        print recv()
        quit(True)
    if s == "-=lastmessage=-":
        print "Sorry, I accidentally 'quit' command"
        quit()
    s = s.decode("base64")
    return s       

if len(os.sys.argv) != 3:
    print "Usage: solution.py <username> <server>"
    quit()
    
user = os.sys.argv[2]
server = os.sys.argv[1]
soc = socket()
soc.connect((server, PORT))
stream = soc.makefile('r+', bufsize=0)

send_buf(user)
flush()
recv()
recv()
recv()

print "Finding two blocks without semicolons at all"            
while True:
    suf = os.urandom(16)
    sec = os.urandom(16)
    send_buf(suf)
    send_buf(sec)
    flush()
    recv()
    if len(recv()) < 90:
        break
        
print "Done"
        
deltas = []
for i in xrange(4,11):
    for ch in xrange(256):
       sn = suf[:i] + chr(ord(suf[i]) ^ ch) + suf[i+1:]
       send_buf(sn)
       send_buf(sec)

print "Sending request length %s in another thread" % len("".join(buf))
flush()

for i in xrange(4,11):
    print "Bruting character",i
    for ch in xrange(256):
       recv()
       if len(recv()) > 90:
            deltas.append(ch)
            print "Found char ",i
    if len(deltas) != i - 3:
        print "Something went wrong"
        quit()

print "Sending command to disable encryption"
cmd = ";noenc;"
snl = []
for i in xrange(7):
    snl.append(chr(ord(suf[i+4]) ^ deltas[i] ^ ord(";") ^ ord(cmd[i])))
send_buf("0000" + "".join(snl) + "00000")
send_buf(sec)
flush()
recv()
recv()
print "Error: seems like encryption is still enabled"
quit()
