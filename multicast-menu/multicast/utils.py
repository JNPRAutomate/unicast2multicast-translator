import random
import string


def create_random_string(length=40):
    return "".join([random.SystemRandom().choice(string.ascii_letters + string.digits) for i in range(length)])
