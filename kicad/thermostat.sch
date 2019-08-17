EESchema Schematic File Version 4
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector:Raspberry_Pi_2_3 J1
U 1 1 5D586BF0
P 2200 2350
F 0 "J1" H 2200 3831 50  0000 C CNN
F 1 "Raspberry_Pi_2_3" H 2200 3740 50  0000 C CNN
F 2 "" H 2200 2350 50  0001 C CNN
F 3 "https://www.raspberrypi.org/documentation/hardware/raspberrypi/schematics/rpi_SCH_3bplus_1p0_reduced.pdf" H 2200 2350 50  0001 C CNN
	1    2200 2350
	1    0    0    -1  
$EndComp
Text GLabel 1650 3850 0    50   Input ~ 0
GND
Wire Wire Line
	1800 3650 1800 3850
Wire Wire Line
	1800 3850 1650 3850
Wire Wire Line
	1900 3650 1900 3850
Wire Wire Line
	1900 3850 1800 3850
Connection ~ 1800 3850
Wire Wire Line
	2000 3650 2000 3850
Wire Wire Line
	2000 3850 1900 3850
Connection ~ 1900 3850
Wire Wire Line
	2100 3650 2100 3850
Wire Wire Line
	2100 3850 2000 3850
Connection ~ 2000 3850
Wire Wire Line
	2200 3650 2200 3850
Wire Wire Line
	2200 3850 2100 3850
Connection ~ 2100 3850
Wire Wire Line
	2300 3650 2300 3850
Wire Wire Line
	2300 3850 2200 3850
Connection ~ 2200 3850
Wire Wire Line
	2400 3650 2400 3850
Wire Wire Line
	2400 3850 2300 3850
Connection ~ 2300 3850
Wire Wire Line
	2500 3650 2500 3850
Wire Wire Line
	2500 3850 2400 3850
Connection ~ 2400 3850
$EndSCHEMATC
