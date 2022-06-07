from cryptography.fernet import Fernet
import pathlib 
import os
from dotenv import load_dotenv
load_dotenv()

def generate_key():
    return Fernet.generate_key().decode("UTF-8")

ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")

def encrypt_dir(input_dir, output_dir):
    key = ENCRYPTION_KEY
    if not key:
        raise Exception("Encryption key not found")
    fer = Fernet(key)
    input_dir = pathlib.Path(input_dir)
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    for path in input_dir.glob("*"):
        _path_bytes = path.read_bytes() # open(filepath, 'rb')
        data = fer.encrypt(_path_bytes)
        rel_path = path.relative_to(input_dir)
        dest_path = output_dir/rel_path
        dest_path.write_bytes(data)

def decrypt_dir(secured_dir, output_dir):
    key = ENCRYPTION_KEY
    if not key:
        raise Exception("Encryption key not found")
    fer = Fernet(key)
    secured_dir = pathlib.Path(secured_dir)
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    for path in secured_dir.glob("*"):
        _path_bytes = path.read_bytes() # open(filepath, 'rb')
        data = fer.decrypt(_path_bytes)
        rel_path = path.relative_to(secured_dir)
        dest_path = output_dir/rel_path
        dest_path.write_bytes(data)


