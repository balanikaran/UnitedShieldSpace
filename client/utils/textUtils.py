import re


def validateEmail(email):
    emailRegex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    if emailRegex.fullmatch(email):
        return True
    return False

def validateUsername(name):
    nameRegex = re.compile(r"(^[a-zA-Z ]*$)")
    if nameRegex.fullmatch(name):
        return True
    return False
