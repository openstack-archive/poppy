import requests
import sys
import time
import datetime


def main(args):
    url = args[1]
    loop = int(args[2])
    sleep_time = int(args[3])

    for x in range(0, loop / sleep_time):
        response = requests.get(url, headers={'PRAGMA': 'akamai-x-cache-on'})
        print (str(datetime.datetime.now()) + " - Akamai Cache Response: " + str(response.headers['X-Cache']))
        time.sleep(sleep_time)


if __name__ == '__main__':
    main(sys.argv)
