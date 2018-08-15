import sys

from src.df1.df1_client import Df1Client
from src.df1.models.command_0fa2 import Command0FA2
from src.df1.models.file_type import FileType


def do():
    with Df1Client(src=0x0, dst=0x1) as client:
        client.connect('192.168.5.41', 10232)
        command = client.create_command(Command0FA2, table=0x7, start=0, bytes_to_read=20, file_type=FileType.INTEGER)
        reply = client.send_command(command)
        print(reply.get_data(FileType.INTEGER))


    sys.exit()

do()

import socket



def read_reply():
    data2 = targetHostSocket.recv(4096)
    print(data2)


targetHostSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
targetHostSocket.connect(('192.168.5.41', 10232))
targetHostSocket.send(bytes([0x10, 0x02, 0x01, 0x00, 0x0f, 0x00, 0x1, 0x0, 0xa2, 0x14, 0x07, 0x89, 0x00, 0x00, 0x10, 0x03, 0xd2, 0xb5]))

read_reply()
read_reply()

sys.exit()

while 1:
    # dans le data (la partie entre les blocs de controle) si on voit un 0x10, faut le doubler, mais apres le calcul du CRC seulement.
    # je suppose qu'y faut le sigulariser (?) si on veut valider un CRC ensuite...

    targetHostSocket.send(bytes([0x10, 0x2, 0x1, 0x0, 0x6, 0x0, 0x6b, 0xc3, 0x1, 0x0, 0x0, 0xb, 0x10, 0x3, 0x9e, 0x58]))
    read_reply()
    read_reply()
    targetHostSocket.send(bytes([0x10, 0x06]))
    targetHostSocket.send(bytes([0x10, 0x2, 0x1, 0x0, 0x6, 0x0, 0xca, 0xef, 0x3, 0x10, 0x3, 0x8f, 0x76]))
    read_reply()
    read_reply()
    targetHostSocket.send(bytes([0x10, 0x06]))
