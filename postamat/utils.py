import random
import string


def generate_receive_code(length=6):
    """Generates a random code.

    :param length: Length of random code.
    :return: Random code.
    """
    return ''.join(random.choices(string.digits, k=length))
