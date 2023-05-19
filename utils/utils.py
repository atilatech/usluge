import random
import string

RIDE_REQUESTS_KEY = 'ride_requests'


def get_random_string(length=16):
    # choose from all lowercase letter
    options = string.ascii_lowercase + string.digits
    result_str = ''.join(random.choice(options) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str
