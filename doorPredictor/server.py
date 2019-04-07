import json
import ibmiotf.application
from time import sleep, time
import numpy as np
import pandas as pd
from joblib import load
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.svm import SVC
import os


def myCallback(cmd):
    if cmd.event == "doorData":
        payload = json.loads(cmd.payload)
        # print(cmd.payload)
        df = pd.read_json(payload, orient='records')
        print(df)
        estimate(svclassifier.predict(df))


def estimate(l):
    op = 0
    close = 0
    for num in l:
        if num == 1:
            op += 1
        else:
            close += 1

    if op > close:
        print("open")
        myData = {'doorStatus': 'Open'}
        client.publishEvent(
            "door_sensor", "b827eb0acdd1", "doorStatus", "json", myData)
    else:
        print("close")
        myData = {'doorStatus': 'Close'}
        client.publishEvent(
            "door_sensor", "b827eb0acdd1", "doorStatus", "json", myData)


print("ahah")
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
