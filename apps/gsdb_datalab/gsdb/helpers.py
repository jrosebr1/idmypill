# import the necessary packages
import hashlib


def get_short_hash(input_string, length=16):
    # encode the input string, compute the hash, and shorten it to its desired
    # length
    return hashlib.sha256(input_string.encode()).hexdigest()[:length]
