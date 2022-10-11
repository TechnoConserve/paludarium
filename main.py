import threading
import time

from gpiozero import DigitalInputDevice, DigitalOutputDevice, LED
import keyboard

led_zero = LED(17)  # Used to signal Adafruit Bluefruit Feather M0 to turn on/off LED strip
led_one = LED(27)
led_two = LED(22)

# Initial values set to True so relays default to OFF
relay_one = DigitalOutputDevice(23, initial_value=True)  # Paludarium water pump
relay_two = DigitalOutputDevice(24, initial_value=True)  # Main paludarium light
relay_three = DigitalOutputDevice(25, initial_value=True)  # Fogger/mister
relay_four = DigitalOutputDevice(26, initial_value=True)  # 5v fan for cooling paludarium

fan_signal = DigitalInputDevice(5)  # Reads from Bluefruit Feather M0


def switch_pin(output):
    if output.is_active:
        output.off()
    else:
        output.on()


def handle_fan_signal():
    while True:
        if fan_signal.value == 1:  # Signal that fan should be on
            relay_four.on()  # Turn on the fan
            relay_two.off()  # Turn off the light to reduce heat
        else:
            relay_four.off()

        time.sleep(300)


def main():
    fan_monitor_thread = threading.Thread(target=handle_fan_signal)
    fan_monitor_thread.start()
    keyboard.add_hotkey('0', switch_pin, (led_zero,))
    keyboard.add_hotkey('1', switch_pin, (led_one,))
    keyboard.add_hotkey('2', switch_pin, (led_two,))
    keyboard.add_hotkey('3', switch_pin, (relay_one,))
    keyboard.add_hotkey('4', switch_pin, (relay_two,))
    keyboard.add_hotkey('5', switch_pin, (relay_three,))
    keyboard.add_hotkey('6', switch_pin, (relay_four,))
    keyboard.wait()


if __name__ == '__main__':
    main()
