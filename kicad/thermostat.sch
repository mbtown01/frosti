EESchema Schematic File Version 4
LIBS:thermostat-cache
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "PoE Thermostat"
Date "2019-08-24"
Rev "1"
Comp "Madllama Electronics"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Wire Wire Line
	3100 1100 2900 1100
Wire Wire Line
	3100 1200 2900 1200
Wire Wire Line
	3000 1300 3000 1700
Wire Wire Line
	3000 2700 2900 2700
Wire Wire Line
	3000 2500 2900 2500
Connection ~ 3000 2700
Wire Wire Line
	3000 2000 2900 2000
Connection ~ 3000 2500
Wire Wire Line
	3000 1700 2900 1700
Connection ~ 3000 2000
Wire Wire Line
	2300 3000 2400 3000
Wire Wire Line
	2300 1500 2300 2300
Wire Wire Line
	2300 2300 2400 2300
Connection ~ 2300 3000
Wire Wire Line
	2200 1900 2400 1900
Wire Wire Line
	2200 1100 2400 1100
Wire Wire Line
	2300 1500 2400 1500
Connection ~ 2300 2300
Wire Wire Line
	2400 1200 1250 1200
Wire Wire Line
	1250 1300 2400 1300
Wire Wire Line
	1250 1400 2400 1400
Wire Wire Line
	2400 1600 1250 1600
Wire Wire Line
	1250 1700 2400 1700
Wire Wire Line
	1250 1800 2400 1800
Wire Wire Line
	2400 2000 1250 2000
Wire Wire Line
	1250 2100 2400 2100
Wire Wire Line
	1250 2200 2400 2200
Wire Wire Line
	2400 2400 1250 2400
Wire Wire Line
	1250 2500 2400 2500
Wire Wire Line
	1250 2600 2400 2600
Wire Wire Line
	2400 2700 1250 2700
Wire Wire Line
	1250 2800 2400 2800
Wire Wire Line
	1250 2900 2400 2900
Wire Wire Line
	2900 2800 3950 2800
Wire Wire Line
	2900 2900 3950 2900
Wire Wire Line
	2900 2300 3950 2300
Wire Wire Line
	2900 2400 3950 2400
Wire Wire Line
	2900 2100 3950 2100
Wire Wire Line
	2900 2200 3950 2200
Wire Wire Line
	2900 1800 3950 1800
Wire Wire Line
	2900 1900 3950 1900
Wire Wire Line
	2900 1500 3950 1500
Wire Wire Line
	2900 1600 3950 1600
Wire Wire Line
	2900 1400 3950 1400
Wire Wire Line
	2900 2600 3950 2600
Text Label 1250 1200 0    50   ~ 0
GPIO2(SDA1)
Text Label 1250 1300 0    50   ~ 0
GPIO3(SCL1)
Text Label 1250 1400 0    50   ~ 0
GPIO4(GCLK)
Text Label 1250 1600 0    50   ~ 0
GPIO17(GEN0)
Text Label 1250 1700 0    50   ~ 0
GPIO27(GEN2)
Text Label 1250 1800 0    50   ~ 0
GPIO22(GEN3)
Text Label 1250 2000 0    50   ~ 0
GPIO10(SPI0_MOSI)
Text Label 1250 2100 0    50   ~ 0
GPIO9(SPI0_MISO)
Text Label 1250 2200 0    50   ~ 0
GPIO11(SPI0_SCK)
Text Label 1250 2400 0    50   ~ 0
ID_SD
Text Label 1250 2500 0    50   ~ 0
GPIO5
Text Label 1250 2600 0    50   ~ 0
GPIO6
Text Label 1250 2700 0    50   ~ 0
GPIO13(PWM1)
Text Label 1250 2800 0    50   ~ 0
GPIO19(SPI1_MISO)
Text Label 1250 2900 0    50   ~ 0
GPIO26
Text Label 3950 2900 2    50   ~ 0
GPIO20(SPI1_MOSI)
Text Label 3950 2800 2    50   ~ 0
GPIO16
Text Label 3950 2600 2    50   ~ 0
GPIO12(PWM0)
Text Label 3950 2400 2    50   ~ 0
ID_SC
Text Label 3950 2300 2    50   ~ 0
GPIO7(SPI1_CE_N)
Text Label 3950 2200 2    50   ~ 0
GPIO8(SPI0_CE_N)
Text Label 3950 2100 2    50   ~ 0
GPIO25(GEN6)
Text Label 3950 1900 2    50   ~ 0
GPIO24(GEN5)
Text Label 3950 1800 2    50   ~ 0
GPIO23(GEN4)
Text Label 3950 1600 2    50   ~ 0
GPIO18(GEN1)(PWM0)
Text Label 3950 1500 2    50   ~ 0
GPIO15(RXD0)
Text Label 3950 1400 2    50   ~ 0
GPIO14(TXD0)
Wire Wire Line
	3000 1300 2900 1300
