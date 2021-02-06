# *****************************************************************************
# * | File        :	  epd2in9.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V4.0
# * | Date        :   2019-06-20
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

# Found the spec sheet...
# https://www.waveshare.com/w/upload/e/e6/2.9inch_e-Paper_Datasheet.pdf
# Also this??
# https://download.mikroe.com/documents/datasheets/e-paper-display-2%2C9-296x128-n.pdf
# Is this chip the SSD1608??

import logging
import time

# Display resolution
EPD_WIDTH = 128
EPD_HEIGHT = 296


class EPD:
    def __init__(self, epdconfig):
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.epdconfig = epdconfig

    lut_full_update = [
        0x50, 0xAA, 0x55, 0xAA, 0x11, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0xFF, 0xFF, 0x1F, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]

    lut_partial_update = [
        0x10, 0x18, 0x18, 0x08, 0x18, 0x18,
        0x08, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x13, 0x14, 0x44, 0x12,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]

    # Hardware reset
    def reset(self):
        self.epdconfig.digital_write(self.epdconfig.RST_PIN, 1)
        self.epdconfig.delay_ms(200)
        self.epdconfig.digital_write(self.epdconfig.RST_PIN, 0)
        self.epdconfig.delay_ms(10)
        self.epdconfig.digital_write(self.epdconfig.RST_PIN, 1)
        self.epdconfig.delay_ms(200)

    def send_command(self, command):
        self.epdconfig.digital_write(self.epdconfig.DC_PIN, 0)
        self.epdconfig.digital_write(self.epdconfig.CS_PIN, 0)
        self.epdconfig.spi_writebyte([command])
        self.epdconfig.digital_write(self.epdconfig.CS_PIN, 1)

    def send_buffer(self, data):
        self.epdconfig.digital_write(self.epdconfig.DC_PIN, 1)
        self.epdconfig.digital_write(self.epdconfig.CS_PIN, 0)
        self.epdconfig.spi_writebyte(data)
        self.epdconfig.digital_write(self.epdconfig.CS_PIN, 1)

    def send_data(self, data):
        self.send_buffer([data])

    def ReadBusy(self):
        start = time.time_ns()
        # 0: idle, 1: busy
        while(self.epdconfig.digital_read(self.epdconfig.BUSY_PIN) == 1):
            self.epdconfig.delay_ms(50)
        logging.debug(f"e-Paper busy for {(time.time_ns()-start)/1e6} ms")

    def TurnOnDisplay(self):
        self.send_command(0x22)  # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xC4)
        self.send_command(0x20)  # MASTER_ACTIVATION
        self.send_command(0xFF)  # TERMINATE_FRAME_READ_WRITE
        self.ReadBusy()

    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44)  # SET_RAM_X_ADDRESS_START_END_POSITION
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start >> 3) & 0xFF)
        self.send_data((x_end >> 3) & 0xFF)
        self.send_command(0x45)  # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(0x4E)  # SET_RAM_X_ADDRESS_COUNTER
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x >> 3) & 0xFF)
        self.send_command(0x4F)  # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        # self.ReadBusy()

    def init(self, lut):
        if (self.epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()

        self.send_command(0x01)  # DRIVER_OUTPUT_CONTROL
        self.send_data((EPD_HEIGHT - 1) & 0xFF)
        self.send_data(((EPD_HEIGHT - 1) >> 8) & 0xFF)
        self.send_data(0x00)  # GD = 0 SM = 0 TB = 0

        self.send_command(0x0C)  # BOOSTER_SOFT_START_CONTROL
        self.send_data(0xD7)
        self.send_data(0xD6)
        self.send_data(0x9D)

        self.send_command(0x2C)  # WRITE_VCOM_REGISTER
        self.send_data(0xA8)  # VCOM 7C

        self.send_command(0x3A)  # SET_DUMMY_LINE_PERIOD
        self.send_data(0x1A)  # 4 dummy lines per gate

        self.send_command(0x3B)  # SET_GATE_TIME
        self.send_data(0x08)  # 2us per line

        self.send_command(0x11)  # DATA_ENTRY_MODE_SETTING
        self.send_data(0x03)  # X increment Y increment

        self.send_command(0x32)  # WRITE_LUT_REGISTER
        for i in range(0, len(lut)):
            self.send_data(lut[i])
        # EPD hardware init end
        return 0

    def display(self, image):
        if image is not None:
            self.SetWindow(0, 0, self.width - 1, self.height - 1)
            for j in range(0, self.height):
                self.SetCursor(0, j)
                self.send_command(0x24)  # WRITE_RAM
                self.send_buffer(image[i + j * (self.width // 8)]
                                 for i in range(self.width // 8))

            self.TurnOnDisplay()

    def displayWin(self, x1, y1, x2, y2, image):
        if image is not None:
            self.SetWindow(x1, y1, x2-1, y2-1)
            for j in range(y1, y2):
                self.SetCursor(x1, j)
                self.send_command(0x24)  # WRITE_RAM
                self.send_buffer(image[i//8 + j * (self.width // 8)]
                                 for i in range(x1, x2, 8))

            self.TurnOnDisplay()

    def Clear(self, color):
        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        for j in range(0, self.height):
            self.SetCursor(0, j)
            self.send_command(0x24)  # WRITE_RAM
            self.send_buffer([color]*int(self.width // 8))
            # for i in range(0, int(self.width / 8)):
            #     self.send_data(color)
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10)  # DEEP_SLEEP_MODE
        self.send_data(0x01)

    def Dev_exit(self):
        self.epdconfig.module_exit()
