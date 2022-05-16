#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author : wzp
# date : 20220516

import stomp,time,os

queueName = "Queue1.A"


class MyListener(stomp.ConnectionListener):
    # def on_error(self, frame):
    #     print('received an error "%s"' % frame.body)
    #     print(frame.headers)

    def on_message(self, frame):
        print('received a message "%s"' % frame.body)
        print(frame.headers)
        if "end" == frame.body:
            os._exit(0)
        # time.sleep(1)


    def on_send(self,frame):
        print(frame.headers)
        print(frame.body)
        if "receipt" in frame.headers:
            print("-=--------------------")

    # def on_connected(self,frame):
    #     print("connented..")
    #     print(frame)
    #     print(frame.headers)
    #     print(frame.body)
    pass

def send_queue():
    for i in range(1,5):
        send_to_queue(i)

def send_to_queue(id):
    print("---------send message--------")
    msg = """msg{}""".format(id)
    conn.send(body=str(msg),destination=queueName,persistent="true")
    conn.send(body=str(msg), destination=queueName)

def get_queue():
    print("----------read messages-------")

    #subscriber
    conn.subscribe(queueName,id=2,ack="auto")

if __name__ == "__main__":
    conn = stomp.Connection([("192.168.1.227","61613")],reconnect_attempts_max=-1)
    conn.connect(username="admin",passcode="Ebupt#2016",wait=True)
    conn.set_listener("",MyListener())
    send_queue()
    get_queue()
    flag = 0
    while True:
        send_queue()
        time.sleep(1)
        flag+=1
        if flag > 10:
            conn.send(body="end", destination=queueName)
        if not conn.is_connected():
            conn.connect(username="admin",passcode="Ebupt#2016",wait=True)
    conn.disconnect()

