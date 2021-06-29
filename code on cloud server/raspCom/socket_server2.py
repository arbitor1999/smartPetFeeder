from socket_base import Publisher, Reader
from socket_address import host, port_server2

P2 = Publisher("./" + 'data.txt', host, port_server2)
P2.receive_msg()
P2.notify('LAPTOP-8H60EICM')