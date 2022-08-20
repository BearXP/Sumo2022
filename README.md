Sumo 2022
========
*Author: Mark Evans*  
*Date: 20/Aug/2022*

----

- [Sumo 2022](#sumo-2022)
  - [Introduction](#introduction)
  - [Reference Documents:](#reference-documents)
  - [Setup](#setup)
    - [Initial Setup](#initial-setup)
    - [Pico Go](#pico-go)
    - [Belay:](#belay)

## Introduction
For the moment this is just the software for my sumo robot, since I want to sync it between a couple of computers while I'm developing it. The rest of the hardware description will be added as I need to.

## Reference Documents:
| Description | Link |
|----|----|
|Pico Datasheet - CHeck pinouts, etc. | [link](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf) |
| Belay - Use micropython peripheral in your main code | [Hackaday](https://hackaday.com/2022/08/10/your-micropython-board-can-be-your-tinkering-peripheral/) <br /> [GitHub](https://github.com/BrianPugh/belay) |
| Wokwi - Pico simuilator | [link](https://wokwi.com/projects/new/pi-pico) |

## Setup
### Initial Setup
Out of the box my Pico did not appear as a COM port. To fix this I needed to re-install micropython.
1. Hold down the button on the Pico
2. Plug the pico in to the PC - keep holding the button
3. When the device appears as a USB drive you can stop holding the button.
4. Go to the website on the usb key, click on Micropython, download the uf2 file, and drag & drop it on to the usb key
After that you should be done, it should have micropython and it should appear as a COM device.

### Pico Go
VS Code has an extension called Pico Go, which lets you upload & run .py files that you write on your PC.
Seems to work out of the box. A few things to remember:
* You may need to "Control Shift P" > "Pico-Go > Configure Project"
* In the bottom left of VS Code it adds a button called "Pico Disconnect", "Upload", "Download", and "Run", which is nice
* You can also "Control Shift P" > "Pico-Go" to access everything.

### Belay:
This is a library which lets you access the REPL micropython device and run some code there, but use your actual PC for processing.  
I wanted to use this so I can use Jupyter-Notebooks to get used to it.  

First you need to re-install micropython, see above.  
Now that the COM port is available, `pip install belay` and then I can use the [python code](https://belay.readthedocs.io/en/latest/).  
The code is as simple as:
```python
import belay
device = belay.Device("COM7")

@device.task
def set_led(state):
    from machine import Pin
    Pin(25, Pin.OUT).value(state) # Pin 25 is the LED on the board
    return "Hello from the Pico"
newState = set_led(True)
print(f"New State: {newState}")

device._board.close()
```