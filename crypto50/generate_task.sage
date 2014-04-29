import random
n = next_prime(random.getrandbits(4096), False)
e = 2**16+1
flag = "MSUCTF__FERMAT_AND_EULER"

m = int(flag.encode("hex"), 16)
field = Integers(n)
crypted = field(m)**e
with open("crypto.txt", "w") as f:
    f.write("n = {n}\ne = {e}\ncrypted = {crypted}\n".format(**locals()))
