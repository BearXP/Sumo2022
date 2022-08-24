import belay
from time import sleep

device = belay.Device("COM5")

@device.task
def count():
    i = 0
    while True:
        i += 1
        yield i


for index in count():
    print(index)