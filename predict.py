from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
from joblib import load
import pandas as pd
import numpy as np
from time import sleep, time
from statistics import stdev, median
import ibmiotf.application
import json


def myCallback(cmd):
    if cmd.event == "doorData":
        payload = json.loads(cmd.payload)
        # print(cmd.payload)
        df = pd.read_json(payload, orient='records')
        estimate(svclassifier.predict(df))


def estimate(l):
    open = 0
    close = 0
    for num in l:
        if num == 1:
            open += 1
        else:
            close += 1

    if open > close:
        print("open")
    else:
        print("close")


svclassifier = load('door_model.joblib')


options = ibmiotf.application.ParseConfigFile("server.cfg")

client = ibmiotf.application.Client(options)
client.connect()
client.deviceEventCallback = myCallback
client.subscribeToDeviceEvents(event="doorData")

try:
    while True:
        sleep(0.2)
except ibmiotf.ConnectionException as e:
    print(e)
