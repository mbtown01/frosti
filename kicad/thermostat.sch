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
	2600 1100 2400 1100
Wire Wire Line
	2600 1200 2400 1200
Wire Wire Line
	2500 1300 2500 1700
Wire Wire Line
	2500 2700 2400 2700
Wire Wire Line
	2500 2500 2400 2500
Connection ~ 2500 2700
Wire Wire Line
	2500 2000 2400 2000
Connection ~ 2500 2500
Wire Wire Line
	2500 1700 2400 1700
Connection ~ 2500 2000
Wire Wire Line
	1800 3000 1900 3000
Wire Wire Line
	1800 1500 1800 2300
Wire Wire Line
	1800 2300 1900 2300
Connection ~ 1800 3000
Wire Wire Line
	1700 1900 1900 1900
Wire Wire Line
	1700 1100 1900 1100
Wire Wire Line
	1800 1500 1900 1500
Connection ~ 1800 2300
Wire Wire Line
	1900 1200 750  1200
Wire Wire Line
	750  1300 1900 1300
Wire Wire Line
	750  1400 1900 1400
Wire Wire Line
	1900 1600 750  1600
Wire Wire Line
	750  1700 1900 1700
Wire Wire Line
	750  1800 1900 1800
Wire Wire Line
	1900 2000 750  2000
Wire Wire Line
	750  2100 1900 2100
Wire Wire Line
	750  2200 1900 2200
Wire Wire Line
	1900 2400 750  2400
Wire Wire Line
	750  2500 1900 2500
Wire Wire Line
	750  2600 1900 2600
Wire Wire Line
	1900 2700 750  2700
Wire Wire Line
	750  2800 1900 2800
Wire Wire Line
	750  2900 1900 2900
Wire Wire Line
	2400 2800 3450 2800
Wire Wire Line
	2400 2900 3450 2900
Wire Wire Line
	2400 2300 3450 2300
Wire Wire Line
	2400 2400 3450 2400
Wire Wire Line
	2400 2100 3450 2100
Wire Wire Line
	2400 2200 3450 2200
Wire Wire Line
	2400 1800 3450 1800
Wire Wire Line
	2400 1900 3450 1900
Wire Wire Line
	2400 1500 3450 1500
Wire Wire Line
	2400 1600 3450 1600
Wire Wire Line
	2400 1400 3450 1400
Wire Wire Line
	2400 2600 3450 2600
Text Label 750  1200 0    50   ~ 0
GPIO2(SDA1)
Text Label 750  1300 0    50   ~ 0
GPIO3(SCL1)
Text Label 750  1400 0    50   ~ 0
GPIO4(GCLK)
Text Label 750  1600 0    50   ~ 0
GPIO17(GEN0)
Text Label 750  1700 0    50   ~ 0
GPIO27(GEN2)
Text Label 750  1800 0    50   ~ 0
GPIO22(GEN3)
Text Label 750  2000 0    50   ~ 0
GPIO10(SPI0_MOSI)
Text Label 750  2100 0    50   ~ 0
GPIO9(SPI0_MISO)
Text Label 750  2200 0    50   ~ 0
GPIO11(SPI0_SCK)
Text Label 750  2400 0    50   ~ 0
ID_SD
Text Label 750  2500 0    50   ~ 0
GPIO5
Text Label 750  2600 0    50   ~ 0
GPIO6
Text Label 750  2700 0    50   ~ 0
GPIO13(PWM1)
Text Label 750  2800 0    50   ~ 0
GPIO19(SPI1_MISO)
Text Label 750  2900 0    50   ~ 0
GPIO26
Text Label 3450 2900 2    50   ~ 0
GPIO20(SPI1_MOSI)
Text Label 3450 2800 2    50   ~ 0
GPIO16
Text Label 3450 2600 2    50   ~ 0
GPIO12(PWM0)
Text Label 3450 2400 2    50   ~ 0
ID_SC
Text Label 3450 2300 2    50   ~ 0
GPIO7(SPI1_CE_N)
Text Label 3450 2200 2    50   ~ 0
GPIO8(SPI0_CE_N)
Text Label 3450 2100 2    50   ~ 0
GPIO25(GEN6)
Text Label 3450 1900 2    50   ~ 0
GPIO24(GEN5)
Text Label 3450 1800 2    50   ~ 0
GPIO23(GEN4)
Text Label 3450 1600 2    50   ~ 0
GPIO18(GEN1)(PWM0)
Text Label 3450 1500 2    50   ~ 0
GPIO15(RXD0)
Text Label 3450 1400 2    50   ~ 0
GPIO14(TXD0)
Wire Wire Line
	2500 1300 2400 1300
Connection ~ 2500 1700
$Comp
L Connector_Generic:Conn_02x20_Odd_Even CONN1
U 1 1 59AD464A
P 2100 2000
F 0 "CONN1" H 2150 3117 50  0000 C CNN
F 1 "Conn_02x20_Odd_Even" H 2150 3026 50  0000 C CNN
F 2 "Socket_Strips:Socket_Strip_Straight_2x20_Pitch2.54mm" H -2750 1050 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/418/NG_CD_534998_P7-1253073.pdf" H -2750 1050 50  0001 C CNN
F 4 "485-2243" H 2100 2000 50  0001 C CNN "Mouser"
F 5 "1" H 2100 2000 50  0001 C CNN "Populate"
	1    2100 2000
	1    0    0    -1  
$EndComp
Text Label 3450 3000 2    50   ~ 0
GPIO21(SPI1_SCK)
Wire Wire Line
	2600 1100 2600 1200
Wire Wire Line
	2500 2500 2500 2700
Wire Wire Line
	2500 2000 2500 2500
Wire Wire Line
	1700 1100 1700 1900
Wire Wire Line
	1800 2300 1800 3000
Wire Wire Line
	2500 1700 2500 2000
Text Label 2600 750  0    50   ~ 0
PWR_5V
Text Label 1700 750  0    50   ~ 0
PWR_3.3V
Connection ~ 2600 1100
Wire Wire Line
	2600 1100 2600 750 
Wire Wire Line
	1700 1100 1700 750 
Connection ~ 1700 1100
Wire Wire Line
	2500 2700 2500 3200
Wire Wire Line
	1800 3000 1800 3200
