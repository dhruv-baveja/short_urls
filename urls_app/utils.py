import hashlib

import arrow


def get_short_url(long_url):
    timestamp = arrow.utcnow().datetime
    str_input = long_url + str(timestamp)
    hashed_str = hashlib.sha256(str_input.encode('utf-8')).hexdigest()
    return hashed_str[::8]