Connection ~ 3000 1700
$Comp
L Connector_Generic:Conn_02x20_Odd_Even CONN1
U 1 1 59AD464A
P 2600 2000
F 0 "CONN1" H 2650 3117 50  0000 C CNN
F 1 "Conn_02x20_Odd_Even" H 2650 3026 50  0000 C CNN
F 2 "Socket_Strips:Socket_Strip_Straight_2x20_Pitch2.54mm" H -2250 1050 50  0001 C CNN
F 3 "" H -2250 1050 50  0001 C CNN
	1    2600 2000
	1    0    0    -1  
$EndComp
Wire Wire Line
	2900 3000 3950 3000
Text Label 3950 3000 2    50   ~ 0
GPIO21(SPI1_SCK)
Wire Wire Line
	3100 1100 3100 1200
Wire Wire Line
	3000 2500 3000 2700
Wire Wire Line
	3000 2000 3000 2500
Wire Wire Line
	2200 1100 2200 1900
Wire Wire Line
	2300 2300 2300 3000
Wire Wire Line
	3000 1700 3000 2000
Text Label 3100 750  0    50   ~ 0
PWR_5V
Text Label 2200 750  0    50   ~ 0
PWR_3.3V
Connection ~ 3100 1100
Wire Wire Line
	3100 1100 3100 750 
Wire Wire Line
	2200 1100 2200 750 
Connection ~ 2200 1100
Text Label 2600 3200 0    50   ~ 0
GND
Wire Wire Line
	3000 2700 3000 3200
Wire Wire Line
	2300 3000 2300 3200
Wire Wire Line
	2300 3200 3000 3200
Text Label 8700 1950 0    50   ~ 0
HVAC_PWR(RED)
Text Label 8700 2050 0    50   ~ 0
HVAC_HEAT(WHITE)
Text Label 8700 2150 0    50   ~ 0
HVAC_COOL(YELLOW)
Text Label 8700 2250 0    50   ~ 0
HVAC_FAN(GREEN)
Wire Wire Line
	8700 1950 9500 1950
Wire Wire Line
	9500 2050 8700 2050
Wire Wire Line
	8700 2150 9500 2150
Wire Wire Line
	8700 2250 9500 2250
$Comp
L thermostat-rescue:Relay?-thermostat-rescue RELAY1
U 1 1 5D5E9059
P 6200 1250
F 0 "RELAY1" V 6350 1450 50  0001 C CNN
F 1 "RELAY_FAN" H 6200 1573 50  0000 C CNN
F 2 "project_footprints:AGQ210A03" V 6350 1450 50  0001 C CNN
F 3 "" V 6350 1450 50  0001 C CNN
F 4 "AGQ210A03" H 6200 1250 50  0001 C CNN "MPN"
F 5 "1" H 6200 1250 50  0001 C CNN "Populate"
F 6 "AGQ210A03" H 6200 1250 50  0001 C CNN "Package"
	1    6200 1250
	1    0    0    -1  
$EndComp
$Comp
L thermostat-rescue:Mounting_Hole-Mechanical-thermostat-rescue MK1
U 1 1 5D5E9722
P 800 6800
F 0 "MK1" H 900 6846 50  0000 L CNN
F 1 "Mounting_Hole-Mechanical" H 900 6755 50  0000 L CNN
F 2 "Mounting_Holes:MountingHole_2.5mm_Pad" H 800 6800 50  0001 C CNN
F 3 "" H 800 6800 50  0001 C CNN
	1    800  6800
	1    0    0    -1  
$EndComp
$Comp
L thermostat-rescue:Mounting_Hole-Mechanical-thermostat-rescue MK2
U 1 1 5D5F78A7
P 800 7050
F 0 "MK2" H 900 7096 50  0000 L CNN
F 1 "Mounting_Hole-Mechanical" H 900 7005 50  0000 L CNN
F 2 "Mounting_Holes:MountingHole_2.5mm_Pad" H 800 7050 50  0001 C CNN
F 3 "" H 800 7050 50  0001 C CNN
	1    800  7050
	1    0    0    -1  
