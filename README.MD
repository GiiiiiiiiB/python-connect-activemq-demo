下载地址：
```wget https://dlcdn.apache.org//activemq/5.16.5/apache-activemq-5.16.5-bin.tar.gz --no-check-certificate```

额外需要java下载
```https://www.oracle.com/java/technologies/downloads/```


```rpm -ivh https://download.oracle.com/java/18/latest/jdk-18_linux-x64_bin.rpm```


python库下载
```pip3 install stomp.py```


启动：
相应的bin目录下启动
```activemq start```




tips :
activemq queue和topic的不同：
queue 一对一，不消费会存储，如果持久化，send()如果队列不存在会创建一个。
topic  一堆多，无状态，不消费会丢失

第一次测试：
生成5w条数据，重启后消失，kahadb正常，配置正常，broswer里面点开发现消息为未持久化状态。
```#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author : wzp
# date : 20220516

import stomp

queueName = "Queue1.A"

def send_to_queue():
    print("---------send message--------")
    body = """msg1"""

    conn.send(body=str(body),destination=queueName)


if __name__ == "__main__":
    conn = stomp.Connection([("192.168.1.227","61613")])
    conn.connect(username="admin",passcode="Ebupt#2016",wait=True)
    for i in range(1,50000):
        send_to_queue()
```

查看activemq默认配置正常，查询还需要在send()时添加 persistent=“true”
keyword_headers: any additional headers the broker requires，确实是添加到headers里面
过期策略确实可以按这个方式添加，还有过期时间，但是官方没有给出demo
Finally, STOMP servers MAY use additional headers to give access to features like persistency or expiration. Consult your server's documentation for details.
```https://stomp.github.io/stomp-specification-1.2.html#SEND```
另外在一次sender结束后，会在frame.headers 放一条{'receipt': '7e234e42-710f-4f37-a06a-8f03283bb008'}
看源码这个在baseconnection中可以自定义


重启后会丢失 non persistent的queue消息，已通过验证。
测试最终版, 消费者会fork出一个线程
```#!/usr/bin/env python
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
```


测试意外关闭activemq，重启后自动重连，如果不设置 reconnect_attempts_max，默认值=3 ，在connect里面定义


正常结束关闭


参考：
https://blog.csdn.net/qq_36059561/article/details/104286702  持久化 java
https://blog.csdn.net/weixin_41806489/article/details/104998760 python
https://blog.csdn.net/qq_36059561/article/details/104286702  也可以在header里面传入persistent 未测试，但应该是可行的，因为在参数里面加了persistent参数后在header里面也增加了