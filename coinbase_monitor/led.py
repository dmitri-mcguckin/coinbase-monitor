from enum import Enum
from raspi import raspi as r


__GPIO_INIT = False
__GPIO_MODE = r.GPIO.BCM


class Led(Enum):
    DOWN = 17
    UP = 18


def init_hw(leds: [Led]) -> None:
    r.GPIO.setwarnings(False)
    r.GPIO.setmode(__GPIO_MODE)
    print(f'Set GPIO mode to: {__GPIO_MODE}')
    r.define_out_pins(list(map(lambda x: x.value, leds)))


def set_indicator(to_on: Led) -> None:
    if(to_on == Led.UP):
        to_off = Led.DOWN
    else:
        to_off = Led.UP

    r.pins_high(to_on)
    r.pins_low(to_off)


def toggle() -> None:
    if(r.is_low(Led.DOWN)):
        set_indicator(Led.DOWN)
    else:
        set_indicator(Led.UP)


def hw_check(leds: [Led]) -> None:
    print('Hardware check:'.ljust(60, '-'))
    for led in leds:
        print(f'\tTesting LED {led} status...')
        r.led_blink(led.value)
        print('\tDone!')
    print('Hardware check complete!'.ljust(60, '-'))
