# -*- coding: utf-8 -*-

import sys

from df1.df1_client import Df1Client
from df1.commands import Command0FAA, Command0FA2, Command0FABSingleBit
from df1.file_type import FileType


def do():
    with Df1Client(src=0x0, dst=0x1) as client:
        client.connect('192.168.5.41', 10232)
        for __ in range(5):
            command = client.create_command(Command0FABSingleBit, table=7, file_type=FileType.INTEGER, start=30, bit_position=0, bit_value=True)
            reply = client.send_command(command)
            print('write:', reply)
    
            command = client.create_command(Command0FA2, bytes_to_read=2, table=7, file_type=FileType.INTEGER, start=30)
            reply = client.send_command(command)
            bts = reply.get_bytes()
            bts = [hex(c) for c in bts]
            print('read:', bts)
            print()

        #command = client.create_command(Command0FA2, table=43, start=50, bytes_to_read=100, file_type=FileType.INTEGER)
        #reply = client.send_command(command)
        #print(reply.get_data(FileType.INTEGER))

    sys.exit()


def write():
    with Df1Client(src=0x0, dst=0x1) as client:
        client.connect('192.168.5.41', 10232)
        data = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        command = client.create_command(Command0FAA, table=45, start=40, file_type=FileType.INTEGER, data_to_write=data)
        print([hex(c)[2:] for c in command.get_bytes()])
        reply = client.send_command(command)
        pass

#write()

do()


sys.exit()

import socket, select


targetHostSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
targetHostSocket.connect(('192.168.5.41', 10232))

def read_reply():
    in_sockets, out_sockets, ex = select.select([targetHostSocket], [], [], 1)  # timeout = 1
    if in_sockets:
        data2 = targetHostSocket.recv(4096)
        print(1, [hex(c)[2:] for c in bytearray(data2)])


#targetHostSocket.send(bytes([0x10, 0x02, 0x01, 0x00, 0x0f, 0x00, 0x1, 0x0, 0xa2, 0x14, 0x07, 0x89, 0x00, 0x00, 0x10, 0x03, 0xd2, 0xb5]))
targetHostSocket.send(bytearray([16, 2, 1, 0, 15, 0, 196, 53, 162, 2, 10, 137, 0, 0, 16, 3, 227, 15]))
targetHostSocket.send(bytearray([0x10, 0x2, 0x1, 0x0, 0xf, 0x0, 0x16, 0x59, 0xaa, 0x50, 0x28, 0x89, 0x0, 0x0, 0x4e, 0x0, 0xfe, 0x4, 0xae, 0x9, 0x5e, 0xe, 0xe, 0x13, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x5a, 0x17, 0x10, 0x3, 0xc9, 0xc6]))

read_reply()
read_reply()
read_reply()
read_reply()

sys.exit()

while 1:
    targetHostSocket.send(bytearray([0x10, 0x2, 0x1, 0x0, 0x6, 0x0, 0x6b, 0xc3, 0x1, 0x0, 0x0, 0xb, 0x10, 0x3, 0x9e, 0x58]))
    read_reply()
    read_reply()
    targetHostSocket.send(bytearray([0x10, 0x06]))
    targetHostSocket.send(bytearray([0x10, 0x2, 0x1, 0x0, 0x6, 0x0, 0xca, 0xef, 0x3, 0x10, 0x3, 0x8f, 0x76]))
    read_reply()
    read_reply()
    targetHostSocket.send(bytearray([0x10, 0x06]))
