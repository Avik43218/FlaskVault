from cryptography.fernet import Fernet
import random, os, string


def encrypt(email, passwd):

    master_key = os.getenv("MASTER_KEY").encode()
    if master_key is None:
        raise ValueError("Master Key could not be found!")
    
    encrypt_key = os.getenv("ENCRYPTED_KEY").encode()
    if encrypt_key is None:
        raise ValueError("Main Encrypted Key could not be found!")
    
    key = Fernet(master_key).decrypt(encrypt_key)
    cipher = Fernet(key)

    charset = string.ascii_letters + string.digits + string.punctuation

    salted_passwd = passwd + ''.join(random.sample(charset, 20))

    encrypted_email = cipher.encrypt(email.encode()).decode('utf-8')
    encrypted_passwd = cipher.encrypt(salted_passwd.encode()).decode('utf-8')

    encrypted_user = (encrypted_email, encrypted_passwd)

    return encrypted_user


def decrypt(encrypted_email):

    master_key = os.getenv("MASTER_KEY").encode()
    if master_key is None:
        raise ValueError("Master Key could not be found!")
    
    encrypt_key = os.getenv("ENCRYPTED_KEY").encode()
    if encrypt_key is None:
        raise ValueError("Main Encrypted Key could not be found!")
    
    key = Fernet(master_key).decrypt(encrypt_key)
    cipher = Fernet(key)

    email = cipher.decrypt(encrypted_email).decode('utf-8')

    return email
