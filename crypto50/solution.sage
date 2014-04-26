with open("crypto.txt", "r") as f:    
    for s in f:
        exec s

_, d, _ = xgcd(e, n-1)
message = Integers(n)(crypted)**d
print hex(int(message))[2:-1].decode("hex")
    
