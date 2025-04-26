# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json

MESSAGE = "Hello World"
TOPIC = "test/testing"
RANGE = 20
class AwsMQTTPublish:
    def __init__(self):
        self.__setup__()
        pass
    def __setup__(self):
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
        # MQTT 관련 설정들
        self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
                    endpoint=ENDPOINT,
                    cert_filepath=PATH_TO_CERTIFICATE,
                    pri_key_filepath=PATH_TO_PRIVATE_KEY,
                    client_bootstrap=client_bootstrap,
                    ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
                    client_id=CLIENT_ID,
                    clean_session=False,
                    keep_alive_secs=6
                    )
        print("Connecting to {} with client ID '{}'...".format(
                ENDPOINT, CLIENT_ID))
        connect_future = self.mqtt_connection.connect()
        connect_future.result()
        print("Connected!") 

    def publish(self , topic, payload, qos): 
        print('Start One Published')
        self.mqtt_connection.publish(
            topic = topic, 
            payload = payload, 
            qos = qos)
        print(f"Published: {payload} to topic: {topic}")
        print('End One Published')

    def __del__(self):
        disconnect_future = self.mqtt_connection.disconnect()
        print("Check disconnect", disconnect_future.result())
        
        
        

# Publish message to server desired number of times.
# print('Begin Publish')
# for i in range (RANGE):
#     data = "{} [{}]".format(MESSAGE, i+1)
#     message = {"message" : data}
#     mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
#     print("Published: '" + json.dumps(message) + "' to the topic: " + "'test/testing'")
#     t.sleep(0.1)
# print('Publish End')
# disconnect_future = mqtt_connection.disconnect()
# disconnect_future.result()