Wire Wire Line
	1800 3200 2150 3200
Text Label 6600 1400 0    50   ~ 0
HVAC_PWR(RED)
Text Label 6600 1500 0    50   ~ 0
HVAC_HEAT(WHITE)
Text Label 6600 1600 0    50   ~ 0
HVAC_COOL(YELLOW)
Text Label 6600 1700 0    50   ~ 0
HVAC_FAN(GREEN)
Wire Wire Line
	6600 1400 7400 1400
Wire Wire Line
	7400 1500 6600 1500
Wire Wire Line
	6600 1600 7400 1600
Wire Wire Line
	6600 1700 7400 1700
$Comp
L thermostat-rescue:Relay?-thermostat RELAY1
U 1 1 5D5E9059
P 5150 1500
F 0 "RELAY1" V 5300 1700 50  0001 C CNN
F 1 "RELAY_FAN" H 5150 1823 50  0000 C CNN
F 2 "project_footprints:AGQ210A03" V 5300 1700 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/mech_eng_gq-1299323.pdf" V 5300 1700 50  0001 C CNN
F 4 "769-AGQ210A03" H 5150 1500 50  0001 C CNN "Mouser"
F 5 "1" H 5150 1500 50  0001 C CNN "Populate"
	1    5150 1500
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical MK1
U 1 1 5D5E9722
P 8250 5850
F 0 "MK1" H 8350 5896 50  0000 L CNN
F 1 "Mounting_Hole-Mechanical" H 8350 5805 50  0000 L CNN
F 2 "Mounting_Holes:MountingHole_2.5mm_Pad" H 8250 5850 50  0001 C CNN
F 3 "" H 8250 5850 50  0001 C CNN
	1    8250 5850
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical MK2
U 1 1 5D5F78A7
P 8250 6100
F 0 "MK2" H 8350 6146 50  0000 L CNN
F 1 "Mounting_Hole-Mechanical" H 8350 6055 50  0000 L CNN
F 2 "Mounting_Holes:MountingHole_2.5mm_Pad" H 8250 6100 50  0001 C CNN
F 3 "" H 8250 6100 50  0001 C CNN
	1    8250 6100
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical MK3
U 1 1 5D5F9275
P 6850 5800
F 0 "MK3" H 6950 5846 50  0000 L CNN
F 1 "Mounting_Hole-Mechanical" H 6950 5755 50  0000 L CNN
F 2 "Mounting_Holes:MountingHole_2.5mm_Pad" H 6850 5800 50  0001 C CNN
F 3 "" H 6850 5800 50  0001 C CNN
	1    6850 5800
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical MK4
U 1 1 5D5FAC9B
P 6850 6050
F 0 "MK4" H 6950 6096 50  0000 L CNN
F 1 "Mounting_Hole-Mechanical" H 6950 6005 50  0000 L CNN
F 2 "Mounting_Holes:MountingHole_2.5mm_Pad" H 6850 6050 50  0001 C CNN
F 3 "" H 6850 6050 50  0001 C CNN
	1    6850 6050
	1    0    0    -1  
$EndComp
Text Label 5600 1300 0    50   ~ 0
GPIO17(GEN0)
Wire Wire Line
	5600 1300 5400 1300
Wire Wire Line
	4900 1550 4700 1550
Text Label 4700 1550 2    50   ~ 0
HVAC_PWR(RED)
$Comp
L thermostat-rescue:Relay?-thermostat RELAY2
U 1 1 5D5EC4AE
P 5150 2200
F 0 "RELAY2" V 5300 2400 50  0001 C CNN
F 1 "RELAY_HEAT" H 5150 2523 50  0000 C CNN
F 2 "project_footprints:AGQ210A03" V 5300 2400 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/mech_eng_gq-1299323.pdf" V 5300 2400 50  0001 C CNN
F 4 "769-AGQ210A03" H 5150 2200 50  0001 C CNN "Mouser"
F 5 "1" H 5150 2200 50  0001 C CNN "Populate"
	1    5150 2200
	1    0    0    -1  
$EndComp
Text Label 5600 2000 0    50   ~ 0
GPIO27(GEN2)
Wire Wire Line
	5600 2000 5400 2000
Wire Wire Line
	4900 2000 4700 2000
Wire Wire Line
	4900 2150 4700 2150
Wire Wire Line
	4900 2250 4700 2250
Text Label 4700 2000 2    50   ~ 0
GPIO6
Text Label 4700 2150 2    50   ~ 0
HVAC_HEAT(WHITE)
Text Label 4700 2250 2    50   ~ 0
HVAC_PWR(RED)
$Comp
L thermostat-rescue:Relay?-thermostat RELAY3
U 1 1 5D5EE68E
P 5150 2900
F 0 "RELAY3" V 5300 3100 50  0001 C CNN
F 1 "RELAY_COOL" H 5150 3223 50  0000 C CNN
F 2 "project_footprints:AGQ210A03" V 5300 3100 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/mech_eng_gq-1299323.pdf" V 5300 3100 50  0001 C CNN
F 4 "769-AGQ210A03" H 5150 2900 50  0001 C CNN "Mouser"
F 5 "1" V 5150 2900 50  0001 C CNN "Populate"
	1    5150 2900
	1    0    0    -1  
$EndComp
Text Label 5600 2700 0    50   ~ 0
GPIO22(GEN3)
Wire Wire Line
	5600 2700 5400 2700
Wire Wire Line
	4900 2700 4700 2700
Wire Wire Line
	4900 2850 4700 2850
Wire Wire Line
	4900 2950 4700 2950
Text Label 4700 2700 2    50   ~ 0
GPIO13(PWM1)
Text Label 4700 2850 2    50   ~ 0
HVAC_COOL(YELLOW)
Text Label 4700 2950 2    50   ~ 0
HVAC_PWR(RED)
Wire Wire Line
	10150 1350 10550 1350
Wire Wire Line
	10150 1800 10550 1800
Wire Wire Line
	10150 2250 10550 2250
Wire Wire Line
	10150 2700 10550 2700
Text Label 10550 2700 0    50   ~ 0
PWR_5V
Text Label 10550 2250 0    50   ~ 0
PWR_5V
Text Label 10550 1800 0    50   ~ 0
PWR_5V
Text Label 10550 1350 0    50   ~ 0
PWR_5V
Wire Wire Line
	9750 2700 8900 2700
