# This file is part of Qualified Caching-as-a-Service.
# Copyright 2019 Intelligent-distributed Cloud and Security Laboratory (ICNS Lab.)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
# title           : TestClient.py
# description     : python SDCManager class
# author          : Yunkon(Alvin) Kim
# date            : 20190305
# version         : 0.1
# python_version  : 3.6
# notes           : This class is an implementation of a test client to consume data from Software-Defined Cache (SDC)
#                   in the Python Programming Language.
# ==============================================================================

import os
# import logging
import random
import threading
import time

import paho.mqtt.client as mqtt
from paho.mqtt import publish

client_id = "Client_1"

MQTT_HOST_ON_EDGE = "127.0.0.1"
MQTT_PORT_ON_EDGE = 1883

# ----------------------------------------Error calculation for PID controller---------------------------------------#
TEST_TIME = 10  # sec


# -------------------------------------------------------MQTT--------------------------------------------------------#
def on_local_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected - Result code: " + str(rc))
        client.subscribe("edge/client/" + client_id + "/data")

    else:
        print("Bad connection returned code = ", rc)
        print("ERROR: Could not connect to MQTT")


def on_local_message(client, userdata, msg):
    # print("Cart new message: " + msg.topic + " " + str(msg.payload))
    message = msg.payload
    print("Arrived topic: %s" % msg.topic)
    # print("Arrived message: %s" % message)

    if msg.topic == "edge/client/" + client_id + "/data":
        print("Data size: %s" % len(message))
        # time.sleep(0.03)
    else:
        print("Unknown - topic: " + msg.topic + ", message: " + message)


def on_local_publish(client, userdata, mid):
    print("mid: " + str(mid))


def on_local_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_local_log(client, userdata, level, string):
    print(string)


# The below lines will be used to publish the topics
# publish.single("elevator/starting_floor_number", "3", hostname=MQTT_HOST, port=MQTT_PORT)
# publish.single("elevator/destination_floor_number", "2", hostname=MQTT_HOST, port=MQTT_PORT)
# ------------------------------------------------------------------------------------------------------------------#

is_finish = False

if __name__ == '__main__':

    # MQTT connection
    message_local_client = mqtt.Client("Client")
    message_local_client.on_connect = on_local_connect
    message_local_client.on_message = on_local_message

    message_local_client.connect(MQTT_HOST_ON_EDGE, MQTT_PORT_ON_EDGE, 60)

    message_local_client.publish("core/edge/" + client_id + "/data_req", 100)
    message_local_client.loop_start()

    while not is_finish:
        time.sleep(0.001)

    message_local_client.loop_stop()
    # start_time = time.time()
    # read_size = (2 << 19)
    # while True:
    #     # consume data
    #     # This section will be changed to apply the distributed messaging structure.
    #     # In other words, MQTT will be used.
    #     message_client.publish("core/edge/" + client_id + "/data_req", read_size)
    #     # print("Consuming data")
    #     running_time = time.time() - start_time
    #     if running_time > TEST_TIME:
    #         break
    #     time.sleep(0.03)
