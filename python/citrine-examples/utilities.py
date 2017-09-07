import os

def check_citrination_key():
    if (citrination_key()):
        return True
    else:
        print ("The environment variable CITRINATION_API_KEY must be assigned to the user's API key")
        return False

def citrination_key():
    return os.getenv('CITRINATION_API_KEY','')