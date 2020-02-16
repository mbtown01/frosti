# rpt

RaspberryPi-powered Griddy-enabled thermostat

## Motivation

I personally love the idea of having electricity priced based on supply/demand.
It wasn't long after a few friends told me about
[GoGriddy](https://www.gogriddy.com/) that I signed up.  Starting in January of
2019, I was easily saving 20% or so relative to available electricy plans.
Everything was going according to plan.

Then in August of 2019, Texas experienced record heat combined with electricity
generation capacity shortages, causing massive spikes in prices.  There were
several times that month where prices got to the legal limit of $9/kW\*h.  To
put that kind of price in perspective, if your house is drawing 10kW running
your multiple AC systems (*by far* the biggest use of electricity in Houston),
that's a $90 power bill in 1 hour.  These price spikes lasted for a period of
time and then go back to reasonable levels.  But beacuse my family is gone
during the day and unable to respond to these price fluctuations by turning
things off, we received an eye-opening electric bill -- something clearly had to
change.

My motivation is very simple.  Air conditioning is by far my biggest power
consumption.  If I can simply curtail usage during periods of high power prices,
I think I can get back to where I was in the first half of the year when I was
saving %20!

But it's more than just saving some money.  I'm also interested in understanding
how my HVAC systems are performing.

* When do they run?
* How long do they run?
* If I set the temperature target higher in the summer, how much electricity does that save me?
* Is there a more efficient algorithm for keeping a target temperature?
