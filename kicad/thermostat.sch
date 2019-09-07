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
F 3 "https://www.mouser.com/datasheet/2/418/NG_CD_534998_P7-1253073.pdf" H -2250 1050 50  0001 C CNN
F 4 "485-2243" H 2600 2000 50  0001 C CNN "Mouser"
F 5 "1" H 2600 2000 50  0001 C CNN "Populate"
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
Text Label 8650 1500 0    50   ~ 0
HVAC_PWR(RED)
Text Label 8650 1600 0    50   ~ 0
HVAC_HEAT(WHITE)
Text Label 8650 1700 0    50   ~ 0
HVAC_COOL(YELLOW)
Text Label 8650 1800 0    50   ~ 0
HVAC_FAN(GREEN)
Wire Wire Line
	8650 1500 9450 1500
Wire Wire Line
	9450 1600 8650 1600
Wire Wire Line
	8650 1700 9450 1700
Wire Wire Line
	8650 1800 9450 1800
$Comp
L thermostat:Relay? RELAY1
U 1 1 5D5E9059
P 6200 1250
F 0 "RELAY1" V 6350 1450 50  0001 C CNN
F 1 "RELAY_FAN" H 6200 1573 50  0000 C CNN
F 2 "project_footprints:AGQ210A03" V 6350 1450 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/mech_eng_gq-1299323.pdf" V 6350 1450 50  0001 C CNN
F 4 "769-AGQ210A03" H 6200 1250 50  0001 C CNN "Mouser"
F 5 "1" H 6200 1250 50  0001 C CNN "Populate"
	1    6200 1250
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical MK1
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
L thermostat:Mounting_Hole-Mechanical MK2
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
L thermostat:Mounting_Hole-Mechanical MK3
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
L thermostat:Mounting_Hole-Mechanical MK4
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
L thermostat:Relay? RELAY2
U 1 1 5D5EC4AE
P 6200 1950
F 0 "RELAY2" V 6350 2150 50  0001 C CNN
F 1 "RELAY_HEAT" H 6200 2273 50  0000 C CNN
F 2 "project_footprints:AGQ210A03" V 6350 2150 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/mech_eng_gq-1299323.pdf" V 6350 2150 50  0001 C CNN
F 4 "769-AGQ210A03" H 6200 1950 50  0001 C CNN "Mouser"
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
L thermostat:Relay? RELAY3
U 1 1 5D5EE68E
P 6200 2650
F 0 "RELAY3" V 6350 2850 50  0001 C CNN
F 1 "RELAY_COOL" H 6200 2973 50  0000 C CNN
F 2 "project_footprints:AGQ210A03" V 6350 2850 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/mech_eng_gq-1299323.pdf" V 6350 2850 50  0001 C CNN
F 4 "769-AGQ210A03" H 6200 2650 50  0001 C CNN "Mouser"
F 5 "1" V 6200 2650 50  0001 C CNN "Populate"
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
L Switch:SW_Push SW_GPIO16
U 1 1 5D59E237
P 1900 4300
F 0 "SW_GPIO16" H 1900 4493 50  0000 C CNN
F 1 "GPIO16" H 1900 4494 50  0001 C CNN
F 2 "Buttons_Switches_SMD:SW_SPST_EVPBF" H 1900 4500 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ATK0000C432-1596775.pdf" H 1900 4500 50  0001 C CNN
F 4 "667-EVP-BFAC1A000" H 1900 4300 50  0001 C CNN "Mouser"
F 5 "1" H 1900 4300 50  0001 C CNN "Populate"
	1    1900 4300
	1    0    0    -1  
$EndComp
Text HLabel 3800 750  0    50   Input ~ 0
TEST
$Comp
L Connector_Generic:Conn_01x04 J1
U 1 1 5D66FD1D
P 9650 2950
F 0 "J1" H 9730 2942 50  0000 L CNN
F 1 "Display i2c" H 9730 2851 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x04_Pitch2.54mm" H 9650 2950 50  0001 C CNN
F 3 "~" H 9650 2950 50  0001 C CNN
F 4 "99" H 9650 2950 50  0001 C CNN "Populate"
F 5 "538-22-28-4044" H 9650 2950 50  0001 C CNN "Mouser"
	1    9650 2950
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x04 J2
U 1 1 5D67AFA8
P 9650 3450
F 0 "J2" H 9730 3442 50  0000 L CNN
F 1 "Sensor i2c" H 9730 3351 50  0000 L CNN
F 2 "Socket_Strips:Socket_Strip_Straight_1x04_Pitch2.54mm" H 9650 3450 50  0001 C CNN
F 3 "~" H 9650 3450 50  0001 C CNN
F 4 "99" H 9650 3450 50  0001 C CNN "Populate"
F 5 "200-SLW10401SS" H 9650 3450 50  0001 C CNN "Mouser"
	1    9650 3450
	1    0    0    -1  
