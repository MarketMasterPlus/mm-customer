# mm-customer/generate_jwt_secret.py
import secrets

def generate_jwt_secret():
    # Generate a 64-character hex string as a secret key
    secret_key = secrets.token_hex(32)
    print(f"Your generated JWT Secret Key is:\n{secret_key}")

if __name__ == "__main__":
    generate_jwt_secret()