Wire Wire Line
	9750 2250 8900 2250
Wire Wire Line
	9750 1800 8900 1800
Wire Wire Line
	9750 1350 8900 1350
Text Label 8900 2700 0    50   ~ 0
GPIO12(PWM0)
Text Label 8900 2250 0    50   ~ 0
GPIO21(SPI1_SCK)
Text Label 8900 1800 0    50   ~ 0
GPIO20(SPI1_MOSI)
Text Label 8900 1350 0    50   ~ 0
GPIO16
$Comp
L Switch:SW_Push SW_GPIO16
U 1 1 5D59E237
P 9950 1350
F 0 "SW_GPIO16" H 9950 1543 50  0000 C CNN
F 1 "GPIO16" H 9950 1544 50  0001 C CNN
F 2 "Buttons_Switches_SMD:SW_SPST_EVPBF" H 9950 1550 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ATK0000C432-1596775.pdf" H 9950 1550 50  0001 C CNN
F 4 "667-EVP-BFAC1A000" H 9950 1350 50  0001 C CNN "Mouser"
F 5 "1" H 9950 1350 50  0001 C CNN "Populate"
	1    9950 1350
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x04 J1
U 1 1 5D66FD1D
P 7600 2150
F 0 "J1" H 7680 2142 50  0000 L CNN
F 1 "Display i2c" H 7680 2051 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x04_Pitch2.54mm" H 7600 2150 50  0001 C CNN
F 3 "~" H 7600 2150 50  0001 C CNN
F 4 "99" H 7600 2150 50  0001 C CNN "Populate"
F 5 "538-22-28-4044" H 7600 2150 50  0001 C CNN "Mouser"
	1    7600 2150
	1    0    0    -1  
$EndComp
Text Label 7200 2050 2    50   ~ 0
GND
Text Label 7200 2150 2    50   ~ 0
PWR_5V
Text Label 7200 2250 2    50   ~ 0
GPIO2(SDA1)
Text Label 7200 2350 2    50   ~ 0
GPIO3(SCL1)
Wire Wire Line
	7200 2050 7400 2050
Wire Wire Line
	7200 2150 7400 2150
Wire Wire Line
	7400 2250 7200 2250
Wire Wire Line
	7200 2350 7400 2350
$Comp
L thermostat:LM2596S-12-RENUM IC1
U 1 1 5D6B23A7
P 2450 3950
F 0 "IC1" H 2450 4317 50  0000 C CNN
F 1 "LM2596S-5" H 2450 4226 50  0000 C CNN
F 2 "TO_SOT_Packages_SMD:TO-263-5_TabPin3" H 2500 3700 50  0001 L CIN
F 3 "http://www.ti.com/lit/ds/symlink/lm2596.pdf" H 2450 3950 50  0001 C CNN
F 4 "926-LM2596S-50" H 2450 3950 50  0001 C CNN "Mouser"
F 5 "1" H 2450 3950 50  0001 C CNN "Populate"
	1    2450 3950
	1    0    0    -1  
$EndComp
$Comp
L Connector:Screw_Terminal_01x05 J6
U 1 1 5D6C475A
P 7600 1600
F 0 "J6" H 7680 1642 50  0000 L CNN
F 1 "Screw_Terminal_01x05" H 7680 1551 50  0000 L CNN
F 2 "project_footprints:CUI_TB004-508-05BE" H 7600 1600 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/670/tb004-508-1550640.pdf" H 7600 1600 50  0001 C CNN
F 4 "490-TB004-508-05BE" H 7600 1600 50  0001 C CNN "Mouser"
F 5 "1" H 7600 1600 50  0001 C CNN "Populate"
	1    7600 1600
	1    0    0    -1  
$EndComp
Text Label 6600 1800 0    50   ~ 0
HVAC_COMMON
Wire Wire Line
	6600 1800 7400 1800
Text Label 1450 3850 2    50   ~ 0
HVAC_PWR(RED)
Text Label 4250 4550 2    50   ~ 0
GND
$Comp
L Device:D_Small D2
U 1 1 5D6DD814
P 3000 4350
F 0 "D2" V 2954 4418 50  0000 L CNN
F 1 "SS24" V 3045 4418 50  0000 L CNN
F 2 "Diodes_SMD:D_SMB" V 3000 4350 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/427/ss22-59686.pdf" V 3000 4350 50  0001 C CNN
F 4 "625-SS24-E3" V 3000 4350 50  0001 C CNN "Mouser"
F 5 "1" H 3000 4350 50  0001 C CNN "Populate"
	1    3000 4350
	0    1    1    0   
$EndComp
$Comp
L pspice:INDUCTOR L1
U 1 1 5D6EE7D4
P 3300 3850
F 0 "L1" H 3300 4065 50  0000 C CNN
F 1 "150uH" H 3300 3974 50  0000 C CNN
F 2 "Inductors_SMD:L_Wuerth_WE-PD-Typ-M-Typ-S" H 3300 3850 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/445/7447773151-1526088.pdf" H 3300 3850 50  0001 C CNN
F 4 "710-7447773151" H 3300 3850 50  0001 C CNN "Mouser"
F 5 "1" H 3300 3850 50  0001 C CNN "Populate"
	1    3300 3850
	1    0    0    -1  
$EndComp
Text Label 1450 4550 2    50   ~ 0
HVAC_COMMON
Wire Wire Line
	4250 4550 3850 4550
Wire Wire Line
	2450 4250 2450 4550
Wire Wire Line
	2450 4550 1950 4550
Wire Wire Line
	1950 4050 1950 4550
Wire Wire Line
	1750 4250 1750 3850
$Comp
L Device:LED D3
U 1 1 5D754FCE
P 3850 4000
F 0 "D3" V 3889 3883 50  0000 R CNN
F 1 "LED" V 3798 3883 50  0000 R CNN
F 2 "LEDs:LED_0805" H 3850 4000 50  0001 C CNN
F 3 "~" H 3850 4000 50  0001 C CNN
F 4 "1" H 3850 4000 50  0001 C CNN "Populate"
	1    3850 4000
	0    -1   -1   0   
