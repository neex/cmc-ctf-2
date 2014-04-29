import hashlib

def is_lucky(name):  # You must be very lucky if you can pass this
    h = hashlib.sha1()
    for i in xrange(10):
        h.update(name[i::10])
        digest_num = map(ord, h.digest())        
        if sum(digest_num[::2]) != sum(digest_num[1::2]) or sum(digest_num[:len(digest_num)/2]) != sum(digest_num[len(digest_num)/2:]):
            return False
    return True
