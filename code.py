#Notes:
# Control change? Should I just ignore this? Maybe for later. Not quite sure what I should do with it?
# let's keep things super-simple and just do note on and note off.
# and only do the latest note.
# would be cool to have one output for the note and one for the volume (for a VCA). Should be do-able.


# technically a midi note can be a number or a string. Let's just deal with numbers for now.

# CV outputs are traditionally 1V per octave which means that this should be linear. 
# Just convert number to the right scale and it's done.

import usb_midi
import adafruit_midi
import time
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.pitch_bend import PitchBend
import digitalio
import board

usb_midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0])

latest_note = -1

note_pins = [digitalio.DigitalInOut(board.GP0),
        digitalio.DigitalInOut(board.GP1),
        digitalio.DigitalInOut(board.GP2),
        digitalio.DigitalInOut(board.GP3),
        digitalio.DigitalInOut(board.GP4),
        digitalio.DigitalInOut(board.GP5),
        digitalio.DigitalInOut(board.GP6),
        digitalio.DigitalInOut(board.GP7),]
        
for pin in pins:
    pin.direction = digitalio.Direction.OUTPUT
    
velocity_pins = [digitalio.DigitalInOut(board.GP10),
        digitalio.DigitalInOut(board.GP11),
        digitalio.DigitalInOut(board.GP11),
        digitalio.DigitalInOut(board.GP11),
        digitalio.DigitalInOut(board.GP11),
        digitalio.DigitalInOut(board.GP11),


#if we're going with 8 bit output, basically just need to double the number.
#might want to do something different in the future.
def scale_note(number):
    return number*2
    
def output(number, pins):
    #how to avoid 'blips'?
    for i in range(8):
        if 1<<i & number:
            pins[i].value = True
        else:
            pins[i].value = False
        
while True:
    msg = usb_midi.receive()
    if msg is not None:
        if isinstance(msg, NoteOn):
            print("Note On")
            latest_note = msg.note
            output(scale_note(msg.note), note_pins)
            print("playing note: ", msg.note)
        elif isinstance(msg, NoteOff):
            print("NoteOff")
            print(msg.note)
            if msg.note == latest_note:
                print("stopping note")
                output(0)
            latest_note == -1

    time.sleep(0.1)
