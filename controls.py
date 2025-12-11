#!/usr/bin/python3

import os, sys
from fcntl import ioctl

# ioctl commands defined at the pci driver
RD_SWITCHES   = 24929
RD_PBUTTONS   = 24930
WR_L_DISPLAY  = 24931
WR_R_DISPLAY  = 24932
WR_RED_LEDS   = 24933
WR_GREEN_LEDS = 24934

def read_button():
    fd = os.open("/dev/mydev", os.O_RDWR)
    ioctl(fd, RD_PBUTTONS)
    red = os.read(fd, 4); # read 4 bytes and store in red var
    red_number = int.from_bytes(red, 'little')
    os.close(fd)

    if red_number == 7:
        return 'LEFT'
    elif red_number == 11:
        return 'DOWN'
    elif red_number == 13:
        return 'UP'
    elif red_number == 14:
        return "RIGHT"
    elif red_number == 6:
        return "LEFT+RIGHT"

    return ''

def write_right_display(data):
    fd = os.open("/dev/mydev", os.O_RDWR)
    ioctl(fd, WR_R_DISPLAY)
    retval = os.write(fd, data.to_bytes(4, 'little'))
    os.close(fd)

def write_left_display(data):
    fd = os.open("/dev/mydev", os.O_RDWR)
    ioctl(fd, WR_L_DISPLAY)
    retval = os.write(fd, data.to_bytes(4, 'little'))
    os.close(fd)

def write_red_leds(data):
    fd = os.open("/dev/mydev", os.O_RDWR)
    ioctl(fd, WR_RED_LEDS)
    retval = os.write(fd, data.to_bytes(4, 'little'))
    os.close(fd)

def write_green_leds(data):
    fd = os.open("/dev/mydev", os.O_RDWR)
    ioctl(fd, WR_GREEN_LEDS)
    retval = os.write(fd, data.to_bytes(4, 'little'))
    os.close(fd)

def dec_to_7seg(number):
    return {
        0: 0xC0,
        1: 0xF9,
        2: 0xA4,
        3: 0xB0,
        4: 0x99,
        5: 0x92,
        6: 0x82,
        7: 0xF8,
        8: 0x80,
        9: 0x90
    }[number]

def digit_to_7seg(numero):
    digitos = str(numero).zfill(4)
    segmentos = [dec_to_7seg(int(digito)) for digito in digitos]
    return int("".join(["{:02X}".format(segmento) for segmento in segmentos]), 16)
    

