proof.arithmetic(False)

with open("crypto.txt", "r") as f:    
    for s in f:
        exec s

if not n in Primes():
    print "Sorry, that works only for prime modulus"
    raise SystemExit()
    
d = xgcd(e, n-1)[1]
message = Integers(n)(crypted)**d
print hex(int(message))[2:-1].decode("hex")
    
