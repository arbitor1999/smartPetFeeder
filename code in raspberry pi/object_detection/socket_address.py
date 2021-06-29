port_server = 5002
port_server2 = 5005
port_client = 5003
port_client2 = 5004
import socket
# https://www.jianshu.com/p/ba8abad56ba9 0.0.0.0和127.0.0.1区别
host = 'instance-5l34b2qz'
target = '106.13.43.30'
#client = socket.socket()
#client.connect((target, port_server))
hostname = socket.gethostname()
ipaddr = socket.gethostbyname(hostname)
print(ipaddr)