$EndComp
$Comp
L thermostat-rescue:Mounting_Hole-Mechanical-thermostat-rescue MK3
U 1 1 5D5F9275
P 800 7300
F 0 "MK3" H 900 7346 50  0000 L CNN
F 1 "Mounting_Hole-Mechanical" H 900 7255 50  0000 L CNN
F 2 "Mounting_Holes:MountingHole_2.5mm_Pad" H 800 7300 50  0001 C CNN
F 3 "" H 800 7300 50  0001 C CNN
	1    800  7300
	1    0    0    -1  
$EndComp
$Comp
L thermostat-rescue:Mounting_Hole-Mechanical-thermostat-rescue MK4
U 1 1 5D5FAC9B
P 800 7550
F 0 "MK4" H 900 7596 50  0000 L CNN
F 1 "Mounting_Hole-Mechanical" H 900 7505 50  0000 L CNN
F 2 "Mounting_Holes:MountingHole_2.5mm_Pad" H 800 7550 50  0001 C CNN
F 3 "" H 800 7550 50  0001 C CNN
	1    800  7550
	1    0    0    -1  
$EndComp
Text Label 6550 1050 0    50   ~ 0
GPIO19(SPI1_MISO)
Wire Wire Line
	6550 1050 6350 1050
Wire Wire Line
	6050 1050 5850 1050
Wire Wire Line
	6050 1200 5850 1200
Wire Wire Line
	6050 1300 5850 1300
Text Label 5850 1050 2    50   ~ 0
GPIO5
Text Label 5850 1200 2    50   ~ 0
HVAC_FAN(GREEN)
Text Label 5850 1300 2    50   ~ 0
HVAC_PWR(RED)
$Comp
L thermostat-rescue:Relay?-thermostat-rescue RELAY2
U 1 1 5D5EC4AE
P 6200 1950
F 0 "RELAY2" V 6350 2150 50  0001 C CNN
F 1 "RELAY_HEAT" H 6200 2273 50  0000 C CNN
F 2 "project_footprints:AGQ210A03" V 6350 2150 50  0001 C CNN
F 3 "" V 6350 2150 50  0001 C CNN
F 4 "AGQ210A03" H 6200 1950 50  0001 C CNN "MPN"
F 5 "1" H 6200 1950 50  0001 C CNN "Populate"
	1    6200 1950
	1    0    0    -1  
$EndComp
Text Label 6550 1750 0    50   ~ 0
GPIO19(SPI1_MISO)
Wire Wire Line
	6550 1750 6350 1750
Wire Wire Line
	6050 1750 5850 1750
Wire Wire Line
	6050 1900 5850 1900
Wire Wire Line
	6050 2000 5850 2000
Text Label 5850 1750 2    50   ~ 0
GPIO6
Text Label 5850 1900 2    50   ~ 0
HVAC_HEAT(WHITE)
Text Label 5850 2000 2    50   ~ 0
HVAC_PWR(RED)
$Comp
L thermostat-rescue:Relay?-thermostat-rescue RELAY3
U 1 1 5D5EE68E
P 6200 2650
F 0 "RELAY3" V 6350 2850 50  0001 C CNN
F 1 "RELAY_COOL" H 6200 2973 50  0000 C CNN
F 2 "project_footprints:AGQ210A03" V 6350 2850 50  0001 C CNN
F 3 "" V 6350 2850 50  0001 C CNN
F 4 "" H 6200 2650 50  0001 C CNN "TEST"
F 5 "AGQ210A03" H 6200 2650 50  0001 C CNN "MPN"
F 6 "1" H 6200 2650 50  0001 C CNN "Populate"
	1    6200 2650
	1    0    0    -1  
$EndComp
Text Label 6550 2450 0    50   ~ 0
GPIO19(SPI1_MISO)
Wire Wire Line
	6550 2450 6350 2450
Wire Wire Line
	6050 2450 5850 2450
Wire Wire Line
	6050 2600 5850 2600
Wire Wire Line
	6050 2700 5850 2700
Text Label 5850 2450 2    50   ~ 0
GPIO13(PWM1)
Text Label 5850 2600 2    50   ~ 0
HVAC_COOL(YELLOW)
Text Label 5850 2700 2    50   ~ 0
HVAC_PWR(RED)
Wire Wire Line
	2100 4300 2500 4300
Wire Wire Line
	2100 4750 2500 4750
Wire Wire Line
	2100 5200 2500 5200
Wire Wire Line
	2100 5650 2500 5650
