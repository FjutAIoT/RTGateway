# -*- coding: UTF-8 -*-
#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import json
import socket
import paho.mqtt.client as mqtt

ALARM_GPIO = 26

broker = '118.24.169.3'
port = 80
deviceId = 'a48d1c6b66629e7ed4f3'
groupId = '9915595732'
# username = ''
# password = ''
topic = 'device/status/' + groupId + '/' + deviceId  		# 发布主题
subTopic = 'device/desired/' + groupId + '/' + deviceId 		# 订阅主题
mqtt_client = mqtt.Client(client_id = deviceId, transport = "websockets")

'''火焰传感器属性值'''
flame = False

'''初始化'''
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # 设置GPIO编码模式
GPIO.setup(ALARM_GPIO, GPIO.IN)

'''连接成功'''
def on_connect(client, userdata, flags, rc):   # 连接后的操作 0为成功
	print("MQTT_pub 连接反馈：" + str(rc))
	mqtt_pub({'flame': flame})

'''MQTT发布消息'''
def mqtt_pub(content):
	rc = 0
	data = {"reported": content}
	data = json.dumps(data).encode('utf-8')
	rc , mid = mqtt_client.publish(topic, data, qos=1)  # 发布消息

def get_data():
	global flame
	tmp = GPIO.input(ALARM_GPIO)
	if tmp == 1:
		tmp = False
	else:
		tmp = True
	if tmp != flame:
		flame = tmp
		mqtt_pub({'flame': flame})

def init():
	mqtt_client.connect(broker, port, 30)  # 设置地址端口与维持心跳
	mqtt_client.on_connect = on_connect  # 连接后的操作
	mqtt_client.loop_start()


