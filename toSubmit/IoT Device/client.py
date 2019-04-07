import ibmiotf.application
import smbus
import os
import json
import uuid
from time import sleep
from statistics import stdev, median
import pandas as pd


# some MPU6050 Registers and their Address
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

client = None

stdDev = 0.03
meanGx = -0.65
meanGy = 0.05
meanGz = -0.65
meanAx = 0.08
meanAy = 0.98
meanAz = 0.03

temp = []

countBig = 0
countEnd = 0


def MPU_Init():
    # write to sample rate register
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

    # Write to power management register
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

    # Write to Configuration register
    bus.write_byte_data(Device_Address, CONFIG, 0)

    # Write to Gyro configuration register
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

    # Write to interrupt enable register
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)


def read_raw_data(addr):
    # Accelero and Gyro value are 16-bit
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr+1)

    # concatenate higher and lower value
    value = ((high << 8) | low)

    # to get signed value from mpu6050
    if(value > 32768):
        value = value - 65536
    return value


def checkThreshold(val, mean):
    if val < 0:
        return val <= (mean - (3*stdDev))
    else:
        return val > (mean + (3*stdDev))


def split_seq(seq, numChuncks):
    newseq = []
    splitsize = 1.0/numChuncks*len(seq)
    for i in range(numChuncks):
        newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
    return newseq


def myCallback(cmd):
    print(cmd)
    if cmd.event == "doorStatus":
        payload = json.loads(cmd.payload)
        command = payload["doorStatus"]
        print(command)


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()


try:
    options = ibmiotf.application.ParseConfigFile("device.cfg")

    client = ibmiotf.application.Client(options)
    client.connect()
    client.deviceEventCallback = myCallback
    client.subscribeToDeviceEvents(event="doorStatus")
    # myData = {'doorStatus': 'Open'}
    # client.publishEvent(
    #     "door_sensor", "b827eb0acdd1", "doorStatus", "json", myData)
    sleep(0.2)
    c = ['Ax', 'Ay', 'Az', 'Gx', 'Gy', 'Gz']
    df = pd.DataFrame(columns=c)
    while True:

        # Read Accelerometer raw value
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)

        # Read Gyroscope raw value
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_YOUT_H)
        gyro_z = read_raw_data(GYRO_ZOUT_H)

        # Full scale range +/- 250 degree/C as per sensitivity scale factor
        Ax = acc_x/16384.0
        Ay = acc_y/16384.0
        Az = acc_z/16384.0

        Gx = gyro_x/131.0
        Gy = gyro_y/131.0
        Gz = gyro_z/131.0
        if checkThreshold(Ax, meanAx) or checkThreshold(Ay, meanAy) or checkThreshold(Az, meanAz) or checkThreshold(Gx, meanGx) or checkThreshold(Gy, meanGy) or checkThreshold(Gz, meanGz):
            countBig += 1
            countEnd = 0
            temp.append((Ax, Ay, Az, Gx, Gy, Gz))
        elif countBig > 20:
            countEnd += 1
            if countEnd > 20:
                s = split_seq(temp, 10)
                # for i in range(0, len(s)):
                #     l = [median([item[0] for item in s[i]]), median([item[1] for item in s[i]]), median([item[2] for item in s[i]]), median(
                #         [item[3] for item in s[i]]), median([item[4] for item in s[i]]), median([item[5] for item in s[i]])]
                #     print(l)
                #     tempdf = pd.DataFrame([l], columns=c)
                # df.append(tempdf)
                df = pd.concat([pd.DataFrame([[median([item[0] for item in s[i]]), median([item[1] for item in s[i]]), median([item[2] for item in s[i]]), median(
                    [item[3] for item in s[i]]), median([item[4] for item in s[i]]), median([item[5] for item in s[i]])]], columns=c) for i in range(0, len(s))], ignore_index=True)

                jsdf = df.to_json(orient='records')
                # print(jsdf)
                client.publishEvent(
                    "door_sensor", "b827eb0acdd1", "doorData", "json", jsdf)
                sleep(0.4)
                print("published")
                countEnd = 0
                countBig = 0
                temp = []
                # Empty the dataframes
                df.iloc[0:0]
        else:
            countBig = 0

        sleep(0.05)

except ibmiotf.ConnectionException as e:
    print(e)