Text Label 2500 5650 0    50   ~ 0
PWR_5V
Text Label 2500 5200 0    50   ~ 0
PWR_5V
Text Label 2500 4750 0    50   ~ 0
PWR_5V
Text Label 2500 4300 0    50   ~ 0
PWR_5V
Wire Wire Line
	1700 5650 850  5650
Wire Wire Line
	1700 5200 850  5200
Wire Wire Line
	1700 4750 850  4750
Wire Wire Line
	1700 4300 850  4300
Text Label 850  5650 0    50   ~ 0
GPIO12(PWM0)
Text Label 850  5200 0    50   ~ 0
GPIO21(SPI1_SCK)
Text Label 850  4750 0    50   ~ 0
GPIO20(SPI1_MOSI)
Text Label 850  4300 0    50   ~ 0
GPIO16
$Comp
L Switch:SW_Push SW_UP1
U 1 1 5D59B864
P 1900 4750
F 0 "SW_UP1" H 1900 4943 50  0000 C CNN
F 1 "SW_UP" H 1900 4944 50  0001 C CNN
F 2 "Buttons_Switches_SMD:SW_SPST_EVPBF" H 1900 4950 50  0001 C CNN
F 3 "~" H 1900 4950 50  0001 C CNN
	1    1900 4750
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_Push SW_MODE1
U 1 1 5D59E237
P 1900 4300
F 0 "SW_MODE1" H 1900 4493 50  0000 C CNN
F 1 "SW_MODE" H 1900 4494 50  0001 C CNN
F 2 "Buttons_Switches_SMD:SW_SPST_EVPBF" H 1900 4500 50  0001 C CNN
F 3 "~" H 1900 4500 50  0001 C CNN
	1    1900 4300
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_Push SW_DOWN1
U 1 1 5D5A0BE1
P 1900 5200
F 0 "SW_DOWN1" H 1900 5393 50  0000 C CNN
F 1 "SW_DOWN" H 1900 5394 50  0001 C CNN
F 2 "Buttons_Switches_SMD:SW_SPST_EVPBF" H 1900 5400 50  0001 C CNN
F 3 "~" H 1900 5400 50  0001 C CNN
	1    1900 5200
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_Push SW_ENTER1
U 1 1 5D5A1B56
P 1900 5650
F 0 "SW_ENTER1" H 1900 5843 50  0000 C CNN
F 1 "SW_ENTER" H 1900 5844 50  0001 C CNN
F 2 "Buttons_Switches_SMD:SW_SPST_EVPBF" H 1900 5850 50  0001 C CNN
F 3 "~" H 1900 5850 50  0001 C CNN
	1    1900 5650
	1    0    0    -1  
$EndComp
Text HLabel 3800 750  0    50   Input ~ 0
TEST
$Comp
L Connector_Generic:Conn_01x04 J1
U 1 1 5D66FD1D
P 4950 6500
F 0 "J1" H 5030 6492 50  0000 L CNN
F 1 "Display i2c" H 5030 6401 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x04_Pitch2.54mm" H 4950 6500 50  0001 C CNN
F 3 "~" H 4950 6500 50  0001 C CNN
	1    4950 6500
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x04 J2
U 1 1 5D67AFA8
P 4950 7000
F 0 "J2" H 5030 6992 50  0000 L CNN
F 1 "Sensor i2c" H 5030 6901 50  0000 L CNN
F 2 "Socket_Strips:Socket_Strip_Straight_1x04_Pitch2.54mm" H 4950 7000 50  0001 C CNN
F 3 "~" H 4950 7000 50  0001 C CNN
	1    4950 7000
	1    0    0    -1  
$EndComp
Text Label 4550 6400 2    50   ~ 0
GND
Text Label 4550 6500 2    50   ~ 0
PWR_5V
Text Label 4550 6600 2    50   ~ 0
GPIO2(SDA1)
Text Label 4550 6700 2    50   ~ 0
GPIO3(SCL1)
Text Label 4550 6900 2    50   ~ 0
GPIO2(SDA1)
Text Label 4550 7000 2    50   ~ 0
GPIO3(SCL1)
Text Label 4550 7100 2    50   ~ 0
GND
Text Label 4550 7200 2    50   ~ 0
PWR_5V
Wire Wire Line
	4550 6400 4750 6400
Wire Wire Line
	4550 6500 4750 6500
Wire Wire Line
	4750 6600 4550 6600
Wire Wire Line
	4550 6700 4750 6700
