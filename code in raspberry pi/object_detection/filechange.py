import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


client = mqtt.Client()
# 设置用户名和密码
client.username_pw_set("server1", "yshbscjt2021!")
client.on_connect = on_connect
client.on_message = on_message
# 连接 IP port keepalive
client.connect('106.13.43.30', 1883, 600)
# 发布 topic 内容
client.publish('test', payload='amazing', qos=0)


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print('modify')
        if event.src_path == "/var/www/html/set_feed_time/setting.txt":      #监控指定文件内容、权限等变化
            f = open(event.src_path,'r')
            data = f.read()
            f.close()
            global client
            client.publish('feed_time', payload=data.encode(), qos=0)
            print("set feed time changed!")


path =  "/var/www/html/set_feed_time/setting.txt"
event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
