EESchema Schematic File Version 4
LIBS:thermostat-cache
EELAYER 30 0
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
$Comp
L Connector:Screw_Terminal_01x04 THERM_CONN1
U 1 1 5D5B6FC9
P 9850 1150
F 0 "THERM_CONN1" H 9930 1096 50  0000 L CNN
F 1 "THERM_CONN" H 9930 1051 50  0001 L CNN
F 2 "TerminalBlocks_Phoenix:TerminalBlock_Phoenix_MPT-2.54mm_4pol" H 9850 1150 50  0001 C CNN
F 3 "~" H 9850 1150 50  0001 C CNN
	1    9850 1150
	1    0    0    -1  
$EndComp
Text Label 8850 1050 0    50   ~ 0
HVAC_PWR(RED)
Text Label 8850 1150 0    50   ~ 0
HVAC_HEAT(WHITE)
Text Label 8850 1250 0    50   ~ 0
HVAC_COOL(YELLOW)
Text Label 8850 1350 0    50   ~ 0
HVAC_FAN(GREEN)
Wire Wire Line
	8850 1050 9650 1050
Wire Wire Line
	9650 1150 8850 1150
Wire Wire Line
	8850 1250 9650 1250
Wire Wire Line
	8850 1350 9650 1350
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
PWR_3.3V
Text Label 2500 5200 0    50   ~ 0
PWR_3.3V
Text Label 2500 4750 0    50   ~ 0
PWR_3.3V
Text Label 2500 4300 0    50   ~ 0
PWR_3.3V
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
P 9500 3100
F 0 "J1" H 9580 3092 50  0000 L CNN
F 1 "Display i2c" H 9580 3001 50  0000 L CNN
F 2 "Socket_Strips:Socket_Strip_Angled_1x04_Pitch2.54mm" H 9500 3100 50  0001 C CNN
F 3 "~" H 9500 3100 50  0001 C CNN
	1    9500 3100
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x04 J2
U 1 1 5D67AFA8
P 9500 3600
F 0 "J2" H 9580 3592 50  0000 L CNN
F 1 "Sensor i2c" H 9580 3501 50  0000 L CNN
F 2 "Socket_Strips:Socket_Strip_Straight_1x04_Pitch2.54mm" H 9500 3600 50  0001 C CNN
F 3 "~" H 9500 3600 50  0001 C CNN
	1    9500 3600
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x04 J3
U 1 1 5D685426
P 4850 5700
F 0 "J3" H 4930 5692 50  0000 L CNN
F 1 "PoE Input" H 4930 5601 50  0000 L CNN
F 2 "Socket_Strips:Socket_Strip_Angled_1x04_Pitch2.54mm" H 4850 5700 50  0001 C CNN
F 3 "~" H 4850 5700 50  0001 C CNN
	1    4850 5700
	-1   0    0    1   
$EndComp
$Comp
L Connector_Generic:Conn_01x04 J4
U 1 1 5D687A2E
P 4850 5100
F 0 "J4" H 4930 5092 50  0000 L CNN
F 1 "PoE Output" H 4930 5001 50  0000 L CNN
F 2 "Socket_Strips:Socket_Strip_Angled_1x04_Pitch2.54mm" H 4850 5100 50  0001 C CNN
F 3 "~" H 4850 5100 50  0001 C CNN
	1    4850 5100
	-1   0    0    1   
$EndComp
$Comp
L thermostat:1827585-1 J5
U 1 1 5D644363
P 5750 5350
F 0 "J5" H 6029 5363 50  0000 L CNN
F 1 "1827585-1" H 6029 5272 50  0000 L CNN
F 2 "TE_1827585-1" H 5750 5350 50  0001 L BNN
F 3 "Compliant" H 5750 5350 50  0001 L BNN
F 4 "1827585-1" H 5750 5350 50  0001 L BNN "Field4"
F 5 "https://www.te.com/usa-en/product-1827585-1.html?te_bu=Cor&te_type=disp&te_campaign=seda_glo_cor-seda-global-disp-prtnr-fy19-seda-model-bom-cta_sma-317_1&elqCampaignId=32493" H 5750 5350 50  0001 L BNN "Field5"
F 6 "Conn RJ-45 F 8 POS 2.04mm Solder RA Thru-Hole 8 Terminal 1 Port Tray" H 5750 5350 50  0001 L BNN "Field6"
F 7 "1827585-1" H 5750 5350 50  0001 L BNN "Field7"
F 8 "Unavailable" H 5750 5350 50  0001 L BNN "Field8"
F 9 "TE Connectivity" H 5750 5350 50  0001 L BNN "Field9"
F 10 "None" H 5750 5350 50  0001 L BNN "Field10"
F 11 "None" H 5750 5350 50  0001 L BNN "Field11"
	1    5750 5350
	1    0    0    -1  
$EndComp
Text Label 9100 3000 2    50   ~ 0
GND
Text Label 9100 3100 2    50   ~ 0
PWR_5V
Text Label 9100 3200 2    50   ~ 0
GPIO2(SDA1)
Text Label 9100 3300 2    50   ~ 0
GPIO3(SCL1)
Text Label 9100 3500 2    50   ~ 0
GPIO2(SDA1)
Text Label 9100 3600 2    50   ~ 0
GPIO3(SCL1)
Text Label 9100 3700 2    50   ~ 0
GND
Text Label 9100 3800 2    50   ~ 0
PWR_5V
Wire Wire Line
	9100 3000 9300 3000
Wire Wire Line
	9100 3100 9300 3100
Wire Wire Line
	9300 3200 9100 3200
Wire Wire Line
	9100 3300 9300 3300
Wire Wire Line
	9300 3500 9100 3500
Wire Wire Line
	9300 3600 9100 3600
Wire Wire Line
	9100 3700 9300 3700
Wire Wire Line
	9300 3800 9100 3800
$EndSCHEMATC
