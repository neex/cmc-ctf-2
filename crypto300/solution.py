import os
from Crypto.Cipher import AES
from socket import socket
import thread
PORT = 8765

sended, recved = 0, 0

def quit():
    global sended, recved
    print "Sended %s, recved %s" % (sended, recved)    
    raise SystemExit()
    
    
buf = []
    
def send(s):
    global stream, sended
    to_send = s.encode("base64").replace("\n", "") + "\n"
    sended += len(to_send)
    stream.write(to_send)

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
        send("secret")
        print recv()
        quit()
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

send(user)
recv()
recv()
recv()

def no_semicolons_send(suf, sec):
    for i in xrange(0, 10):
        send_buf(chr(i)+suf+sec)


def no_semicolons_check_full():
    res = True
    for i in xrange(0, 10):
        r = recv()
        if len(r) > 100:
            res = False
    return res

def no_semicolons_check_second():
    res = False
    for i in xrange(0, 10):
        r = recv()
        if len(r) < 100:
            res = True
    return res
            
print "Finding two blocks without semicolons at all"            
while True:
    suf = os.urandom(15)
    sec = os.urandom(16)
    no_semicolons_send(suf, sec)
    flush()
    if no_semicolons_check_full():
        break
print "Done"
        
deltas = []
for i in xrange(7):
    for ch in xrange(256):
       sn = suf[:i] + chr(ord(suf[i]) ^ ch) + suf[i+1:]
       no_semicolons_send(sn, sec)

print "Sending request length %s in another thread" % len("".join(buf))
flush()

for i in xrange(7):
    print "Bruting character",i
    for ch in xrange(256):
       sn = suf[:i] + chr(ord(suf[i]) ^ ch) + suf[i+1:]
       no_semicolons_send(sn, sec)
       if not no_semicolons_check_second():
            deltas.append(ch)
            print "Found char ",i
    if len(deltas) != i + 1:
        print "Something went wrong"
        quit()

print "Sending command to disable encryption"
cmd = ";noenc;"
snl = []
for i in xrange(7):
    snl.append(chr(ord(suf[i]) ^ deltas[i] ^ ord(";") ^ ord(cmd[i])))
send("0" + "".join(snl) + "0" * 8 + sec)
recv()
print "Error: seems like encryption is still enabled"
quit()
