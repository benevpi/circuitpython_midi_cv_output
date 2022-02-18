#Notes:
# Control change? Should I just ignore this? Maybe for later. Not quite sure what I should do with it?
#should be easy enough to do control change on velocity.
# let's keep things super-simple and just do note on and note off.
# and only do the latest note.
# would be cool to have one output for the note and one for the volume (for a VCA). Should be do-able.


# technically a midi note can be a number or a string. Let's just deal with numbers for now.

# CV outputs are traditionally 1V per octave which means that this should be linear.
# Just convert number to the right scale and then just need to amplify to the correct voltage range and it should work

import usb_midi
import adafruit_midi
import time
#note - these must be imported like this
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.pitch_bend import PitchBend
import digitalio
import board

usb_midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0])

latest_note = -1

#note only need 7 bits as midi is 7 bits.
note_pins = [digitalio.DigitalInOut(board.GP0),
        digitalio.DigitalInOut(board.GP1),
        digitalio.DigitalInOut(board.GP2),
        digitalio.DigitalInOut(board.GP3),
        digitalio.DigitalInOut(board.GP4),
        digitalio.DigitalInOut(board.GP5),
        digitalio.DigitalInOut(board.GP6),]

for pin in note_pins:
    pin.direction = digitalio.Direction.OUTPUT

#note only need 7 bits as midi is 7 bits.
velocity_pins = [digitalio.DigitalInOut(board.GP10),
        digitalio.DigitalInOut(board.GP11),
        digitalio.DigitalInOut(board.GP12),
        digitalio.DigitalInOut(board.GP13),
        digitalio.DigitalInOut(board.GP14),
        digitalio.DigitalInOut(board.GP15),
        digitalio.DigitalInOut(board.GP16),]

for pin in velocity_pins:
    pin.direction = digitalio.Direction.OUTPUT


#not doing any scaling as 7 bits in and a 7 bit DAC. However, leaving this here incase we want to do any jiggery-pokery
def scale_note(number):
    return number

def output(number, pins):
    #how to avoid 'blips'?
    #probably just start at the lowest as switch a bit at a time
    #if it's a problem could use C to put a mask.
    for i in range(7):
        if 1<<i & number:
            pins[i].value = True
        else:
            pins[i].value = False

for i in range(127):
    print("testing: ", i)

    output(i, note_pins)
    output(i, velocity_pins)
    time.sleep(0.5)

print("running")
while True:
    msg = usb_midi.receive()
    if msg is not None:
        print("here")
        if isinstance(msg, NoteOn):
            print("Note On")
            latest_note = msg.note
            output(scale_note(msg.note), note_pins)
            output(scale_note(msg.velocity), velocity_pins)
            print("playing note: ", msg.note)
            print("at velocity: ", msg.velocity)
            print("msg channel: ", msg.channel)
        elif isinstance(msg, NoteOff):
            print("NoteOff")
            print(msg.note)
            if msg.note == latest_note:
                print("stopping note")
                #turn off velocity first
                output(0, velocity_pins)
                output(0, note_pins)
            latest_note == -1

    time.sleep(0.1)
