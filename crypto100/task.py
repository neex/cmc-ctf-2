import hashlib
import SocketServer

HOST = "0.0.0.0"
PORT = 8475

def is_lucky(name):  # You must be very lucky if you can pass this
    h = hashlib.sha1()
    for i in xrange(10):
        h.update(name[i::10])
        digest_num = map(ord, h.digest())        
        if sum(digest_num[::2]) != sum(digest_num[1::2]) or sum(digest_num[:len(digest_num)/2]) != sum(digest_num[len(digest_num)/2:]):
            return False
    return True
    

class Handler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.stream = self.request.makefile('r+', bufsize=0)
        self.stream.write("Enter your name: ")
        name = self.stream.readline().strip()
        if is_lucky(name):
            self.stream.write("Seems like you are lucky enough!\nFlag is {0}\n".format(flag))
        else:
            self.stream.write("Sorry, we don't need unlucky ones in our team\n")
        self.stream.close()
        self.stream = None

        
if __name__ == "__main__":            
        with open("flag.txt") as f:
            flag = f.read().strip()
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        server = SocketServer.ThreadingTCPServer((HOST, PORT), Handler)
        server.allow_reuse_address = True    
        server.serve_forever()
