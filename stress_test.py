# USAGE
# python stress_test.py

# import the necessary packages
from threading import Thread
import requests
import time
import json

# initialize the Keras REST API endpoint URL along with the input
# data path
KERAS_REST_API_URL = "http://localhost:5000/predict"
DATA_PATH = "test.json"

# initialize the number of requests for the stress test along with
# the sleep amount between requests
NUM_REQUESTS = 500
SLEEP_COUNT = 0.05


def call_predict_endpoint(n, data):
    # submit the request
    r = requests.post(KERAS_REST_API_URL, json=data).json()

    # ensure the request was sucessful
    if r["success"]:
        print("[INFO] thread {} OK".format(n))

    # otherwise, the request failed
    else:
        print("[INFO] thread {} FAILED".format(n))


if __name__ == '__main__':
    # load the input image and construct the payload for the request
    with open(DATA_PATH, 'r') as f:
        data = json.load(f)

    # loop over the number of threads
    for i in range(0, NUM_REQUESTS):
        # start a new thread to call the API
        t = Thread(target=call_predict_endpoint, args=(i, data,))
        t.daemon = True
        t.start()
        time.sleep(SLEEP_COUNT)

    # insert a long sleep so we can wait until the server is finished
    # processing the images
    time.sleep(300)
