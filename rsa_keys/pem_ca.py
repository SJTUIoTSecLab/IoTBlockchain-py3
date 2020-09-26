import rsa

(pubkey, privkey) = rsa.newkeys(1024)

pub = pubkey.save_pkcs1()
with open('g5008_public.pem', 'wb+') as f:
    f.write(pub)

pri = privkey.save_pkcs1()
with open('g5008_private.pem', 'wb+') as f:
    f.write(pri)