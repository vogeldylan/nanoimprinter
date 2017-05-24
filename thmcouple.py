'''

    ************************************************************************
    *   FILE NAME:      thmcouple.py
    *   AUTHOR:         Dylan Vogel
    *   PURPOSE:        This file contains functions related to thermocouple
    *                   measurement via the MAX31855.
    *
    *   EXTERNAL REFERENCES:    spidev
    *
    *
    *   NOTES:          The read function could be modified to read 32 bits instead
    *                   of 16 and check what type of fault is encountered.
    *
    *   REVISION HISTORY:
    *
    *                   2017-05-22: Wrote setup and read functions.
    *                   2017-05-23: Added comments.

'''
import spidev

global READBYTE
global tc_1, tc_2

READBYTE = [0x00, 0x00]

def setup():
    global tc_1, tc_2

    tc_1 = spidev.SpiDev()
    tc_2 = spidev.SpiDev()
    tc_1.open(0,0)
    tc_2.open(0,1)
    tc_1.max_speed_hz = 5000000    # See MAX31855 datasheet
    tc_2.max_speed_hz = 5000000;


def read(thmcouple):
    # Assume the input is either 1 or 2, and default to 1 if another value is entered.
    if (thmcouple == 2):
        rec = tc_2.xfer2(READBYTE)
    else:
        rec = tc_1.xfer2(READBYTE)

    # Check the fault bit of the returned message
    if rec[1] & 0x01:
        fault = 1
        #print "A fault was encountered by the MAX31855"
    else:
        fault = 0

    # Convert the 16-bit returned number to the 14-bit temp value.
    data = (rec[0] << 6) | (rec[1] >> 2)

    # Check for negatives
    if data >> 13:
        temp = float((int(data) / 4.0) - 2048)
    else:
        temp = float(data / 4.0)

    return temp

def close():
    tc_1.close()
    tc_2.close()
