from socket_base import Publisher, Reader
from socket_address import hostname, target, port_server2, port_client2

C1 = Reader(hostname, 5003)
C1.subscribePublisher(target, port_server2)
C1.receive_server()