Wire Wire Line
	4750 6900 4550 6900
Wire Wire Line
	4750 7000 4550 7000
Wire Wire Line
	4550 7100 4750 7100
Wire Wire Line
	4750 7200 4550 7200
$Comp
L Connector_Generic:Conn_01x05 J4
U 1 1 5D687A2E
P 4500 4100
F 0 "J4" H 4580 4092 50  0000 L CNN
F 1 "PoE Output" H 4580 4001 50  0000 L CNN
F 2 "project_footprints:M20-7910542R" H 4500 4100 50  0001 C CNN
F 3 "~" H 4500 4100 50  0001 C CNN
	1    4500 4100
	-1   0    0    1   
$EndComp
$Comp
L Connector_Generic:Conn_01x05 J3
U 1 1 5D685426
P 4500 4700
F 0 "J3" H 4580 4692 50  0000 L CNN
F 1 "PoE Input" H 4580 4601 50  0000 L CNN
F 2 "project_footprints:M20-7910542R" H 4500 4700 50  0001 C CNN
F 3 "~" H 4500 4700 50  0001 C CNN
	1    4500 4700
	-1   0    0    1   
$EndComp
$Comp
L thermostat:0857891001 J5
U 1 1 5D6600E3
P 5600 4350
F 0 "J5" H 5600 3635 50  0000 C CNN
F 1 "0857891001" H 5600 3726 50  0000 C CNN
F 2 "project_footprints:0857891001" H 4950 4100 50  0001 C CNN
F 3 "" H 4950 4100 50  0001 C CNN
	1    5600 4350
	-1   0    0    1   
$EndComp
Wire Wire Line
	5200 4500 4950 4500
Wire Wire Line
	4950 4500 4950 4800
Wire Wire Line
	4950 4800 4700 4800
Text Label 4850 4200 0    50   ~ 0
GND
Text Label 4850 4100 0    50   ~ 0
PWR_5V
Wire Wire Line
	4700 4200 4850 4200
Wire Wire Line
	4700 4100 4850 4100
$Comp
L Regulator_Switching:LM2596S-5 IC1
U 1 1 5D6B23A7
P 8900 3600
F 0 "IC1" H 8900 3967 50  0000 C CNN
F 1 "LM2596S-5" H 8900 3876 50  0000 C CNN
F 2 "Package_TO_SOT_SMD:TO-263-5_TabPin3" H 8950 3350 50  0001 L CIN
F 3 "http://www.ti.com/lit/ds/symlink/lm2596.pdf" H 8900 3600 50  0001 C CNN
F 4 "926-LM2596S-50" H 8900 3600 50  0001 C CNN "Mouser"
	1    8900 3600
	1    0    0    -1  
$EndComp
$Comp
L Connector:Screw_Terminal_01x05 J6
U 1 1 5D6C475A
P 9700 2150
F 0 "J6" H 9780 2192 50  0000 L CNN
F 1 "Screw_Terminal_01x05" H 9780 2101 50  0000 L CNN
F 2 "" H 9700 2150 50  0001 C CNN
F 3 "~" H 9700 2150 50  0001 C CNN
	1    9700 2150
	1    0    0    -1  
$EndComp
Text Label 8700 2350 0    50   ~ 0
HVAC_COMMON
Wire Wire Line
	8700 2350 9500 2350
Text Label 7000 3500 0    50   ~ 0
HVAC_PWR(RED)
Wire Wire Line
	7000 3500 7800 3500
Text Label 10950 4200 2    50   ~ 0
GND
$Comp
L Device:D_Small D1
U 1 1 5D6DC8DD
P 7900 3500
F 0 "D1" H 7900 3295 50  0000 C CNN
F 1 "S1A" H 7900 3386 50  0000 C CNN
F 2 "Diodes_SMD:D_SOD-123F" V 7900 3500 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/308/US1AFA-1301710.pdf" V 7900 3500 50  0001 C CNN
F 4 "512-US1AFA" H 7900 3500 50  0001 C CNN "Mouser"
	1    7900 3500
	-1   0    0    1   
$EndComp
$Comp
L Device:D_Small D2
U 1 1 5D6DD814
P 9500 4000
F 0 "D2" V 9454 4068 50  0000 L CNN
F 1 "SS24" V 9545 4068 50  0000 L CNN
F 2 "Diodes_SMD:D_SMB" V 9500 4000 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/427/ss22-59686.pdf" V 9500 4000 50  0001 C CNN
F 4 "625-SS24-E3" V 9500 4000 50  0001 C CNN "Mouser"
	1    9500 4000
	0    1    1    0   
