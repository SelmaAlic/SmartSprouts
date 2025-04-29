#Note: Run "pip install pycryptdome" on CMD from your machine

from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def to_encrypt(password):
    #salt generated using salt=get_random_bytes(32)
    salt=b'\xf8\xae\xd5$\xab\x1f"\xd6hw80\xd0e_&e\x90(\x89}s\x97\xd5\xc3|[\x8d\x9aP\xdb\x95'

    #generating encryption key using predefined function
    key=PBKDF2(password,salt,dkLen=32)

    #actual encryption done using Advanced Encryption Standard (AES) algorithm
    cipher=AES.new(key, AES.MODE_CBC)
    encrypted_password= cipher.encrypt(pad(password.encode(), AES.block_size))

    return encrypted_password
