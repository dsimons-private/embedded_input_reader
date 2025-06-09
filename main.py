"""
Project: Embedded Input Reader Project,
Udacity Embedded Systems Fundamentals Nanodegree

Date: 2025-05-23

Important Note:
The code body is adopted from Udacity Embedded Systems Fundamentals Nanodegree
Chapter 4 and modified for two chained 2-1 MUX's
"""

import machine
import time
from utime import sleep

BUTTON_COUNT = 3
LED_COUNT = 9
INPUT_COUNT = 4
BUTTON_START_ID = 16
LED_GPIO_START = 7

last_button_time_stamp = 0
key_presses = []

INACTIVITY_TIME_MS = 3000  # 3s inactivity

# Extract the numeric pin id from the passed in Pin instance
def PinId(pin):
    # Pin(GPIO17, mode=IN, pull=PULL_DOWN)
    return int(str(pin)[8:10].rstrip(","))

def interrupt_callback(pin):
    global last_button_time_stamp

    cur_button_ts = time.ticks_ms()
    button_press_delta = cur_button_ts - last_button_time_stamp
    if button_press_delta > 200:
        last_button_time_stamp = cur_button_ts
        key_presses.append(pin)
        # Call the PinId method to get the numeric pin value
        print(f'key press: {PinId(pin) - BUTTON_START_ID}')

def inactivity_time_clear_key_presses():
    # if inactivity time elapsed, clear key_presses list    
    global key_presses
    global last_button_time_stamp

    if len(key_presses) != 0 and time.ticks_ms() - last_button_time_stamp > INACTIVITY_TIME_MS:
        key_presses = []
        print('Note: Due to inactivity your key presses have been cleared')

def main():
    global key_presses
    global last_button_time_stamp
    PASSCODE_LENGTH = 0

    # A tiny sleep to allow the first print to be displayed
    sleep(0.01)
    print('Program starting')

    # For MUX input set pin to IN mode
    mux_in = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_DOWN)
    
    # To control MUX select lines set pins to OUT mode
    s1 = machine.Pin(28, machine.Pin.OUT)
    s0 = machine.Pin(27, machine.Pin.OUT)

    buttons = []
    for btn_idx in range(0, BUTTON_COUNT):
        # assign button the right pin
        buttons.append(machine.Pin(BUTTON_START_ID + btn_idx, machine.Pin.IN, machine.Pin.PULL_DOWN))
        # implement interrupt routine
        buttons[-1].irq(trigger=machine.Pin.IRQ_FALLING, handler=interrupt_callback)

    # correct passcode is "021"
    PASS_CODE = [buttons[0], buttons[2], buttons[1]]
    PASSCODE_LENGTH = len(PASS_CODE)

    # assign LED pins
    out_pins = []
    for out_id in range(0, LED_COUNT):
        out_pins.append(machine.Pin(LED_GPIO_START + out_id, machine.Pin.OUT))

    last_dev = -1
    while True:
        binary_code = 0
        for selector_val in range(INPUT_COUNT):
            s0.value(selector_val % 2)
            s1.value(selector_val // 2)
            sleep(0.02)
            binary_code += (pow(2, selector_val) * mux_in.value())

        if last_dev != binary_code:
            last_dev = binary_code
            print(f'selected output: {last_dev}')
        sleep(0.1)

        if len(key_presses) >= PASSCODE_LENGTH:
            if key_presses[:PASSCODE_LENGTH] == PASS_CODE:
                print('correct passcode')
                if binary_code < LED_COUNT:
                    print(f'toggling: {binary_code}')
                    out_pins[binary_code].toggle()
                else:
                    print(f'invalid output: {binary_code}, ' + \
                    f'valid range: 0-{len(out_pins) - 1}, doing nothing')
            else:
                print('wrong passcode')

            key_presses = key_presses[PASSCODE_LENGTH:]
        
        # add inactivity methode to main code
        inactivity_time_clear_key_presses()

#
# ******* MAIN ********
#
if __name__ == "__main__":
    main()