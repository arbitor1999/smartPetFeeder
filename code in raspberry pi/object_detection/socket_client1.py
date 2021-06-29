from socket_base import Publisher, Reader
from socket_address import host, hostname, port_server, target, port_client
target = '106.13.43.30'
C1 = Reader(hostname, port_client)
C1.subscribePublisher(target, port_server)
C1.send_pic('temp_dog.jpg','a')