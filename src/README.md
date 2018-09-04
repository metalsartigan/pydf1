# DF1 #

A very basic Allen Bradley DF1 protocol implementation in Python.

### How to use ###
```
from df1.df1_client import Df1Client
from df1.commands import Command0FAA, Command0FA2
from df1.file_type import FileType

with Df1Client(src=0x0, dst=0x1) as client:
    client.connect('192.168.0.32', 10232)
    command = client.create_command(Command0FA2, table=43, start=245, bytes_to_read=10, file_type=FileType.INTEGER)
    reply = client.send_command(command)
    print(reply.get_data(FileType.INTEGER))
```
