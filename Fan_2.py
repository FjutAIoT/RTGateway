# -*- coding: UTF-8 -*-
#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import json
import socket
import paho.mqtt.client as mqtt

FAN_GPIO = 13

broker = '118.24.169.3'
port = 80
deviceId = '80a5a14bacb6ca3d43a2'
groupId = '9915595732'
# username = ''
# password = ''
topic = 'device/status/' + groupId + '/' + deviceId  		# 发布主题
subTopic = 'device/desired/' + groupId + '/' + deviceId 		# 订阅主题
mqtt_client = mqtt.Client(client_id = deviceId, transport = "websockets")

'''风扇属性值'''
switch = False
speed = 1

'''初始化'''
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # 设置GPIO编码模式
GPIO.setup(FAN_GPIO, GPIO.OUT)
# pwm = GPIO.PWM(FAN_GPIO, 50)
# pwm.start(100)
# time.sleep(2)
# pwm.stop()



'''连接成功'''
def on_connect(client, userdata, flags, rc):   # 连接后的操作 0为成功
    print("MQTT_pub 连接反馈：" + str(rc))
    mqtt_pub({'switch': switch, 'speed': speed})

'''MQTT发布消息'''
def mqtt_pub(content):
    rc = 0
    data = {"reported": content}
    data = json.dumps(data).encode('utf-8')
    rc , mid = mqtt_client.publish(topic, data, qos=1)  # 发布消息

'''MQTT订阅消息'''
def on_subscribe():
    mqtt_client.subscribe(subTopic, 1)
    mqtt_client.on_message = on_message # 消息到来处理函数

'''消息处理函数'''
def on_message(lient, userdata, msg):
    data = msg.payload.decode('utf-8')
    data = json.loads(data)
    # print (data['desired'])
    Fan_desired_handle(data['desired'])

'''关闭释放资源'''
def destroy():
    GPIO.cleanup()               #释放资源

'''操作风扇 '''
def Fan_desired_handle(data):
    global switch, speed
    value = 40
    if data.__contains__('speed') == True:
        speed = data["speed"]
    if data.__contains__('switch') == True:
        switch = data['switch']

    if speed == 1:
        value = 40
    elif speed == 2:
        value = 70
    elif speed == 3:
        value = 100

    if switch == True:
        GPIO.output(FAN_GPIO, 0)
    else:
        GPIO.output(FAN_GPIO, 1)

    mqtt_pub(data)

def init():
    mqtt_client.connect(broker, port, 30)  # 设置地址端口与维持心跳
    mqtt_client.on_connect = on_connect  # 连接后的操作
    mqtt_client.loop_start()
    on_subscribe()