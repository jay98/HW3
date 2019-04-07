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
    if cmd.event == "doorStatus":
        payload = json.loads(cmd.payload)
        command = payload["doorStatus"]
        print(command)


svclassifier = load('door_model.joblib')


options = ibmiotf.application.ParseConfigFile("laptop.cfg")

client = ibmiotf.application.Client(options)
client.connect()
client.deviceEventCallback = myCallback
client.subscribeToDeviceEvents(event="doorStatus")

try:
    while True:
        sleep(0.2)
except ibmiotf.ConnectionException as e:
    print(e)
