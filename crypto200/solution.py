import hashlib, itertools

strs = []
curhash = hashlib.sha1()
for i in xrange(10):
    for s in itertools.product(*[range(ord('A'),ord('Z')+1)]*5):
        s = "".join(map(chr, s))
        h=curhash.copy()
        h.update(s)
        d=map(ord, h.digest())
        if sum(d[::2])==sum(d[1::2]) and sum(d[:len(d)/2])==sum(d[len(d)/2:]):
            curhash = h
            strs.append(s)
            break
       
print "".join(map("".join, zip(*strs)))    
