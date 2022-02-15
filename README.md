Circuit Python to CV output
===========================

This converts midi to *A* voltage. using two R/2R ladders on pins 0-6 and 10-16 (each is 7 bit because midi is 7 bit). You could also use some other DAC if you want. It should be pretty easy. It should be approx linear so if you amplify it appropriately, it should be 1v per octave, but that's up to you.

There might be blips as the values change. They'll be very high frequency, so a low-pass filter should iron them out.