$EndComp
$Comp
L Device:R_US R1
U 1 1 5D7582DF
P 3850 4300
F 0 "R1" H 3918 4346 50  0000 L CNN
F 1 "1k" H 3918 4255 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 3890 4290 50  0001 C CNN
F 3 "~" H 3850 4300 50  0001 C CNN
F 4 "1" H 3850 4300 50  0001 C CNN "Populate"
	1    3850 4300
	1    0    0    -1  
$EndComp
Wire Wire Line
	3850 4550 3850 4450
$Comp
L Device:CP C2
U 1 1 5D767EF7
P 3600 4200
F 0 "C2" H 3400 4400 50  0000 L CNN
F 1 "100uF/50V" H 3100 4300 50  0000 L CNN
F 2 "Capacitors_SMD:CP_Elec_8x10" H 3638 4050 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ABA0000C1184-947404.pdf" H 3600 4200 50  0001 C CNN
F 4 "667-EEE-FP1H101AV" H 3600 4200 50  0001 C CNN "Mouser"
F 5 "1" H 3600 4200 50  0001 C CNN "Populate"
	1    3600 4200
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical Pi1
U 1 1 5D6C5FE0
P 9550 6100
F 0 "Pi1" H 9650 6146 50  0000 L CNN
F 1 "PiZero" H 9650 6055 50  0000 L CNN
F 2 "project_footprints:RasperryPi_Zero" H 9550 6100 50  0001 C CNN
F 3 "" H 9550 6100 50  0001 C CNN
	1    9550 6100
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical Gr1
U 1 1 5D6CA3D9
P 9550 5850
F 0 "Gr1" H 9650 5896 50  0000 L CNN
F 1 "Logo" H 9650 5805 50  0000 L CNN
F 2 "project_footprints:LlamaHead" H 9550 5850 50  0001 C CNN
F 3 "" H 9550 5850 50  0001 C CNN
	1    9550 5850
	1    0    0    -1  
$EndComp
$Comp
L Device:CP C1
U 1 1 5D6E0E38
P 1750 4400
F 0 "C1" H 1500 4550 50  0000 L CNN
F 1 "100uF/50V" H 1200 4450 50  0000 L CNN
F 2 "Capacitors_SMD:CP_Elec_8x10" H 1788 4250 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ABA0000C1184-947404.pdf" H 1750 4400 50  0001 C CNN
F 4 "667-EEE-FP1H101AV" H 1750 4400 50  0001 C CNN "Mouser"
F 5 "1" H 1750 4400 50  0001 C CNN "Populate"
	1    1750 4400
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_Push SW_GPIO20
U 1 1 5D6D34AF
P 9950 1800
F 0 "SW_GPIO20" H 9950 1993 50  0000 C CNN
F 1 "GPIO20" H 9950 1994 50  0001 C CNN
F 2 "Buttons_Switches_SMD:SW_SPST_EVPBF" H 9950 2000 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ATK0000C432-1596775.pdf" H 9950 2000 50  0001 C CNN
F 4 "667-EVP-BFAC1A000" H 9950 1800 50  0001 C CNN "Mouser"
F 5 "1" H 9950 1800 50  0001 C CNN "Populate"
	1    9950 1800
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_Push SW_GPIO21
U 1 1 5D6D75B1
P 9950 2250
F 0 "SW_GPIO21" H 9950 2443 50  0000 C CNN
F 1 "GPIO21" H 9950 2444 50  0001 C CNN
F 2 "Buttons_Switches_SMD:SW_SPST_EVPBF" H 9950 2450 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ATK0000C432-1596775.pdf" H 9950 2450 50  0001 C CNN
F 4 "667-EVP-BFAC1A000" H 9950 2250 50  0001 C CNN "Mouser"
F 5 "1" H 9950 2250 50  0001 C CNN "Populate"
	1    9950 2250
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_Push SW_GPIO12
U 1 1 5D6DB82D
P 9950 2700
F 0 "SW_GPIO12" H 9950 2893 50  0000 C CNN
F 1 "GPIO12" H 9950 2894 50  0001 C CNN
F 2 "Buttons_Switches_SMD:SW_SPST_EVPBF" H 9950 2900 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/315/ATK0000C432-1596775.pdf" H 9950 2900 50  0001 C CNN
F 4 "667-EVP-BFAC1A000" H 9950 2700 50  0001 C CNN "Mouser"
F 5 "1" H 9950 2700 50  0001 C CNN "Populate"
	1    9950 2700
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical MH1
U 1 1 5D6D64DA
P 10200 5850
F 0 "MH1" H 10300 5896 50  0000 L CNN
F 1 "Mounting_Hole-Wall" H 10300 5805 50  0000 L CNN
F 2 "Mounting_Holes:MountingHole_5mm" H 10200 5850 50  0001 C CNN
F 3 "" H 10200 5850 50  0001 C CNN
	1    10200 5850
	1    0    0    -1  
$EndComp
$Comp
L thermostat:Mounting_Hole-Mechanical MH2
U 1 1 5D6E2454
P 10200 6100
F 0 "MH2" H 10300 6146 50  0000 L CNN
F 1 "Mounting_Hole-Wall" H 10300 6055 50  0000 L CNN
F 2 "Mounting_Holes:MountingHole_5mm" H 10200 6100 50  0001 C CNN
F 3 "" H 10200 6100 50  0001 C CNN
	1    10200 6100
	1    0    0    -1  
$EndComp
$Comp
L Device:CP C11
U 1 1 5E139BCA
P 4000 6350
F 0 "C11" H 4118 6396 50  0000 L CNN
F 1 "25F" H 4118 6305 50  0000 L CNN
F 2 "Capacitors_THT:CP_Radial_D16.0mm_P7.50mm" H 4038 6200 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/87/eaton-hb-supercapacitor-data-sheet-1608755.pdf" H 4000 6350 50  0001 C CNN
F 4 "504-HB1625-2R5256-R" H 4000 6350 50  0001 C CNN "Mouser"
	1    4000 6350
	1    0    0    -1  
$EndComp
Text Label 1450 5150 2    50   ~ 0
PWR_5V_CAP_IN
Wire Wire Line
	2400 3000 3450 3000
