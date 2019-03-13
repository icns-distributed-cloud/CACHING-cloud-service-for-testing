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

# import logging
import threading
import time

import matplotlib.pyplot as plt
import numpy as np
import paho.mqtt.client as mqtt
from paho.mqtt import publish

client_id = "Client_1"

# MQTT_HOST_ON_EDGE = "192.168.0.58"
# MQTT_PORT_ON_EDGE = 1883
MQTT_HOST_ON_EDGE = "163.180.117.185"
MQTT_PORT_ON_EDGE = 11883

# ----------------------------------------Error calculation for PID controller---------------------------------------#
TEST_TIME = 30  # sec

is_finish = False
is_running = False
is_received = False

condition = threading.Condition()

cache_hits_list = []


# -------------------------------------------------------MQTT--------------------------------------------------------#
def on_local_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected - Result code: " + str(rc))
        client.subscribe("edge/client/" + client_id + "/data")
        client.subscribe("edge/client/" + client_id + "/start_caching")

    else:
        print("Bad connection returned code = ", rc)
        print("ERROR: Could not connect to MQTT")


def on_local_message(client, userdata, msg):
    global is_running
    global condition
    global cache_hits_list

    # print("Cart new message: " + msg.topic + " " + str(msg.payload))
    message = msg.payload
    print("Arrived topic: %s" % msg.topic)
    # print("Arrived message: %s" % message)

    if msg.topic == "edge/client/" + client_id + "/data":
        with condition:
            # if message.decode("utf-8") == "False":
            #     print("No data (Message: %s)" % message)
            # else:
            #     print("Here")
            if message != "False".encode():
                print("Data size: %s" % len(message))
                cache_hits_list.append(1)
            else:
                print("No data received(Message: %s)" % message)
                cache_hits_list.append(0)
            # print("Data size: %s" % message)
            condition.notify()
        # time.sleep(0.03)
    elif msg.topic == "edge/client/" + client_id + "/start_caching":
        scenario_no = int(message)
        # Starting threads
        print("Scenario number: % s" % scenario_no)
        if scenario_no == 1:
            t1.start()
            time.sleep(0.05)
            is_running = True
        else:
            print("Unknown - scenario number: %s" % scenario_no)

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


def consume_data_scenario1(mqtt_obj):
    # A cloud service periodically consumes an equal amount of cached data.
    global condition

    start_time = time.time()
    read_size = (1 << 19)
    with condition:
        while True:
            # consume data
            # This section will be changed to apply the distributed messaging structure.
            # In other words, MQTT will be used.
            # print("Request data")
            mqtt_obj.publish("edge/client/" + client_id + "/data_req", read_size, qos=2)
            condition.wait()
            # print("Consuming data")
            running_time = time.time() - start_time
            if running_time > TEST_TIME:
                break
            time.sleep(0.03)


if __name__ == '__main__':

    # MQTT connection
    message_local_client = mqtt.Client("Client")
    message_local_client.on_connect = on_local_connect
    message_local_client.on_message = on_local_message
    # message_local_client.on_publish = on_local_publish

    message_local_client.connect(MQTT_HOST_ON_EDGE, MQTT_PORT_ON_EDGE, 60)

    message_local_client.loop_start()

    # message_local_client.publish("edge/client/" + client_id + "/data_req", 100)
    # publish.single("edge/client/" + client_id + "/data_req", 100, hostname=MQTT_HOST_ON_EDGE, port=MQTT_PORT_ON_EDGE)

    # Creating threads
    t1 = threading.Thread(target=consume_data_scenario1, args=[message_local_client])
    while not is_running:
        time.sleep(0.005)

    # Wait until threads are completely executed
    t1.join()
    print("Test 1 is done!")

    publish.single("edge/client/" + client_id + "/done_to_test", "done", hostname=MQTT_HOST_ON_EDGE,
                   port=MQTT_PORT_ON_EDGE, qos=2)
    time.sleep(3)

    trimmed_cache_hits_list = cache_hits_list[10:]

    cache_hit_ratio = float(cache_hits_list.count(1)) / len(cache_hits_list) * 100.0
    trimmed_cache_hit_ratio = float(trimmed_cache_hits_list.count(1)) / len(trimmed_cache_hits_list) * 100.0

    print("Cache hit ratio: %s" % cache_hit_ratio)
    print("Cache hit ratio(Trimmed): %s" % trimmed_cache_hit_ratio)

    time_list = [i for i in range(1, len(trimmed_cache_hits_list)+1)]

    # time_sm = np.array(time_list)
    # time_smooth = np.linspace(time_sm.min(), time_sm.max(), 300)

    # feedback_smooth = spline(time_list, percentage_list, time_smooth)
    # Using make_interp_spline to create BSpline

    # Smooth graph
    # helper_x3 = make_interp_spline(time_list, percentage_feedback_list)
    # feedback_smooth = helper_x3(time_smooth)
    #
    # helper_x3 = make_interp_spline(time_list, percentage_output_list)
    # output_smooth = helper_x3(time_smooth)
    #
    # plt.plot(time_smooth, feedback_smooth, marker='o', markersize=3, linestyle='-')
    # plt.plot(time_smooth, output_smooth, marker='o', markersize=3, linestyle='-')
    # plt.plot(time_list, percentage_setpoint_list)

    # # Real value graph
    # plt.plot(time_list, trimmed_cache_hits_list, marker='o', markersize=3, linestyle='None')
    #
    # plt.xlim((1, len(trimmed_cache_hits_list)+1))
    # # plt.ylim((min(percentage_list) - 0.5, max(percentage_list) + 0.5))
    # # plt.ylim(0, 100)
    # plt.xlabel('Round no.')
    # plt.ylabel('Cache hit(Hit:1, Miss:0)')
    # plt.title('Cache hits')
    #
    # # plt.ylim((1 - 0.5, 1 + 0.5))
    #
    # plt.grid(True)
    # plt.show()

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
