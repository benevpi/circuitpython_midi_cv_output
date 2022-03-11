
#Note this is in Micropython not circuit python as circuit python doesn't give enough control over the state machines.

from machine import Pin, ADC
import array
from rp2 import PIO, StateMachine, asm_pio
import uctypes
from uctypes import BF_POS, BF_LEN, UINT32, BFUINT32, struct
from math import floor, ceil
from time import sleep
import _thread

min_sound_freq = 110 #A2
max_sound_freq = 7040 #A8


@asm_pio(out_init=(PIO.OUT_HIGH, PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW,PIO.OUT_LOW,), out_shiftdir=PIO.SHIFT_RIGHT)
def seven_bit_dac(): # also want FIFO join.
    wrap_target()
    label("loop")
    pull()
    out(pins, 7) [2]
    out(pins, 7) [2]
    out(pins, 7) [2]
    out(pins, 7)
    jmp("loop")
    wrap()

PIO0_BASE       = 0x50200000
SM0_CLKDIV      = 0x0C8

PIO0_SM0_CLKDIV = PIO0_BASE + SM0_CLKDIV

CLKDIV_REGS = {"VALUE" : 0|UINT32}

CLKDIVPIO0SM0_STRUCT = struct(PIO0_SM0_CLKDIV, CLKDIV_REGS)

def set_sm_frequency(structure, sm_freq):
    #need to set this using the registers :(
    #formula (from datasheet) is: Frequency = clock freq / (CLKDIV_INT + CLKDIV_FRAC / 256)
    #note fractional int -- a bit weird
    machine_frequency = machine.freq()
    
    #get nearest main divider (16 bits), so max number is 65535
    main_div = ceil(machine_frequency / sm_freq)
    
    if (main_div > 65535):
        main_div = 65535
        
    print(main_div)
    
    #get fracitional bit (8 bits), so max number is 256
    #no idea if this is right. My maths is iffy. I'll have to see how it works out
    
    if ((machine_frequency / main_div) == sm_freq):
        fractional_div = 0
    else:
        fractional_div = int((machine_frequency/ (sm_freq - (machine_frequency / main_div)) ) * 265)
    
    print(fractional_div)
    
    if (fractional_div > 256):
        fractional_div = 256
        
    if (fractional_div < 0):
        fractional_div = 0
        
    CLKDIVPIO0SM0_STRUCT.VALUE = (main_div <<16) | (fractional_div << 8)
    
def sound_freq_to_sm_freq(samples, sound_freq):
    return (sound_freq * 3) * samples

def set_frequency(sm, min_freq, max_freq):
    wanted_freq = int (min_sound_freq + ((analog_in.value/65536) * (max_freq - min_freq)))
    sm.frequency = sound_freq_to_sm_freq(130, wanted_freq)
    
packed_data = array.array('I', [0 for _ in range(30)])
for i in range(30):
    outval = 0
    for j in range(4):
        value = (i*4)+j
        outval = outval | (value << j*7)
    packed_data[i] = outval
    
print(packed_data)
    
frequency = sound_freq_to_sm_freq(120, 440)

print(frequency)

def second_core():
    adc=ADC(0)
    while True:
        analog_value = adc.read_u16()
        wanted_freq = int (min_sound_freq + ((analog_value/65536) * (max_sound_freq - min_sound_freq)))
        calc_freq = sound_freq_to_sm_freq(120, wanted_freq)
        set_sm_frequency(0, calc_freq)
        sleep(0.1)
    
    
sm = rp2.StateMachine(0, seven_bit_dac, freq=frequency, out_base=Pin(0))
sm.active(1)

_thread.start_new_thread(second_core, ())

while True:
    sm.put(packed_data,0)
    
