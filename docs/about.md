---
layout: page
title: About
permalink: /about/
---

FROSTI (the Financially Responsive Open-Source Thermostat Initiative) is a
Raspberry Pi-based thermostat that monitors the local spot market for power
and changes temperature targets to minimize power usage during periods of
high prices.

![rendering](/frosti/images/enclosure_v1.png)

## Features

* Real-time monitoring of local power-price
* Web-based configuration
* 2.9" e-paper display clearly visible from a distance
* LED indicators for mode changes
* Full RESTful API for monitoring status and controlling from remote

Today, FROSTI works with [GoGriddy](https://www.gogriddy.com/), but can
be extended in the future for other power markets.

## Motivation

I love the idea of having electricity priced based on supply/demand. It wasn't
long after a few friends told me about [GoGriddy](https://www.gogriddy.com/)
that I signed up.  Starting in January of 2019, I was easily saving 20% or so
relative to available electricy plans. Everything was going according to plan.

Then in August of 2019, Houston (where I live) experienced record heat combined
with electricity generation capacity shortages, causing massive spikes in
prices.  There were several times that month where prices got to $9/kW\*h,
costing me around $100 in a *single hour*.

My motivation is very simple.  Air conditioning is by far my biggest source
of power consumption.  If I can curtail usage during periods of high prices,
I get the benefits of cheap power 99.95% of the time and de-risk the other
0.05%, and I come out a winner.

## Future Work

FROSTI is about far more than just lowering your power bills.  The *data* that
comes from FROSTI is valuable for things like:

* Sizing a next A/C system (e.g. how many 'tons')
* Knowing whether your A/C system is
  [short-cycling](https://www.google.com/search?q=what+is+short+cycling)
* Knowing how changing your temperature targets affects HVAC usage

Also, with the addition of remote sensors, we could do things like:

* Balance HVAC for additional rooms
* Monitor the temperature of air coming out of the ducts, potentially catching
  problems
* Monitor the air speed at the ducts, potentially notifying the homeowner that
  airflow is impeded (e.g. filter needs changed)
  