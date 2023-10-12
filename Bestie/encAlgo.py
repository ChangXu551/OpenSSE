
import os
import re
import hashlib
import hmac
import math
import array
import time
import string
import base64
from Crypto.Cipher import AES
from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from cryptography.hazmat.primitives import padding
import binascii

class encAlgo:
    def __init__(self):
        self.K1 = 0
        self.K2 = 0
        self.K3 = 0
        self.K4 = 0
        self.k = 32
        self.z = 100000
        self.id_size = 20       # SHA1 is used for file ID and is 20 bytes long. Currently not changeable
        self.addr_size = 0

    def x_o_r(self, str1, str2):# 传入两个数，并返回它们的异或结果，结果为16进制数
        byte1 = int(str1, 16)
        byte2 = int(str2, 16)
        value = hex(byte1 ^ byte2)[2:].zfill(20)
        return value

    def Gen(self):  #初始化密钥K1-K4
        self.K1 = os.urandom(self.k)
        self.K2 = os.urandom(self.k)
        self.K3 = os.urandom(self.k)
        self.K4 = os.urandom(self.k)
        self.keys = (self.K1, self.K2, self.K3, self.K4)
        return self.keys

    def importkeys(self, keys):
        self.K1 = keys[0]
        self.K2 = keys[1]
        self.K3 = keys[2]
        self.K4 = keys[3]
        self.k = len(self.K1)

    def exportkeys(self):  #导出密钥
        return (self.K1, self.K2, self.K3, self.K4)

    def F1(self,key, msg):
        b_key = bytes(key, 'utf-8')
        b_msg = bytes(msg, 'utf-8')
        mac = hmac.new(b_key, b_msg, digestmod = "sha256") # 第一个参数是密钥key，第二个参数是待加密的字符串，第三个参数是hash函数
        return mac.hexdigest()  # 打印出加密后字符串的十六进制格式

    def F2(self,key, msg):
        b_key = bytes(key, 'utf-8')
        b_msg = bytes(msg, 'utf-8')
        mac = hmac.new(b_key, b_msg, digestmod='sha256')  # 第一个参数是密钥key，第二个参数是待加密的字符串，第三个参数是hash函数
        # print(mac.hexdigest())
        return mac.hexdigest()  # 打印出加密后字符串的十六进制格式

    def F3(self,key, msg):
        b_key = bytes(key, 'utf-8')
        b_msg = bytes(msg, 'utf-8')
        mac = hmac.new(b_key, b_msg, digestmod='sha256')  # 第一个参数是密钥key，第二个参数是待加密的字符串，第三个参数是hash函数
        # print(mac.hexdigest())
        return mac.hexdigest()  # 打印出加密后字符串的十六进制格式

    def F4(self,key, msg):
        b_key = bytes(key, 'utf-8')
        b_msg = bytes(msg, 'utf-8')
        mac = hmac.new(b_key, b_msg, digestmod='sha512')  # 第一个参数是密钥key，第二个参数是待加密的字符串，第三个参数是hash函数
        # print(mac.hexdigest())
        return mac.hexdigest()  # 打印出加密后字符串的十六进制格式



    def hash_length(self, msg, int):  # h(msg+i)+h(mag+i-1)+……
        h = hash(msg)
        i = 0
        while i < int:
            h = hash(msg + bytes(str(i), "utf-8")) + h
            i = i + 1
        return h

    def egcd(self, a, b):  # 扩展欧几里得算法
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = self.egcd(b % a, a)
            return (g, x - (b // a) * y, y)

    def modinv(self, a, m):  # 模逆
        g, x, y = self.egcd(a, m)
        if g != 1:
            raise Exception('modular inverse does not exist')
        else:
            return x % m

    def get_str_sha1_secret_str(self, res):
        """
        使用sha1加密算法，返回str加密后的字符串
        """
        sha = hashlib.sha256(res.encode('utf-8'))
        encrypts = sha.hexdigest()
        # print(encrypts)
        return encrypts

    def add_to_16(self, value):
        while len(value) % 16 != 0:
            value += '\0'
        return str.encode(value)  # 返回bytes

        # 加密方法

    def encrypt_oracle(self, key, text):
        # 初始化加密器
        aes = AES.new(self.add_to_16(key), AES.MODE_ECB)
        # 先进行aes加密
        encrypt_aes = aes.encrypt(self.add_to_16(text))
        # 用base64转成字符串形式
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
        # print(encrypted_text)
        return encrypted_text

        # 解密方法

    def decrypt_oralce(self, key, text):

        # 初始化加密器
        aes = AES.new(self.add_to_16(key), AES.MODE_ECB)
        # 优先逆向解密base64成bytes
        base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
        # 执行解密密并转码返回str
        decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
        # print(decrypted_text)
        return decrypted_text



if __name__=='__main__':
    begin_time = time.time()
    for i in range(10000):
        enc=encAlgo().F1('123','123')
    print(enc)
    end_time = time.time()
    print("time:", end_time - begin_time)
    enk=int(enc,16)% 100000000
    print(enk)
    enc = encAlgo().F2('123', '123')
    print(enc)
    enk = int(enc, 16) % 100000000
    print(enk)
    enc=encAlgo().F3('123','123')
    print(enc)
    enk=int(enc,16)% 100000000
    print(enk)
    enc = encAlgo().F4('123', '123')
    print(enc)
    enk = int(enc, 16) % 100000000
    print(enk)
    begin_time = time.time()
    for i in range(10000):
        enc = encAlgo().get_str_sha1_secret_str('123')
    print(enc)
    end_time = time.time()
    print("time:", end_time - begin_time)

    begin_time = time.time()
    for i in range(10000):
        enc = encAlgo().encrypt_oracle('123','123')
    print(enc)
    end_time = time.time()
    print("time:", end_time - begin_time)

