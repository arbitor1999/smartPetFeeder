import socket
import numpy as np
import cv2
import os
import time
import pymysql

# 服务器
class Publisher(object):

    def __init__(self, host, port, *args, **kwargs):
        # 服务器基本配置
        self.port = port  # 端口  0--1024 为系统保留
        self.host = host
        self.address = (host, port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.address)
        self.server.listen(5)

        # 保存信息的文件位置
        self.feed_time = '/var/www/html/set_feed_time/setting.txt'
        self.temperature = '/home/info/temperature/'
        self.eat = '/home/info/eat/'

        # 存储硬件的网络地址
        self.clients = {}

        # 接收信息后的处理函数
        self.switch = {'status': self.receive_status,
                       'temp': self.receive_temp,
                       'warning': self.receive_warn,
                       'pic': self.receive_pic}
        # address = open('address.txt', 'r')
        # for i in address.readlines():
        #    add = i.split(' ')
        #    self.clients[add[0]]=add[1]
        # address.close()

    def receive_msg(self):
        while True:
            conn, addr = self.server.accept()
            if conn:
                conn.send("msg received!".encode())
                client_address = conn.recv(1024).decode()   # 硬件网络地址接收
                print('hardware address', client_address)
                self.clients[client_address.split(' ')[0]] = conn
                msg = conn.recv(1024).decode()         # 信息类别接收
                print('msg', msg)
                info = self.switch.get(msg, self.receive_default)(conn)
                if info == 'wrong':
                    print(info)
        return info

    def receive_default(self, blank):
        print('no such case!')
        return 'wrong'

    def receive_status(self,conn):
        info = conn.recv(1024).decode()  # 获得状态信息
        print('info', info)
        infos = info.split(' ')
        f = open(self.eat + infos[0] + '.txt', 'a')
        f.write(infos[1] + '@' + infos[2] + "\n")
        f.close()

    def receive_temp(self, conn):
        info = conn.recv(1024).decode()  # 获得温度信息
        print('info', info)
        infos = info.split(' ')
        f = open(self.temperature+infos[0]+'.txt', 'a')
        f.write(infos[1]+'@'+infos[2]+"\n")
        f.close()

    def receive_warn(self, conn):
        info = conn.recv(1024).decode()  # 获得状态信息
        print('info', info)
        infos = info.split(' ')
        date = infos[0]
        time = infos[1]
        warn_label = infos[2]
        # 打开数据库连接
        db = pymysql.connect(host="localhost", user="root", password="yshbscjt2021!", db='petfeeder')
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()
        sql = "INSERT INTO %s(warn_date, warn_time, warn_label)\
                         VALUES (%s,%s,%s)" % \
              ('`1_warning`', '\''+date+'\'', '\''+time+'\'', '\''+warn_label+'\'')
        print(sql)
        #  执行 SQL 查询
        cursor.execute(sql)
        db.commit()
        # 关闭数据库连接
        db.close()

    def receive_pic(self, conn):
        info = conn.recv(1024).decode()  # 获得图片信息
        print('info', info)
        infos = info.split(' ')
        string_data = self.recvall(conn, int(infos[2]))  # 根据获得的文件长度，获取图片文件
        data = np.frombuffer(string_data, np.uint8)  # 将获取到的字符流数据转换成1维数组
        decode_img = cv2.imdecode(data, cv2.IMREAD_COLOR)  # 将数组解码成图像
        cv2.imwrite('/var/www/html/images/'+str(infos[0])+str(infos[1])+'.jpg', decode_img)  # 保存图片
        self.pic_db(infos)  # 图片信息存入数据库
        # conn.send("received！".encode())
        return infos

    def pic_db(self, info):
        # 打开数据库连接
        db = pymysql.connect(host="localhost", user="root", password="yshbscjt2021!", db='petfeeder')
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()
        sql = "INSERT INTO %s(pic_route, pic_time, pic_label)\
                 VALUES (%s,%s,%s)"%\
              ('`1_petpic`', '\'../images/'+info[0]+info[1]+'.jpg\'', '\''+info[0]+'\'', '\''+info[3]+'\'')
        print(sql)
        #  执行 SQL 查询
        cursor.execute(sql)
        db.commit()
        # 关闭数据库连接
        db.close()

    # 图片信息读取函数
    def recvall(self, conn, count):
        buf = b''  # buf是一个byte类型
        while count:
            # 接受TCP套接字的数据。数据以字符串形式返回，count指定要接收的最大数据量.
            newbuf = conn.recv(count)
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    # 发布信息函数，abandon
    def notify(self, target):
        print('notify')
        # 从文件中读取喂食信息
        fr = open(self.feed_time, "r")
        feed_times = []
        for i in fr.readlines():
            feed_times.append(i)
        fr.close()
        feed_times = ''.join(feed_times)
        print(feed_times)
        client_conn = self.clients[target]
        print('client')
        client_conn.send(feed_times.encode())
        #self.publish.close()


# 智能硬件
class Reader(object):

    def __init__(self, host, port, *args, **kwargs):
        # Reader 的初始化方法
        self.client = socket.socket()
        self.host = host
        self.port = port
        self.address = (self.host, self.port)
        self.server = None
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 15]

    def subscribePublisher(self, host, port, *args, **kwargs):
        # Reader向Publisher订阅
        self.client.connect((host, port))
        self.client.send((str(self.host)+' '+str(self.port)).encode())
        # 返回订阅成功信息
        print(self.client.recv(100).decode())

    def send_pic(self, pic_route, label):
        print("sending picture")
        img = cv2.imread(pic_route)
        result, imgencode = cv2.imencode('.jpg', img, self.encode_param)
        data = np.array(imgencode)
        # 将numpy矩阵转换成字符形式，以便在网络中传输
        string_data = data.tostring()
        self.client.send("pic".encode())
        info = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+" "+str(len(string_data))+" "+label
        time.sleep(0.1)
        self.client.send(info.encode(encoding='UTF-8'))
        time.sleep(0.1)
        print('pic_len', len(string_data))
        print('start sending!')
        self.client.send(string_data)
        print('end sending!')

    def send_temperature(self, temp):
        print('sending temperature')
        self.client.send("temp".encode())
        time.sleep(0.1)
        info = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+" "+str(temp)
        self.client.send(info.encode())
        print('end sending temperature')

    def send_warning(self,warn_label):
        print('sending warning')
        self.client.send('warning'.encode())
        time.sleep(0.1)
        info = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+" "+str(warn_label)
        self.client.send(info.encode())
        print('end sending warning')

    def send_eat_status(self, amount):
        print('sending eating status')
        self.client.send('status'.encode())
        time.sleep(0.1)
        info = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+" "+str(amount)
        self.client.send(info.encode())
        print('end sending status')

    def receive_server(self):
        self.client.send('waitingfordata'.encode())
        while True:
            information = self.client.recv(1024).decode()
            if information != '':
                with open('time.txt' 'w') as f:
                    f.write(information)

            #conn, addr = self.client.accept()
            #if conn:
            #    information = conn.recv(10240).decode()
            #    print(information)
            #    conn.close()
