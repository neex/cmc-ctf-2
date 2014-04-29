import hashlib
import SocketServer
import logging
from logcompress import logsetup

HOST = "0.0.0.0"
PORT = 8475

logger = logging.getLogger(__name__)

def is_lucky(name):  # You must be very lucky if you can pass this
    logger.debug("Cheching %s",name)
    h = hashlib.sha1()
    for i in xrange(10):
        h.update(name[i::10])
        digest_num = map(ord, h.digest())        
        if sum(digest_num[::2]) != sum(digest_num[1::2]) or sum(digest_num[:len(digest_num)/2]) != sum(digest_num[len(digest_num)/2:]):
            return False
    return True
    

class Handler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            stream = self.request.makefile('r+', bufsize=0)
            stream.write("Enter your name: ")
            name = stream.readline().strip()
            if is_lucky(name):
                stream.write("Seems like you are lucky enough!\nFlag is {0}\n".format(flag))
            else:
                stream.write("Sorry, we don't need losers in our team\n")
        except Exception as e:
            logger.exception()
        finally:
            stream.close()

        
if __name__ == "__main__":   
        logsetup("lucky.log", "DEBUG")        
        with open("flag.txt") as f:
            flag = f.read().strip()
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        server = SocketServer.ThreadingTCPServer((HOST, PORT), Handler)
        server.allow_reuse_address = True    
        server.daemon_threads = True                
        server.serve_forever()
