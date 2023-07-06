#  Copyright (c) Benedek Szanyó 2023. All rights reserved.
import base64
import os
import time

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Cryptography:
    def __init__(self, key=None):
        self._key = key
        if self._key is None:
            self._key = generate_standard_key()
        self._crypt = Fernet(self._key)

    def set_key(self, key):
        self._key = key
        self._crypt = Fernet(self._key)

    def get_key(self):
        return self._key

    def encrypt(self, not_secret):
        return self._crypt.encrypt(not_secret)

    def decrypt(self, secret):
        try:
            return self._crypt.decrypt(secret)
        except Exception as e:
            time.sleep(1)
            return "!INVALID ENCRYPTION KEY AND/OR DATA!"


def generate_custom_key(random_param, password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=random_param,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(bytes(password, "UTF-8")))


def generate_standard_key():
    return Fernet.generate_key()


def generate_safe_random_number(length=16):
    return os.urandom(length)


if __name__ == "__main__":
    salt = generate_safe_random_number(16)
    password = "1-2-3-4-5-6-7-8-9-10-11-12"
    safety = Cryptography(generate_custom_key(salt, password))
    data = "British troops entered Cuxhaven at 14:00 on 6 May 1945 from now on all radio traffic will cease -- " \
           "wishing you all the best. Lt Kunkel, Closing down forever -- all the best -- goodbye."
    print(data)
    print()
    secret = safety.encrypt(data.encode("UTF-8"))
    print("SALT: " + str(salt))
    print("PASSWORD: " + password)
    print("KEY: " + str(safety.get_key()))
    print("SECRET: " + str(secret))
    print()
    safety = Cryptography(generate_custom_key(salt, password))
    original_data = safety.decrypt(secret).decode("UTF-8")
    print("SALT: " + str(salt))
    print("PASSWORD: " + password)
    print("KEY: " + str(safety.get_key()))
    print("ORIGINAL DATA: " + str(original_data))
