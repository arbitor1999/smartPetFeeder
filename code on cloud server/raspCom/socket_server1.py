from socket_base import Publisher, Reader
from socket_address import host, port_server
import pymysql
P1 = Publisher(host, port_server)
P1.receive_msg()

