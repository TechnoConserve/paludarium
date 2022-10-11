import logging
import threading
import time

from gpiozero import DigitalInputDevice, DigitalOutputDevice, LED
import keyboard

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

led_zero = LED(17)  # Used to signal Adafruit Bluefruit Feather M0 to turn on/off LED strip
led_one = LED(27)
led_two = LED(22)

# Initial values set to True so relays default to OFF
relay_one = DigitalOutputDevice(23, initial_value=True)  # 5v fan for cooling paludarium
relay_two = DigitalOutputDevice(24, initial_value=True)  # Fogger/mister
relay_three = DigitalOutputDevice(25, initial_value=True)  # Main paludarium light
relay_four = DigitalOutputDevice(26, initial_value=True)  # Water pump

fan_signal = DigitalInputDevice(5)  # Reads from Bluefruit Feather M0


def switch_pin(output: DigitalOutputDevice):
    logging.debug('Keyboard input received!')
    if output.is_active:
        logging.info(f'Turning off pin {output.pin}')
        output.off()
    else:
        logging.info(f'Turning on pin {output.pin}')
        output.on()


def handle_fan_signal():
    logging.info('Handling fan signals...')
    while True:
        logging.debug('Checking fan signal pin...')
        if fan_signal.value == 1:  # Signal that fan should be on
            logging.info('Turning ON relay one...')
            relay_one.off()  # Off actually turns it on because of how it is wired in the relay
            time.sleep(1)
            logging.info('Turning OFF relay three...')
            relay_three.on()  # Turn off the light to reduce heat
        else:
            logging.info('Turning OFF relay one...')
            relay_one.on()

        logging.debug('Going to sleep...')
        time.sleep(300)


def main():
    fan_monitor_thread = threading.Thread(target=handle_fan_signal)
    logging.debug('Starting up fan monitor thread...')
    fan_monitor_thread.start()

    keyboard.add_hotkey('0', switch_pin, (led_zero,))
    keyboard.add_hotkey('1', switch_pin, (led_one,))
    keyboard.add_hotkey('2', switch_pin, (led_two,))
    keyboard.add_hotkey('3', switch_pin, (relay_one,))
    keyboard.add_hotkey('4', switch_pin, (relay_two,))
    keyboard.add_hotkey('5', switch_pin, (relay_three,))
    keyboard.add_hotkey('6', switch_pin, (relay_four,))
    logging.debug('Waiting on keyboard input...')
    keyboard.wait()


if __name__ == '__main__':
    main()