$Comp
L Device:R_US R11
U 1 1 5E151833
P 1900 6050
F 0 "R11" H 1650 6050 50  0000 L CNN
F 1 "38.3k" H 1600 5950 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 1940 6040 50  0001 C CNN
F 3 "~" H 1900 6050 50  0001 C CNN
F 4 "1" H 1900 6050 50  0001 C CNN "Populate"
	1    1900 6050
	1    0    0    -1  
$EndComp
$Comp
L Device:C C12
U 1 1 5E1B5622
P 1900 5300
F 0 "C12" H 2015 5346 50  0000 L CNN
F 1 "2.2uF" H 2015 5255 50  0000 L CNN
F 2 "Capacitors_SMD:C_0805" H 1938 5150 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/40/AutoMLCC-777028.pdf" H 1900 5300 50  0001 C CNN
F 4 "581-08053C225K4T2A" H 1900 5300 50  0001 C CNN "Mouser"
	1    1900 5300
	1    0    0    -1  
$EndComp
$Comp
L Device:C C14
U 1 1 5E1B9F70
P 2750 7150
F 0 "C14" H 2500 7150 50  0000 L CNN
F 1 "1nF" H 2500 7050 50  0000 L CNN
F 2 "Capacitors_SMD:C_0805" H 2788 7000 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/212/KEM_C1090_X7R_ESD-1103328.pdf" H 2750 7150 50  0001 C CNN
F 4 "80-C0805C102KMRECAUT" H 2750 7150 50  0001 C CNN "Mouser"
	1    2750 7150
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R12
U 1 1 5E1BF857
P 2950 7150
F 0 "R12" H 3050 7150 50  0000 L CNN
F 1 "1k" H 3050 7050 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 2990 7140 50  0001 C CNN
F 3 "~" H 2950 7150 50  0001 C CNN
F 4 "1" H 2950 7150 50  0001 C CNN "Populate"
	1    2950 7150
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R15
U 1 1 5E1DD608
P 3400 5300
F 0 "R15" H 3150 5350 50  0000 L CNN
F 1 "1050k" H 3100 5250 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 3440 5290 50  0001 C CNN
F 3 "~" H 3400 5300 50  0001 C CNN
F 4 "1" H 3400 5300 50  0001 C CNN "Populate"
	1    3400 5300
	-1   0    0    1   
$EndComp
$Comp
L Device:R_US R16
U 1 1 5E1DD60F
P 3550 5800
F 0 "R16" V 3750 5700 50  0000 L CNN
F 1 "200k" V 3650 5700 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 3590 5790 50  0001 C CNN
F 3 "~" H 3550 5800 50  0001 C CNN
F 4 "1" H 3550 5800 50  0001 C CNN "Populate"
	1    3550 5800
	0    1    1    0   
$EndComp
$Comp
L Device:C C13
U 1 1 5E202618
P 3850 5300
F 0 "C13" H 3965 5346 50  0000 L CNN
F 1 "100uF" H 3965 5255 50  0000 L CNN
F 2 "Capacitors_SMD:C_0805" H 3888 5150 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/281/murata_03052018_GRM_Series_1-1310166.pdf" H 3850 5300 50  0001 C CNN
F 4 "81-GRM21BR60J107ME5L" H 3850 5300 50  0001 C CNN "Mouser"
	1    3850 5300
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R18
U 1 1 5E207CE6
P 2400 5150
F 0 "R18" V 2600 5050 50  0000 L CNN
F 1 "12m" V 2500 5050 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 2440 5140 50  0001 C CNN
F 3 "~" H 2400 5150 50  0001 C CNN
F 4 "1" H 2400 5150 50  0001 C CNN "Populate"
	1    2400 5150
	0    1    1    0   
$EndComp
$Comp
L thermostat:GND #PWR0101
U 1 1 5E217AC1
P 1900 5450
F 0 "#PWR0101" H 1900 5200 50  0001 C CNN
F 1 "GND" H 1905 5277 50  0000 C CNN
F 2 "" H 1900 5450 50  0000 C CNN
F 3 "" H 1900 5450 50  0000 C CNN
	1    1900 5450
	1    0    0    -1  
$EndComp
$Comp
L thermostat:GND #PWR0102
U 1 1 5E218EC3
P 4000 6500
F 0 "#PWR0102" H 4000 6250 50  0001 C CNN
F 1 "GND" H 4005 6327 50  0000 C CNN
F 2 "" H 4000 6500 50  0000 C CNN
F 3 "" H 4000 6500 50  0000 C CNN
	1    4000 6500
	1    0    0    -1  
$EndComp
$Comp
L thermostat:GND #PWR0103
U 1 1 5E219536
P 3850 5450
F 0 "#PWR0103" H 3850 5200 50  0001 C CNN
F 1 "GND" H 3855 5277 50  0000 C CNN
F 2 "" H 3850 5450 50  0000 C CNN
F 3 "" H 3850 5450 50  0000 C CNN
	1    3850 5450
	1    0    0    -1  
$EndComp
$Comp
L thermostat:GND #PWR0104
U 1 1 5E2198F5
P 2950 7300
F 0 "#PWR0104" H 2950 7050 50  0001 C CNN
F 1 "GND" H 2955 7127 50  0000 C CNN
F 2 "" H 2950 7300 50  0000 C CNN
F 3 "" H 2950 7300 50  0000 C CNN
	1    2950 7300
	1    0    0    -1  
$EndComp
$Comp
L thermostat:GND #PWR0105
U 1 1 5E21A536
P 2750 7300
F 0 "#PWR0105" H 2750 7050 50  0001 C CNN
F 1 "GND" H 2755 7127 50  0000 C CNN
F 2 "" H 2750 7300 50  0000 C CNN
F 3 "" H 2750 7300 50  0000 C CNN
	1    2750 7300
	1    0    0    -1  
$EndComp
$Comp
L thermostat:GND #PWR0106
U 1 1 5E21ACCA
P 1900 6200
F 0 "#PWR0106" H 1900 5950 50  0001 C CNN
F 1 "GND" H 1905 6027 50  0000 C CNN
F 2 "" H 1900 6200 50  0000 C CNN
F 3 "" H 1900 6200 50  0000 C CNN
	1    1900 6200
	1    0    0    -1  
