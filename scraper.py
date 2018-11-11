import requests
import time

def timeout(to=True):
    if 'slp' not in timeout.__dict__:
        timeout.slp = 1
        return timeout.slp
    elif to:
        timeout.slp *= 2
    else:
        timeout.slp = 1
    return timeout.slp

def checkRequest(r):
    if r.status_code != requests.codes.ok:
        time.sleep(timeout()) # back off exponentially
        print("error")
        return False
    else:
        timeout(False)
        return True
