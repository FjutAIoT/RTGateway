# -*- coding: UTF-8 -*-
#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import json
import socket
import paho.mqtt.client as mqtt

R_GPIO = 22
G_GPIO = 23
B_GPIO = 24

broker = '118.24.169.3'
port = 80
deviceId = '729461c2f9b239db283f'
groupId = '9915595732'
# username = ''
# password = ''
topic = 'device/status/' + groupId + '/' + deviceId  		# 发布主题
subTopic = 'device/desired/' + groupId + '/' + deviceId 		# 订阅主题
mqtt_client = mqtt.Client(client_id = deviceId, transport = "websockets")

'''LED灯属性值'''
switch = False
luminance = 100
color = 0

'''初始化'''
# GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # 设置GPIO编码模式
GPIO.setup(R_GPIO, GPIO.OUT)
GPIO.setup(G_GPIO, GPIO.OUT)
GPIO.setup(B_GPIO, GPIO.OUT)

pwm_R = GPIO.PWM(R_GPIO, 80)
pwm_G = GPIO.PWM(G_GPIO, 80)
pwm_B = GPIO.PWM(B_GPIO, 80)

pwm_R.start(0)
pwm_G.start(0)
pwm_B.start(0)


'''连接成功'''
def on_connect(client, userdata, flags, rc):   # 连接后的操作 0为成功
    print("MQTT_pub 连接反馈：" + str(rc))
    mqtt_pub({'switch': switch})

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

'''操作LED灯 '''
def Fan_desired_handle(data):
    global switch,luminance,color
    if data.__contains__('switch') == True:
        switch = data['switch']
    if data.__contains__('luminance') == True:
        luminance = data['luminance']
    if data.__contains__('color') == True:
        color = data['color']
    if switch == True:
        if color == 0:
            pwm_R.ChangeDutyCycle(luminance)
            pwm_G.ChangeDutyCycle(luminance)
            pwm_B.ChangeDutyCycle(luminance)
        elif color == 1:
            pwm_R.ChangeDutyCycle(luminance)
            pwm_G.ChangeDutyCycle(0)
            pwm_B.ChangeDutyCycle(0)
        elif color == 2:
            pwm_R.ChangeDutyCycle(0)
            pwm_G.ChangeDutyCycle(luminance)
            pwm_B.ChangeDutyCycle(0)
        elif color == 3:
            pwm_R.ChangeDutyCycle(0)
            pwm_G.ChangeDutyCycle(0)
            pwm_B.ChangeDutyCycle(luminance)
    else:
        pwm_R.ChangeDutyCycle(0)
        pwm_G.ChangeDutyCycle(0)
        pwm_B.ChangeDutyCycle(0)

    mqtt_pub(data)

def init():
    mqtt_client.connect(broker, port, 30)  # 设置地址端口与维持心跳
    mqtt_client.on_connect = on_connect  # 连接后的操作
    mqtt_client.loop_start()
    on_subscribe()
