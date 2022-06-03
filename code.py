#import os
import gc
import time
import busio
import digitalio
import board
import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

gc.collect()

WIDTH = 128
HEIGHT = 64
CENTER_X = int(WIDTH/2)
CENTER_Y = int(HEIGHT/2)

displayio.release_displays()

SDA = board.GP0
SCL = board.GP1
i2c = busio.I2C(SCL, SDA)

if(i2c.try_lock()):
    i2c.unlock()


display_bus = displayio.I2CDisplay(i2c, device_address=60)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

time.sleep(0.5)

####

buttonOne = digitalio.DigitalInOut(board.GP17)
buttonOne.direction = digitalio.Direction.OUTPUT

buttonTwo = digitalio.DigitalInOut(board.GP16)
buttonTwo.direction = digitalio.Direction.OUTPUT

buttonThree = digitalio.DigitalInOut(board.GP18)
buttonThree.direction = digitalio.Direction.OUTPUT

buttonFour = digitalio.DigitalInOut(board.GP19)
buttonFour.direction = digitalio.Direction.OUTPUT

buttonFive = digitalio.DigitalInOut(board.GP20)
buttonFive.direction = digitalio.Direction.OUTPUT

# Classes ########

class keyMacroGroup:
    def __init__(self, header, keyMacroList):
        self.header = header
        self.keyMacroList = keyMacroList

class keyMacro:
    def __init__(self, label, action):
        self.label = label
        self.action = action

# Set up a keyboard device.
kbd = Keyboard(usb_hid.devices)

layout = KeyboardLayoutUS(kbd)

def printButtonPress(text):
    global displayMenu
    global displayio
    global display
    global splash
    
    color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = 0x000000  # Black

    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)
    
    time.sleep(0.02)
            
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=0, y=4)
    splash.append(text_area)
    
    time.sleep(0.02)

    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)
    
    displayMenu = 1

    splash = displayio.Group()
    display.show(splash)

    time.sleep(0.02)

def displayMacroList():
    global displayMenu
    global macroDictionary
    global displayio
    global display
    
    if (displayMenu):

        text_area = label.Label(terminalio.FONT, text=macroDictionary[currentMacroPage].header, color=0xFFFF00, x=0, y=(0 * displayLineHeight) + 4)
        splash.append(text_area)

        for index in macroDictionary[currentMacroPage].keyMacroList:
            macroText = str(index + 1) + ") " + macroDictionary[currentMacroPage].keyMacroList[index].label
                
            text_area = label.Label(terminalio.FONT, text=macroText, color=0xFFFF00, x=0, y=(((index + 1) * displayLineHeight) + 4))
            splash.append(text_area)
            
            displayMenu = 0
            
        gc.collect()
            

####

splash = displayio.Group()
display.show(splash)

### MACRO FUNCTIONS

windowsMode = 0

if (windowsMode):
    Keycode.COMMAND = Keycode.CONTROL

# Google Meet

def googleMeetToggleMic():
    global kbd
    kbd.send(Keycode.COMMAND, Keycode.D)

def googleMeetToggleCam():
    global kbd
    kbd.send(Keycode.COMMAND, Keycode.E)

def googleMeetRaiseHand():
    global kbd
    kbd.press(Keycode.COMMAND)
    kbd.press(0xE0)
    kbd.press(Keycode.H)
    kbd.release_all()

def googleMeetHangUp():
    global kbd
    kbd.send(Keycode.ALT, Keycode.LEFT_ARROW)

# VS Code

def vsCodeBookmarkToggle():
    global kbd
    kbd.send(Keycode.COMMAND, Keycode.ALT, Keycode.K)

def vsCodeBookmarkListAll():
    global kbd
    kbd.send(Keycode.COMMAND, Keycode.SHIFT, Keycode.ALT, Keycode.K)

def vsCodeBookmarkPrevious():
    global kbd
    kbd.send(Keycode.COMMAND, Keycode.ALT, Keycode.J)  
    
def vsCodeBookmarkNext():
    global kbd
    kbd.send(Keycode.COMMAND, Keycode.ALT, Keycode.L)

# Discord

def discordServerPrevious():
    global kbd
    kbd.send(Keycode.COMMAND, Keycode.ALT, Keycode.UP_ARROW)  

def discordServerNext():
    global kbd
    kbd.send(Keycode.COMMAND, Keycode.ALT, Keycode.DOWN_ARROW)  

def discordChannelPrevious():
    global kbd
    kbd.send(Keycode.ALT, Keycode.UP_ARROW)  

def discordChannelNext():
    global kbd
    kbd.send(Keycode.ALT, Keycode.DOWN_ARROW)  

### RUNNING CODE

displayMenu = 1
currentMacroPage = 0
displayLineHeight = 12

macroDictionary = {
    0: keyMacroGroup(
        'Google Meet', 
        {
            0: keyMacro('Microphone', googleMeetToggleMic),
            1: keyMacro('Camera', googleMeetToggleCam),
            2: keyMacro('Raise Hand', googleMeetRaiseHand),
            3: keyMacro('Hang Up', googleMeetHangUp)
        }
    ),
    1: keyMacroGroup(
        'VS Code: Bookmarks', 
        {
            0: keyMacro('Toggle', vsCodeBookmarkToggle),
            1: keyMacro('List All', vsCodeBookmarkListAll),
            2: keyMacro('Previous', vsCodeBookmarkPrevious),
            3: keyMacro('Next', vsCodeBookmarkNext)
        }
    ),
    2: keyMacroGroup(
        'Discord: Servers', 
        {
            0: keyMacro('Server <<', discordServerPrevious),
            1: keyMacro('Server >>', discordServerNext),
            2: keyMacro('Channel <<', discordChannelPrevious),
            3: keyMacro('Channel >>', discordChannelNext)
        }
    )
}

while True:
    if buttonOne.value:
        macroDictionary[currentMacroPage].keyMacroList[0].action()
        time.sleep(0.2)

    elif buttonTwo.value:
        macroDictionary[currentMacroPage].keyMacroList[1].action()
        time.sleep(0.2)

    elif buttonThree.value:
        macroDictionary[currentMacroPage].keyMacroList[2].action()
        time.sleep(0.2)

    elif buttonFour.value:
        macroDictionary[currentMacroPage].keyMacroList[3].action()
        time.sleep(0.2)

    elif buttonFive.value:
        # Debugging memory
        # printButtonPress(str(gc.mem_free()))
        printButtonPress('')
        
        if currentMacroPage == (len(macroDictionary) - 1):
            currentMacroPage = 0
        else:
            currentMacroPage = currentMacroPage + 1
        time.sleep(0.2)

    else:
        # Dispay the list of macros for the current page
        displayMacroList()

        time.sleep(0.01)

        
        

