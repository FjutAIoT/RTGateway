# -*- coding: UTF-8 -*-
#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import json
import socket
import paho.mqtt.client as mqtt
import Adafruit_DHT

sensor = Adafruit_DHT.DHT11

DHT11_GPIO = 27

broker = '118.24.169.3'
port = 80
deviceId = '8ee7c0625612d94173cc'
groupId = '9915595732'
# username = ''
# password = ''
topic = 'device/status/' + groupId + '/' + deviceId  		# 发布主题
subTopic = 'device/desired/' + groupId + '/' + deviceId 		# 订阅主题
mqtt_client = mqtt.Client(client_id = deviceId, transport = "websockets")

humidity, temp = Adafruit_DHT.read_retry(sensor, DHT11_GPIO)


'''初始化'''
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # 设置GPIO编码模式
GPIO.setup(DHT11_GPIO, GPIO.IN)

'''连接成功'''
def on_connect(client, userdata, flags, rc):   # 连接后的操作 0为成功
    print("MQTT_pub 连接反馈：" + str(rc))
    mqtt_pub({"humidity": humidity, "temp": temp})

'''MQTT发布消息'''
def mqtt_pub(content):
    rc = 0
    data = {"reported": content,"type": "sensor"}
    data = json.dumps(data).encode('utf-8')
    rc , mid = mqtt_client.publish(topic, data, qos=1)  # 发布消息

'''获取温湿度发送'''
def get_data():
    global humidity, temp
    humidity, temp = Adafruit_DHT.read_retry(sensor, DHT11_GPIO)
    if humidity is not None and temp is not None:
        print (humidity, temp)
        mqtt_pub({"humidity": humidity, "temp": temp})

def init():
    mqtt_client.connect(broker, port, 30)  # 设置地址端口与维持心跳
    mqtt_client.on_connect = on_connect  # 连接后的操作
    mqtt_client.loop_start()

