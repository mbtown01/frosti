# Hardware notes

## Simulator for Relays

After a few mis-steps, I learned that you need to give the relays more power
to move than GPIO is able to deliver.  We're employing a 'Darlington array'
(the TI ULN2003AD chip) to *briefly* deliver about 95mW to the relay.

The code below can be pasted into the circuit simulator at
<https://www.falstad.com/circuit/> to simulate the relay circuit.  The resistors
we're using (Mouser part 667-ERJ-P06F64R9V) can dissipate up to 500mW, which
this circuit will get to about 80% to move the relay.  In code, we ensure this
loop is only active for a fraction of a second.

```
$ 1 0.000005 10.20027730826997 50 5 43
r 368 272 368 160 0 64
r 224 272 224 160 0 64
r 368 272 224 272 0 90
w 224 160 368 160 0
v 128 352 128 160 0 0 40 5 0 0 0.5
w 128 160 224 160 0
s 224 272 224 352 0 1 false
s 368 272 368 352 0 1 false
w 128 352 224 352 0
w 224 352 368 352 0
```
