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


def control_fan(state: str = 'OFF'):
    """
    Change the state of the cooling fan.
    Note that the relay's off method actually turns on the appliance connected it
    and vice versa.
    """
    if state.upper() == 'ON':
        logging.info('Turning ON fan connected to relay one...')
        relay_one.off()
    elif state.upper() == 'OFF':
        logging.info('Turning OFF fan connected to relay one...')
        relay_one.on()
    else:
        return Exception('state should be given as ON or OFF')


def control_fog(state: str = 'OFF'):
    """
    Control the mister.
    Note that the relay's off method actually turns on the appliance connected it
    and vice versa.
    """
    if state.upper() == 'ON':
        logging.info('Turning ON mister/fogger connected to relay two...')
        relay_two.off()
    elif state.upper() == 'OFF':
        logging.info('Turning OFF mister/fogger connected to relay two...')
        relay_two.on()
    else:
        return Exception('state should be given as ON or OFF')


def control_light(state: str = 'OFF'):
    """
    Control the main paludarium light.
    Note that the relay's off method actually turns on the appliance connected it
    and vice versa.
    """
    if state.upper() == 'ON':
        logging.info('Turning ON main light connected to relay three...')
        relay_three.off()
    elif state.upper() == 'OFF':
        logging.info('Turning OFF main light connected to relay three...')
        relay_three.on()
    else:
        return Exception('state should be given as ON or OFF')


def control_water(state: str = 'OFF'):
    """
    Control the water pump.
    Note that the relay's off method actually turns on the appliance connected it
    and vice versa.
    """
    if state.upper() == 'ON':
        logging.info('Turning ON water pump connected to relay four...')
        relay_four.off()
    elif state.upper() == 'OFF':
        logging.info('Turning OFF water pump connected to relay four...')
        relay_four.on()
    else:
        return Exception('state should be given as ON or OFF')


def cool_down():
    """
    Try to cool down the paludarium
    """
    logging.info('Turning fan on to cool down tank...')
    control_fan('ON')
    time.sleep(1)
    logging.info('Turning light off to help cool down tank...')
    control_light('OFF')
    time.sleep(1)
    logging.info('Turning water pump on so fogger has water in the top reservoir...')
    control_water('ON')
    water_timer = threading.Timer(10.0, control_water, ['OFF'])
    logging.info('Starting timer to turn off water in 10 seconds...')
    water_timer.start()
    logging.info('Turning fogger on...')
    control_fog('ON')
    fog_timer = threading.Timer(270.0, control_fog, ['OFF'])
    logging.info('Starting timer to turn fogger off in 270 seconds...')
    fog_timer.start()


def handle_fan_signal():
    logging.info('Handling fan signals...')
    while True:
        logging.debug('Checking fan signal pin...')
        if fan_signal.value == 1:  # Signal that fan should be on
            cool_down()
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