$EndComp
$Comp
L thermostat:GND #PWR0107
U 1 1 5E21B2E1
P 3700 5800
F 0 "#PWR0107" H 3700 5550 50  0001 C CNN
F 1 "GND" H 3705 5627 50  0000 C CNN
F 2 "" H 3700 5800 50  0000 C CNN
F 3 "" H 3700 5800 50  0000 C CNN
	1    3700 5800
	1    0    0    -1  
$EndComp
Wire Wire Line
	3100 5800 3250 5800
Wire Wire Line
	3100 5900 3250 5900
Wire Wire Line
	3250 5900 3250 5800
Connection ~ 3250 5800
Wire Wire Line
	3250 5800 3400 5800
$Comp
L Device:L L2
U 1 1 5E2A01AC
P 3250 6200
F 0 "L2" V 3100 6200 50  0000 C CNN
F 1 "2.2uH" V 3200 6200 50  0000 C CNN
F 2 "Inductors_SMD:L_Coilcraft_XAL5030" H 3250 6200 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/597/xal50xx-270657.pdf" H 3250 6200 50  0001 C CNN
F 4 "994-XAL5030-222MEC" V 3250 6200 50  0001 C CNN "Mouser"
	1    3250 6200
	0    1    1    0   
$EndComp
$Comp
L thermostat:GND #PWR0108
U 1 1 5E21A15F
P 3550 6850
F 0 "#PWR0108" H 3550 6600 50  0001 C CNN
F 1 "GND" H 3555 6677 50  0000 C CNN
F 2 "" H 3550 6850 50  0000 C CNN
F 3 "" H 3550 6850 50  0000 C CNN
	1    3550 6850
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R14
U 1 1 5E1D2723
P 3550 6400
F 0 "R14" H 3650 6450 50  0000 L CNN
F 1 "698k" H 3650 6350 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 3590 6390 50  0001 C CNN
F 3 "~" H 3550 6400 50  0001 C CNN
F 4 "1" H 3550 6400 50  0001 C CNN "Populate"
	1    3550 6400
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R13
U 1 1 5E1CC50D
P 3550 6700
F 0 "R13" H 3650 6750 50  0000 L CNN
F 1 "348k" H 3650 6650 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 3590 6690 50  0001 C CNN
F 3 "~" H 3550 6700 50  0001 C CNN
F 4 "1" H 3550 6700 50  0001 C CNN "Populate"
	1    3550 6700
	1    0    0    -1  
$EndComp
Wire Wire Line
	3550 6250 3550 6200
Wire Wire Line
	3550 6200 3450 6200
Wire Wire Line
	3100 6350 3450 6350
Wire Wire Line
	3450 6350 3450 6200
Connection ~ 3450 6200
Wire Wire Line
	3450 6200 3400 6200
Wire Wire Line
	3100 6550 3550 6550
Connection ~ 3550 6550
$Comp
L thermostat:GND #PWR0109
U 1 1 5E300572
P 2250 7300
F 0 "#PWR0109" H 2250 7050 50  0001 C CNN
F 1 "GND" H 2255 7127 50  0000 C CNN
F 2 "" H 2250 7300 50  0000 C CNN
F 3 "" H 2250 7300 50  0000 C CNN
	1    2250 7300
	1    0    0    -1  
$EndComp
Wire Wire Line
	2550 7100 2400 7100
Connection ~ 2250 7100
Connection ~ 2400 7100
Wire Wire Line
	2400 7100 2250 7100
Wire Wire Line
	2100 7100 2250 7100
Wire Wire Line
	3550 6200 4000 6200
Connection ~ 3550 6200
Wire Wire Line
	3400 5450 3400 5800
Connection ~ 3400 5800
Wire Wire Line
	2850 5450 2950 5450
$Comp
L thermostat:LTC4041 U11
U 1 1 5E1374C4
P 2500 6250
F 0 "U11" V 2700 6350 50  0000 C CNN
F 1 "LTC4041" V 2600 6350 50  0000 C CNN
F 2 "project_footprints:ltc4041" H 1950 8400 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/609/LTC4041-1504291.pdf" H 2500 6500 50  0001 C CNN
F 4 "584-4041EUFDPB" H 2500 6250 50  0001 C CNN "Mouser"
	1    2500 6250
	1    0    0    -1  
$EndComp
Connection ~ 3100 6200
Wire Wire Line
	3100 6100 3100 6200
Wire Wire Line
	2550 7000 2550 7100
Wire Wire Line
	2400 7000 2400 7100
Wire Wire Line
	2250 7000 2250 7100
Wire Wire Line
	2100 6550 2100 7100
Wire Wire Line
	2250 5150 2250 5450
Wire Wire Line
	2550 5150 2550 5450
Connection ~ 2550 5150
Wire Wire Line
	2950 5450 3200 5450
Wire Wire Line
	3200 5450 3200 5150
Wire Wire Line
	3200 5150 3050 5150
Connection ~ 2950 5450
Wire Wire Line
	3200 5150 3400 5150
Connection ~ 3200 5150
Wire Wire Line
	2700 5400 2700 5450
Wire Wire Line
	3050 5250 3050 5150
Connection ~ 3050 5150
$Comp
L thermostat:SIR424DP U12
U 1 1 5E21048A
P 2900 5200
F 0 "U12" H 2750 5450 50  0000 L CNN
F 1 "SIR424DP" H 2600 5350 50  0000 L CNN
F 2 "Housings_SOIC:PowerPAK_SO-8_Single" V 2750 4950 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/427/sir424dp-244427.pdf" H 2900 5250 50  0001 C CNN
F 4 "781-SIR424DP-GE3" V 2850 5200 50  0001 C CNN "Mouser"
	1    2900 5200
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R10
U 1 1 5E14D4D6
P 1750 5900
F 0 "R10" V 1800 6200 50  0000 L CNN
F 1 "113k" V 1700 6200 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 1790 5890 50  0001 C CNN
F 3 "~" H 1750 5900 50  0001 C CNN
F 4 "1" H 1750 5900 50  0001 C CNN "Populate"
	1    1750 5900
	0    -1   -1   0   
$EndComp
Wire Wire Line
	1450 5150 1550 5150
Wire Wire Line
	4100 5150 3850 5150
Wire Wire Line
	3850 5150 3400 5150
Connection ~ 3850 5150
Connection ~ 3400 5150
Wire Wire Line
	1550 5150 1550 5900
