import exceptions, requests, threading, time
import sys

requestRate = 1
connectionPerSec = 4

def client_notify(msg):
    return time.time(), threading.current_thread().name, msg

def generate_req(reqSession):
    requestCounter = 0
    while requestCounter < requestRate:
        try:
            response1 = reqSession.get('http://www.google.com')
            if response1.status_code == 200:
                print client_notify('r')
        except:
            print("Unexpected error:", sys.exc_info()[0])
            break
        requestCounter += 1

def main():
    for cnum in range(connectionPerSec):
        s1 = requests.session()
        th = threading.Thread(
            target=generate_req, args=(s1,),
            name='thread-{:03d}'.format(cnum),
        )
        th.start()

    for th in threading.enumerate():
        if th != threading.current_thread():
            th.join()

if __name__=='__main__':
    main()