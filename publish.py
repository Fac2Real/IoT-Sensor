# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT="a2n7kxevn6fh72-ats.iot.ap-northeast-2.amazonaws.com"
CLIENT_ID = "MSJ"
# MQTT 인증 정보
PATH_TO_CERTIFICATE="C:/lgCns/finalPrj-factoreal/IoTcoreCert/54e5d2549e672108375364398317635c85a2a4082c90ff9378d02a118bd41800-certificate.pem.crt"
PATH_TO_PRIVATE_KEY="C:/lgCns/finalPrj-factoreal/IoTcoreCert/54e5d2549e672108375364398317635c85a2a4082c90ff9378d02a118bd41800-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1="C:/lgCns/finalPrj-factoreal/IoTcoreCert/root.pem"

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