$EndComp
Text Label 9250 2850 2    50   ~ 0
GND
Text Label 9250 2950 2    50   ~ 0
PWR_5V
Text Label 9250 3050 2    50   ~ 0
GPIO2(SDA1)
Text Label 9250 3150 2    50   ~ 0
GPIO3(SCL1)
Text Label 9250 3350 2    50   ~ 0
GPIO2(SDA1)
Text Label 9250 3450 2    50   ~ 0
GPIO3(SCL1)
Text Label 9250 3550 2    50   ~ 0
GND
Text Label 9250 3650 2    50   ~ 0
PWR_5V
Wire Wire Line
	9250 2850 9450 2850
Wire Wire Line
	9250 2950 9450 2950
Wire Wire Line
	9450 3050 9250 3050
Wire Wire Line
	9250 3150 9450 3150
Wire Wire Line
	9450 3350 9250 3350
Wire Wire Line
	9450 3450 9250 3450
Wire Wire Line
	9250 3550 9450 3550
Wire Wire Line
	9450 3650 9250 3650
$Comp
L thermostat:LM2596S-12-RENUM IC1
U 1 1 5D6B23A7
P 6650 4750
F 0 "IC1" H 6650 5117 50  0000 C CNN
F 1 "LM2596S-5" H 6650 5026 50  0000 C CNN
F 2 "project_footprints:TO170P1435X465-6N" H 6700 4500 50  0001 L CIN
F 3 "http://www.ti.com/lit/ds/symlink/lm2596.pdf" H 6650 4750 50  0001 C CNN
F 4 "926-LM2596S-50" H 6650 4750 50  0001 C CNN "Mouser"
F 5 "1" H 6650 4750 50  0001 C CNN "Populate"
	1    6650 4750
	1    0    0    -1  
$EndComp
$Comp
L Connector:Screw_Terminal_01x05 J6
U 1 1 5D6C475A
P 9650 1700
F 0 "J6" H 9730 1742 50  0000 L CNN
F 1 "Screw_Terminal_01x05" H 9730 1651 50  0000 L CNN
F 2 "project_footprints:CUI_TB004-508-05BE" H 9650 1700 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/670/tb004-508-1550640.pdf" H 9650 1700 50  0001 C CNN
F 4 "490-TB004-508-05BE" H 9650 1700 50  0001 C CNN "Mouser"
F 5 "1" H 9650 1700 50  0001 C CNN "Populate"
	1    9650 1700
	1    0    0    -1  
$EndComp
Text Label 8650 1900 0    50   ~ 0
HVAC_COMMON
Wire Wire Line
	8650 1900 9450 1900
Text Label 4350 4650 0    50   ~ 0
HVAC_PWR(RED)
Wire Wire Line
	4350 4650 5150 4650
Text Label 9000 5350 2    50   ~ 0
GND
$Comp
L Device:D_Small D1
U 1 1 5D6DC8DD
P 5250 4650
F 0 "D1" H 5250 4445 50  0000 C CNN
F 1 "S1A" H 5250 4536 50  0000 C CNN
F 2 "Diodes_SMD:D_SOD-123F" V 5250 4650 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/308/US1AFA-1301710.pdf" V 5250 4650 50  0001 C CNN
F 4 "512-US1AFA" H 5250 4650 50  0001 C CNN "Mouser"
F 5 "1" H 5250 4650 50  0001 C CNN "Populate"
	1    5250 4650
	-1   0    0    1   
$EndComp
$Comp
L Device:D_Small D2
U 1 1 5D6DD814
P 7250 5150
F 0 "D2" V 7204 5218 50  0000 L CNN
F 1 "SS24" V 7295 5218 50  0000 L CNN
F 2 "Diodes_SMD:D_SMB" V 7250 5150 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/427/ss22-59686.pdf" V 7250 5150 50  0001 C CNN
F 4 "625-SS24-E3" V 7250 5150 50  0001 C CNN "Mouser"
F 5 "1" H 7250 5150 50  0001 C CNN "Populate"
	1    7250 5150
	0    1    1    0   
