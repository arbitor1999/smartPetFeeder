import time
import paho.mqtt.client as mqtt

    
def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))


def on_message(client, userdata, msg):
    global feed_time
    feed_time = {}
    control = msg.payload.decode()
    print(control)
    f = open('feedtime.txt','w')
    f.write(control)
    f.close()


feed_time = {}

client = mqtt.Client()
#设置用户名和密码
client.username_pw_set("client1", "yshbscjt2021!")
client.on_connect = on_connect
client.on_message = on_message
#client.on_disconnect = on_disconnect
#连接 IP port keepalive
client.connect('106.13.43.30', 1883, 600)
#订阅的 topic
client.subscribe('feed_time', qos=0)

client.loop_forever()