Wire Wire Line
	1550 5900 1600 5900
Wire Wire Line
	1550 5150 1700 5150
Connection ~ 1550 5150
Wire Wire Line
	1900 5150 2250 5150
Connection ~ 1900 5150
Connection ~ 2250 5150
Wire Wire Line
	1900 5900 2100 5900
Connection ~ 1900 5900
Wire Wire Line
	2100 5800 1700 5800
Wire Wire Line
	1700 5800 1700 5150
Connection ~ 1700 5150
Wire Wire Line
	1700 5150 1900 5150
Wire Wire Line
	2250 7100 2250 7300
$Comp
L Device:D_Small D1
U 1 1 5D6DC8DD
P 1650 3850
F 0 "D1" H 1650 3645 50  0000 C CNN
F 1 "S1A" H 1650 3736 50  0000 C CNN
F 2 "Diodes_SMD:D_SOD-123F" V 1650 3850 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/308/US1AFA-1301710.pdf" V 1650 3850 50  0001 C CNN
F 4 "512-US1AFA" H 1650 3850 50  0001 C CNN "Mouser"
F 5 "1" H 1650 3850 50  0001 C CNN "Populate"
	1    1650 3850
	-1   0    0    1   
$EndComp
Wire Wire Line
	1450 4550 1750 4550
Wire Wire Line
	1750 4550 1950 4550
Connection ~ 1750 4550
Connection ~ 1950 4550
Wire Wire Line
	1750 3850 1950 3850
Connection ~ 1750 3850
Wire Wire Line
	1450 3850 1550 3850
Wire Wire Line
	3000 4450 3000 4550
Wire Wire Line
	3000 4550 2450 4550
Connection ~ 2450 4550
Wire Wire Line
	3000 4250 3000 3850
Wire Wire Line
	3000 3850 2950 3850
Wire Wire Line
	3050 3850 3000 3850
Connection ~ 3000 3850
Wire Wire Line
	3600 4050 3600 3850
Wire Wire Line
	3600 3850 3550 3850
Wire Wire Line
	3850 3850 3600 3850
Connection ~ 3600 3850
Wire Wire Line
	3600 4350 3600 4550
Wire Wire Line
	3600 4550 3000 4550
Connection ~ 3000 4550
Wire Wire Line
	3850 4550 3600 4550
Connection ~ 3850 4550
Connection ~ 3600 4550
Wire Wire Line
	2950 4050 3600 4050
Connection ~ 3600 4050
Text Label 4700 1450 2    50   ~ 0
HVAC_FAN(GREEN)
Text Label 4700 1300 2    50   ~ 0
GPIO5
Wire Wire Line
	4900 1450 4700 1450
Wire Wire Line
	4900 1300 4700 1300
Wire Wire Line
	4100 3850 3850 3850
Connection ~ 3850 3850
Text Label 6550 4050 0    50   ~ 0
PWR_5V
$Comp
L Connector_Generic:Conn_02x03_Odd_Even J31
U 1 1 5E3A0C5A
P 6150 4150
F 0 "J31" H 6200 4467 50  0000 C CNN
F 1 "Conn_02x03_Odd_Even" H 6200 4376 50  0000 C CNN
F 2 "Socket_Strips:Socket_Strip_Straight_2x03_Pitch2.54mm_SMD" H 6150 4150 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/181/M20-875-1273831.pdf" H 6150 4150 50  0001 C CNN
F 4 "855-M20-8750342" H 6150 4150 50  0001 C CNN "Mouser"
	1    6150 4150
	1    0    0    -1  
$EndComp
Text Label 4100 5150 0    50   ~ 0
PWR_5V_CAP
Text Label 4100 3850 0    50   ~ 0
PWR_5V_RAW
Text Label 6550 4150 0    50   ~ 0
PWR_5V_CAP_IN
Text Label 6550 4250 0    50   ~ 0
PWR_5V
Text Label 5850 4250 2    50   ~ 0
PWR_5V_CAP
Text Label 5850 4050 2    50   ~ 0
PWR_5V_RAW
Text Label 5850 4150 2    50   ~ 0
PWR_5V_RAW
Wire Wire Line
	5850 4050 5950 4050
Wire Wire Line
	5950 4150 5850 4150
Wire Wire Line
	5850 4250 5950 4250
Wire Wire Line
	6550 4250 6450 4250
Wire Wire Line
	6450 4150 6550 4150
Wire Wire Line
	6550 4050 6450 4050
Text Notes 5250 4500 0    50   ~ 0
To bypass supercapacitor circuit, jumper 1,2\nTo enable supercapacitor circuit, jumper 3,4 and 5,6
$Comp
L Sensor_Pressure:BMP280 U21
U 1 1 5E52B744
P 9400 4100
F 0 "U21" H 9630 4196 50  0000 L CNN
F 1 "BMP280" H 9630 4105 50  0000 L CNN
F 2 "Housings_LGA:Bosch_LGA-8_2.5x2.5mm_Pitch0.65mm_ClockwisePinNumbering" H 9400 3400 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/783/BST-BMP280-DS001-1509562.pdf" H 9400 4100 50  0001 C CNN
F 4 "262-BMP280" H 9400 4100 50  0001 C CNN "Mouser"
	1    9400 4100
	1    0    0    -1  
$EndComp
$Comp
L thermostat:GND #PWR0110
U 1 1 5E52C53F
P 9500 4450
F 0 "#PWR0110" H 9500 4200 50  0001 C CNN
F 1 "GND" H 9505 4277 50  0000 C CNN
F 2 "" H 9500 4450 50  0000 C CNN
F 3 "" H 9500 4450 50  0000 C CNN
	1    9500 4450
	1    0    0    -1  
$EndComp
Wire Wire Line
	9500 4400 9500 4450
Wire Wire Line
	9400 4400 9400 4450
Wire Wire Line
	9400 4450 9500 4450