$EndComp
$Comp
L pspice:INDUCTOR L1
U 1 1 5D6EE7D4
P 7600 4650
F 0 "L1" H 7600 4865 50  0000 C CNN
F 1 "150uH" H 7600 4774 50  0000 C CNN
F 2 "Inductors_SMD:L_Wuerth_WE-PD-Typ-M-Typ-S" H 7600 4650 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/445/7447773151-1526088.pdf" H 7600 4650 50  0001 C CNN
F 4 "710-7447773151" H 7600 4650 50  0001 C CNN "Mouser"
F 5 "1" H 7600 4650 50  0001 C CNN "Populate"
	1    7600 4650
	1    0    0    -1  
$EndComp
Text Label 4350 5350 0    50   ~ 0
HVAC_COMMON
Wire Wire Line
	9000 5350 8600 5350
Wire Wire Line
	7250 5250 7250 5350
Connection ~ 7250 5350
Wire Wire Line
	7250 5350 6650 5350
Wire Wire Line
	7950 5150 7950 5350
Wire Wire Line
	7950 5350 7250 5350
Wire Wire Line
	7950 4650 7950 4850
Wire Wire Line
	5350 4650 5550 4650
Wire Wire Line
	6650 5050 6650 5350
Connection ~ 6650 5350
Wire Wire Line
	6650 5350 6150 5350
Wire Wire Line
	6150 4850 6150 5350
Text Label 9000 4650 2    50   ~ 0
PWR_5V
Wire Wire Line
	9000 4650 8600 4650
Wire Wire Line
	5550 5050 5550 4650
$Comp
L Device:LED D3
U 1 1 5D754FCE
P 8600 4800
F 0 "D3" V 8639 4683 50  0000 R CNN
F 1 "LED" V 8548 4683 50  0000 R CNN
F 2 "LEDs:LED_0805" H 8600 4800 50  0001 C CNN
F 3 "~" H 8600 4800 50  0001 C CNN
F 4 "1" H 8600 4800 50  0001 C CNN "Populate"
	1    8600 4800
	0    -1   -1   0   
$EndComp
$Comp
L Device:R_US R1
U 1 1 5D7582DF
P 8600 5100
F 0 "R1" H 8668 5146 50  0000 L CNN
F 1 "1k" H 8668 5055 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 8640 5090 50  0001 C CNN
F 3 "~" H 8600 5100 50  0001 C CNN
F 4 "1" H 8600 5100 50  0001 C CNN "Populate"
	1    8600 5100
	1    0    0    -1  
$EndComp
Wire Wire Line
	8600 5350 8600 5250
$Comp
L Device:CP C2
U 1 1 5D767EF7
P 7950 5000
F 0 "C2" H 8068 5046 50  0000 L CNN
F 1 "100uF/50V" H 8068 4955 50  0000 L CNN
F 2 "Capacitors_SMD:CP_Elec_8x10" H 7988 4850 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ABA0000C1184-947404.pdf" H 7950 5000 50  0001 C CNN
F 4 "667-EEE-FP1H101AV" H 7950 5000 50  0001 C CNN "Mouser"
F 5 "1" H 7950 5000 50  0001 C CNN "Populate"
	1    7950 5000
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical Pi1
U 1 1 5D6C5FE0
P 800 6550
F 0 "Pi1" H 900 6596 50  0000 L CNN
F 1 "PiZero" H 900 6505 50  0000 L CNN
F 2 "project_footprints:RasperryPi_Zero" H 800 6550 50  0001 C CNN
F 3 "" H 800 6550 50  0001 C CNN
	1    800  6550
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical Gr1
U 1 1 5D6CA3D9
P 800 6300
F 0 "Gr1" H 900 6346 50  0000 L CNN
F 1 "Logo" H 900 6255 50  0000 L CNN
F 2 "project_footprints:LlamaHead" H 800 6300 50  0001 C CNN
F 3 "" H 800 6300 50  0001 C CNN
	1    800  6300
	1    0    0    -1  
$EndComp
Wire Wire Line
	7950 4650 7850 4650
