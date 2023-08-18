import jwt
import sys


# Crack token
def crack(token, key):
    try:
        jwt.decode(token, key)
        sys.stdout.write("[#] KEY FOUND: %s\n" % key)
        sys.stdout.flush()
        exit(0)
    except jwt.exceptions.InvalidSignatureError:
        print("[-] Key failed: " + key)
        pass


# Decode
def decode(token):
    token_decoded = jwt.decode(token, verify=False)
    print("Decoded Token")
    print(token_decoded)
    print()


def main():
    payload = {
        "linkIds": ["3pGGZC6j"],
        "role": "CODE",
        "exp": 1723894233
    }
    secret = "test"

    # Encode + sign
    jwt_token = jwt.encode(payload, secret, algorithm="HS256")
    jwt_token = jwt_token.decode("utf-8")
    print("Generated Token")
    print(jwt_token)
    print()

    # Brute force crack
    crack(jwt_token, "test1")
    crack(jwt_token, "test2")
    crack(jwt_token, "test")
    crack(jwt_token, "test3")


if __name__ == "__main__":
    main()