Connection ~ 9500 4450
Text Label 9500 3400 2    50   ~ 0
PWR_3.3V
Text Label 8500 4300 3    50   ~ 0
GPIO2(SDA1)
Text Label 8800 4300 3    50   ~ 0
GPIO3(SCL1)
$Comp
L Device:R_US R21
U 1 1 5E560971
P 8950 4450
F 0 "R21" H 9050 4500 50  0000 L CNN
F 1 "10k" H 9050 4400 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 8990 4440 50  0001 C CNN
F 3 "~" H 8950 4450 50  0001 C CNN
F 4 "1" H 8950 4450 50  0001 C CNN "Populate"
	1    8950 4450
	1    0    0    -1  
$EndComp
$Comp
L thermostat:GND #PWR0111
U 1 1 5E568D5E
P 8950 4600
F 0 "#PWR0111" H 8950 4350 50  0001 C CNN
F 1 "GND" H 8955 4427 50  0000 C CNN
F 2 "" H 8950 4600 50  0000 C CNN
F 3 "" H 8950 4600 50  0000 C CNN
	1    8950 4600
	1    0    0    -1  
$EndComp
Wire Wire Line
	9000 4100 8950 4100
Wire Wire Line
	8950 4100 8950 4300
$Comp
L Device:C C21
U 1 1 5E5B7137
P 10100 3750
F 0 "C21" H 10215 3796 50  0000 L CNN
F 1 "1uF" H 10215 3705 50  0000 L CNN
F 2 "Capacitors_SMD:C_0805" H 10138 3600 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/212/KEM_C1023_X7R_AUTO_SMD-1093309.pdf" H 10100 3750 50  0001 C CNN
F 4 "80-C0805C105M8RAUTO" H 10100 3750 50  0001 C CNN "Mouser"
	1    10100 3750
	1    0    0    -1  
$EndComp
$Comp
L thermostat:GND #PWR0112
U 1 1 5E5B713D
P 10100 3900
F 0 "#PWR0112" H 10100 3650 50  0001 C CNN
F 1 "GND" H 10105 3727 50  0000 C CNN
F 2 "" H 10100 3900 50  0000 C CNN
F 3 "" H 10100 3900 50  0000 C CNN
	1    10100 3900
	1    0    0    -1  
$EndComp
$Comp
L Device:C C22
U 1 1 5E5BFD1A
P 10500 3750
F 0 "C22" H 10615 3796 50  0000 L CNN
F 1 "100nF" H 10615 3705 50  0000 L CNN
F 2 "Capacitors_SMD:C_0805" H 10538 3600 50  0001 C CNN
F 3 "https://www.mouser.com/datasheet/2/212/KEM_C1013_X7R_FT-CAP_SMD-1103280.pdf" H 10500 3750 50  0001 C CNN
F 4 "80-C0805X104K5R3316" H 10500 3750 50  0001 C CNN "Mouser"
	1    10500 3750
	1    0    0    -1  
$EndComp
$Comp
L thermostat:GND #PWR0113
U 1 1 5E5C9350
P 10500 3900
F 0 "#PWR0113" H 10500 3650 50  0001 C CNN
F 1 "GND" H 10505 3727 50  0000 C CNN
F 2 "" H 10500 3900 50  0000 C CNN
F 3 "" H 10500 3900 50  0000 C CNN
	1    10500 3900
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R22
U 1 1 5E62AE45
P 8200 3750
F 0 "R22" H 8300 3800 50  0000 L CNN
F 1 "10k" H 8300 3700 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 8240 3740 50  0001 C CNN
F 3 "~" H 8200 3750 50  0001 C CNN
F 4 "1" H 8200 3750 50  0001 C CNN "Populate"
	1    8200 3750
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R23
U 1 1 5E633581
P 8500 3750
F 0 "R23" H 8600 3800 50  0000 L CNN
F 1 "10k" H 8600 3700 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 8540 3740 50  0001 C CNN
F 3 "~" H 8500 3750 50  0001 C CNN
F 4 "1" H 8500 3750 50  0001 C CNN "Populate"
	1    8500 3750
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R24
U 1 1 5E63BF33
P 8800 3750
F 0 "R24" H 8900 3800 50  0000 L CNN
F 1 "10k" H 8900 3700 50  0000 L CNN
F 2 "Resistors_SMD:R_0805" V 8840 3740 50  0001 C CNN
F 3 "~" H 8800 3750 50  0001 C CNN
F 4 "1" H 8800 3750 50  0001 C CNN "Populate"
	1    8800 3750
	1    0    0    -1  
$EndComp
Wire Wire Line
	8200 3600 8200 3550
Wire Wire Line
	8200 3550 8500 3550
Wire Wire Line
	10500 3550 10500 3600
Wire Wire Line
	10100 3600 10100 3550
Connection ~ 10100 3550
Wire Wire Line
	10100 3550 10500 3550
Wire Wire Line
	9500 3700 9500 3550
Connection ~ 9500 3550
Wire Wire Line
	9500 3550 10100 3550
Wire Wire Line
	9400 3700 9400 3550
Connection ~ 9400 3550
Wire Wire Line
	9400 3550 9500 3550
Wire Wire Line
	8800 3600 8800 3550
Connection ~ 8800 3550
Wire Wire Line
	8800 3550 9400 3550
Wire Wire Line
	8500 3600 8500 3550
Connection ~ 8500 3550
Wire Wire Line
	8500 3550 8800 3550
Wire Wire Line
	9000 3900 8800 3900
Wire Wire Line
	9000 4000 8500 4000
Wire Wire Line
	8500 4000 8500 3900
Wire Wire Line
	9000 4200 8200 4200
Wire Wire Line
	8200 4200 8200 3900
Wire Wire Line
	8800 4300 8800 3900
Connection ~ 8800 3900
Wire Wire Line
	8500 4300 8500 4000
Connection ~ 8500 4000
Text Notes 7750 3300 0    50   ~ 0
Based on https://www.electroschematics.com/bmp280-diy-project-primer/
$Comp
L thermostat:GND #PWR?
U 1 1 5E0DA227
P 2150 3200
F 0 "#PWR?" H 2150 2950 50  0001 C CNN
F 1 "GND" H 2155 3027 50  0000 C CNN
F 2 "" H 2150 3200 50  0000 C CNN
F 3 "" H 2150 3200 50  0000 C CNN
	1    2150 3200
	1    0    0    -1  
$EndComp
Wire Wire Line
	2150 3200 2500 3200
Connection ~ 2150 3200
Wire Wire Line
	9500 3400 9500 3550
$EndSCHEMATC