Wire Wire Line
	7150 4650 7250 4650
Wire Wire Line
	7150 4850 7950 4850
Connection ~ 7950 4850
Wire Wire Line
	7250 5050 7250 4650
Connection ~ 7250 4650
Wire Wire Line
	7250 4650 7350 4650
Wire Wire Line
	4350 5350 5550 5350
$Comp
L Device:CP C1
U 1 1 5D6E0E38
P 5550 5200
F 0 "C1" H 5668 5246 50  0000 L CNN
F 1 "100uF/50V" H 5668 5155 50  0000 L CNN
F 2 "Capacitors_SMD:CP_Elec_8x10" H 5588 5050 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ABA0000C1184-947404.pdf" H 5550 5200 50  0001 C CNN
F 4 "667-EEE-FP1H101AV" H 5550 5200 50  0001 C CNN "Mouser"
F 5 "1" H 5550 5200 50  0001 C CNN "Populate"
	1    5550 5200
	1    0    0    -1  
$EndComp
Wire Wire Line
	7950 4650 8600 4650
Connection ~ 7950 4650
Connection ~ 8600 4650
Wire Wire Line
	8600 5350 7950 5350
Connection ~ 8600 5350
Connection ~ 7950 5350
Wire Wire Line
	6150 4650 5550 4650
Connection ~ 5550 4650
Wire Wire Line
	6150 5350 5550 5350
Connection ~ 6150 5350
Connection ~ 5550 5350
$Comp
L Switch:SW_Push SW_GPIO20
U 1 1 5D6D34AF
P 1900 4750
F 0 "SW_GPIO20" H 1900 4943 50  0000 C CNN
F 1 "GPIO20" H 1900 4944 50  0001 C CNN
F 2 "Buttons_Switches_SMD:SW_SPST_EVPBF" H 1900 4950 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ATK0000C432-1596775.pdf" H 1900 4950 50  0001 C CNN
F 4 "667-EVP-BFAC1A000" H 1900 4750 50  0001 C CNN "Mouser"
F 5 "1" H 1900 4750 50  0001 C CNN "Populate"
	1    1900 4750
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_Push SW_GPIO21
U 1 1 5D6D75B1
P 1900 5200
F 0 "SW_GPIO21" H 1900 5393 50  0000 C CNN
F 1 "GPIO21" H 1900 5394 50  0001 C CNN
F 2 "Buttons_Switches_SMD:SW_SPST_EVPBF" H 1900 5400 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ATK0000C432-1596775.pdf" H 1900 5400 50  0001 C CNN
F 4 "667-EVP-BFAC1A000" H 1900 5200 50  0001 C CNN "Mouser"
F 5 "1" H 1900 5200 50  0001 C CNN "Populate"
	1    1900 5200
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_Push SW_GPIO12
U 1 1 5D6DB82D
P 1900 5650
F 0 "SW_GPIO12" H 1900 5843 50  0000 C CNN
F 1 "GPIO12" H 1900 5844 50  0001 C CNN
F 2 "Buttons_Switches_SMD:SW_SPST_EVPBF" H 1900 5850 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ATK0000C432-1596775.pdf" H 1900 5850 50  0001 C CNN
F 4 "667-EVP-BFAC1A000" H 1900 5650 50  0001 C CNN "Mouser"
F 5 "1" H 1900 5650 50  0001 C CNN "Populate"
	1    1900 5650
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical MH1
U 1 1 5D6D64DA
P 1450 6300
F 0 "MH1" H 1550 6346 50  0000 L CNN
F 1 "Mounting_Hole-Wall" H 1550 6255 50  0000 L CNN
F 2 "Mounting_Holes:MountingHole_5mm" H 1450 6300 50  0001 C CNN
F 3 "" H 1450 6300 50  0001 C CNN
	1    1450 6300
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical MH2
U 1 1 5D6E2454
P 1450 6550
F 0 "MH2" H 1550 6596 50  0000 L CNN
F 1 "Mounting_Hole-Wall" H 1550 6505 50  0000 L CNN
F 2 "Mounting_Holes:MountingHole_5mm" H 1450 6550 50  0001 C CNN
F 3 "" H 1450 6550 50  0001 C CNN
	1    1450 6550
	1    0    0    -1  
$EndComp
$EndSCHEMATC