$EndComp
$Comp
L Device:CP C1
U 1 1 5D6E0E38
P 8200 4050
F 0 "C1" H 8318 4096 50  0000 L CNN
F 1 "100uF/50V" H 8318 4005 50  0000 L CNN
F 2 "Capacitors_SMD:CP_Elec_8x10" H 8238 3900 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ABA0000C1184-947404.pdf" H 8200 4050 50  0001 C CNN
F 4 "667-EEE-FP1H101AV" H 8200 4050 50  0001 C CNN "Mouser"
	1    8200 4050
	1    0    0    -1  
$EndComp
$Comp
L pspice:INDUCTOR L1
U 1 1 5D6EE7D4
P 9850 3500
F 0 "L1" H 9850 3715 50  0000 C CNN
F 1 "150uH" H 9850 3624 50  0000 C CNN
F 2 "Inductors_SMD:L_Neosid_Ms95a" H 9850 3500 50  0001 C CNN
F 3 "~" H 9850 3500 50  0001 C CNN
	1    9850 3500
	1    0    0    -1  
$EndComp
Text Label 7000 4200 0    50   ~ 0
HVAC_COMMON
Wire Wire Line
	7000 4200 8200 4200
Wire Wire Line
	10950 4200 10550 4200
Connection ~ 8200 4200
Wire Wire Line
	9500 4100 9500 4200
Connection ~ 9500 4200
Wire Wire Line
	9500 4200 8900 4200
Wire Wire Line
	9400 3700 9500 3700
Wire Wire Line
	9500 3700 9500 3900
Wire Wire Line
	9400 3500 9500 3500
Wire Wire Line
	9500 3700 9500 3500
Connection ~ 9500 3700
Connection ~ 9500 3500
Wire Wire Line
	9500 3500 9600 3500
Wire Wire Line
	9500 3700 10200 3700
Wire Wire Line
	10200 4000 10200 4200
Wire Wire Line
	10200 4200 9500 4200
Wire Wire Line
	10100 3500 10200 3500
Wire Wire Line
	10200 3500 10200 3700
Wire Wire Line
	8000 3500 8200 3500
Wire Wire Line
	8900 3900 8900 4200
Connection ~ 8900 4200
Wire Wire Line
	8900 4200 8400 4200
Wire Wire Line
	8400 4200 8200 4200
Connection ~ 8400 4200
Wire Wire Line
	8400 3700 8400 4200
Text Label 10950 3500 2    50   ~ 0
PWR_5V
Wire Wire Line
	10950 3500 10550 3500
Wire Wire Line
	8200 3900 8200 3500
Connection ~ 8200 3500
Wire Wire Line
	8200 3500 8400 3500
$Comp
L Device:LED D3
U 1 1 5D754FCE
P 10550 3650
F 0 "D3" V 10589 3533 50  0000 R CNN
F 1 "LED" V 10498 3533 50  0000 R CNN
F 2 "LEDs:LED_0805" H 10550 3650 50  0001 C CNN
F 3 "~" H 10550 3650 50  0001 C CNN
	1    10550 3650
	0    -1   -1   0   
$EndComp
$Comp
L Device:R_US R1
U 1 1 5D7582DF
P 10550 3950
F 0 "R1" H 10618 3996 50  0000 L CNN
F 1 "1k" H 10618 3905 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 10590 3940 50  0001 C CNN
F 3 "~" H 10550 3950 50  0001 C CNN
	1    10550 3950
	1    0    0    -1  
$EndComp
Wire Wire Line
	10550 4200 10550 4100
Wire Wire Line
	10550 4200 10200 4200
Connection ~ 10550 4200
Connection ~ 10200 4200
Wire Wire Line
	10550 3500 10200 3500
Connection ~ 10550 3500
Connection ~ 10200 3500
$Comp
L Device:CP C2
U 1 1 5D767EF7
P 10200 3850
F 0 "C2" H 10318 3896 50  0000 L CNN
F 1 "100uF/50V" H 10318 3805 50  0000 L CNN
F 2 "Capacitors_SMD:CP_Elec_8x10" H 10238 3700 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ABA0000C1184-947404.pdf" H 10200 3850 50  0001 C CNN
F 4 "667-EEE-FP1H101AV" H 10200 3850 50  0001 C CNN "Mouser"
	1    10200 3850
	1    0    0    -1  
$EndComp
Connection ~ 10200 3700
$EndSCHEMATC
