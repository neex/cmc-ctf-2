import random
import SocketServer
import os
from Crypto.Cipher import AES
import logging
from logcompress import logsetup


HOST = "0.0.0.0"
PORT = 8765

logger = logging.getLogger(__name__)

users = {"guest": 
            {"client_key" : "0" * 32, 
             "server_key" : "1" * 32,
             "secret" : "no secrets for this user"}, 
             
        "alice": 
            {"client_key" : "KuWvrEZFOYMLvQj9cjkpCEA28aQmwUnW", 
             "server_key" : "ncOuaF2swcXLCZzWfvdyGANUsrchaCT9",
             "secret" : "MSUCTF__THAT_IS_WHY_YOU_BETTER_USE_HMAC"}}

help = """
Available commands:
    users   ---   list all users
    secret  ---   show your secret
    noenc   ---   disable channel encryption
    help    ---   show this help    
    quit    ---   exit
    
    
You can use semicolon to send many commands in one line"""
    
class Handler(SocketServer.BaseRequestHandler):
    def send(self, s):
        logger.debug("Sending %s to %s on %s (encryption = %s)", repr(s), self.user, self.peername, self.encrypted_mode)
        if self.encrypted_mode:
            s += " " * ((-len(s)) % 16)
            s = self.server_aes.encrypt(s)
        to_send = s.encode("base64").replace("\n","")+"\n"
        self.stream.write(to_send)
      
    def recv(self):    
        s = self.stream.readline()
        if s == "":
            self.running = False
            return ""
        s = s.strip()
        s = s.decode("base64")
        if self.encrypted_mode:
            s = self.client_aes.decrypt(s)
        logger.debug("Received %s from %s on %s (encryption = %s)", repr(s), self.user, self.peername, self.encrypted_mode)
        return s            
    
    def init_ciphers(self, user, client_iv, server_iv):
        self.encrypted_mode = True
        self.client_aes = AES.new(users[user]["client_key"], AES.MODE_CBC, client_iv)
        self.server_aes = AES.new(users[user]["server_key"], AES.MODE_CBC, server_iv)
        
    def shutdown_enc(self):
        self.encrypted_mode = False
        self.stream.write("-=noenc=-\n")
        
    def process_command(self, cmd):
        logger.debug("Processing %s from %s on %s (encryption = %s)", repr(cmd), self.user, self.peername, self.encrypted_mode)
        if cmd == "help":
            return help
        if cmd == "quit":
            self.running = False
            self.stream.write("-=lastmessage=-\n")
            return "Ok, exiting"
        if cmd == "users":
            return "\n".join(users)
        if cmd == "noenc":
            self.shutdown_enc()
            return "Ok, no encryption anymore"        
        if cmd == "secret":
            return "Your secret: " + users[self.user]["secret"]                    
        return "Unknown command: "+cmd+"\n\nPlease use 'help' for command list"
        
    def handle(self):
        try:
            self.peername = self.request.getpeername()
            self.user = "<not defined yet>"
            self.encrypted_mode = False
            self.banner = "Welcome!"
            self.prompt = "\n\n>"                
            self.stream = self.request.makefile('r+', bufsize=0)
            self.user = self.recv()
            print "User: ",self.user
            if not self.user in users:
                self.send("no such user!")
                raise Exception()
            server_iv = os.urandom(16)
            client_iv = os.urandom(16)                            
            self.send(server_iv)
            self.send(client_iv)
            self.init_ciphers(self.user, client_iv, server_iv)            
            self.send(self.banner + self.prompt)
            self.running = True
            while self.running:
                command_str = self.recv().strip()
                output = "\n\n".join(map(self.process_command, filter(None, map(str.strip, command_str.split(";")))))+self.prompt
                self.send(output)
        except Exception as e:
            logger.exception("Exception from %s", self.peername)
            raise
        finally:
            self.stream.close()

        
if __name__ == "__main__":    
        logsetup("chained.log", "DEBUG")         
        SocketServer.ThreadingTCPServer.allow_reuse_address = True
        server = SocketServer.ThreadingTCPServer((HOST, PORT), Handler)
        server.allow_reuse_address = True    
        server.serve_forever()
