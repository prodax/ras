import os
import time

from luma.core.render import canvas
from PIL import ImageFont
from PIL import Image

from .reset_lib import get_ip

import logging

_logger = logging.getLogger(__name__)

dic = {
    ' ': [" ", 0, 1, 0, 0, 24],
    'check_in': ['CHECKED IN', 6, 1, 0, 0, 22],
    'check_out': ['CHECKED OUT', 18, 2, 45, 0, 22],
    'FALSE': ['NOT AUTHORIZED', 45, 2, 8, 0, 20],
    'shut_down': ['Rebooting', 5, 1, 0, 0, 24],
    '1': ['1', 50, 1, 0, 0, 50],
    '2': ['2', 50, 1, 0, 0, 50],
    'Wifi1': ['Connect to AP;RFID Attendance System', 30, 2, 10, 0, 12],
    'Wifi2': ['Browse 192.168.42.1;for Wi-Fi Configuration', 20, 2, 10, 0, 12],
    'Wifi3': ['Connect;to;192.168.42.1', 20, 3, 50, 1, 24],
    'Wifi4': ['Wi-Fi;Connection', 35, 2, 15, 0, 20],
    'update': ['Updating;Firmware', 20, 2, 20, 0, 24],
    'config1': ['Connect to;' + get_ip() + ':3000', 35, 2, 25, 0, 15]
}
dicerror = {
    ' ': [1, " ", 1, 0, 0, 0, 24],
    'error1': [2, 'Odoo;communication;failed', 3, 41, 5, 40,
               'Check;the;parameters', 3, 41, 53, 20, 19],
    'error2': [2, 'RFID;intrigrity;failed', 3, 50, 20, 35,
               'Pass;the;card', 3, 48, 45, 48, 20]}


def menu(device, msg1, msg2, msg3, msg4, loc):
    # use custom font
    font_path = os.path.abspath(os.path.join(
        '/home/pi/ras/fonts', 'Orkney.ttf'))
    font2 = ImageFont.truetype(font_path, 16)
    with canvas(device) as draw:
        if loc == 0:
            draw.rectangle((3, 1, 124, 16), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="black")
            draw.text((5, 15), msg2, font=font2, fill="white")
            draw.text((5, 30), msg3, font=font2, fill="white")
            draw.text((5, 45), msg4, font=font2, fill="white")
        elif loc == 1:
            draw.rectangle((3, 17, 124, 30), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="white")
            draw.text((5, 15), msg2, font=font2, fill="black")
            draw.text((5, 30), msg3, font=font2, fill="white")
            draw.text((5, 45), msg4, font=font2, fill="white")
        elif loc == 2:
            draw.rectangle((3, 31, 124, 46), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="white")
            draw.text((5, 15), msg2, font=font2, fill="white")
            draw.text((5, 30), msg3, font=font2, fill="black")
            draw.text((5, 45), msg4, font=font2, fill="white")
        elif loc == 3:
            draw.rectangle((3, 47, 124, 60), outline="white", fill="white")
            draw.text((5, 0), msg1, font=font2, fill="white")
            draw.text((5, 15), msg2, font=font2, fill="white")
            draw.text((5, 30), msg3, font=font2, fill="white")
            draw.text((5, 45), msg4, font=font2, fill="black")


def screen_drawing(device, info):
    # use custom font
    global error, msg
    font_path = os.path.abspath(os.path.join(
        '/home/pi/ras/fonts', 'Orkney.ttf'))
    if 'error' in info:
        _logger.debug(info)
        code = info.replace('error', '')
        font2 = ImageFont.truetype(font_path, dicerror[info][11] - 3)
        fonte = ImageFont.truetype(font_path, 28)
        with canvas(device) as draw:
            # draw.rectangle(device.bounding_box, outline="white")
            draw.text((17, 5), "ERROR", font=fonte, fill="white")
            draw.text((14, 37), "CODE " + code, font=fonte, fill="white")
        time.sleep(2)
        _logger.debug(str(dicerror[info][0]))
        for i in range(0, dicerror[info][0] + 1):
            _logger.debug("FOR: " + str(i))
            with canvas(device) as draw:
                # draw.rectangle(device.bounding_box, outline="white")
                try:
                    if dicerror[info][0] != i:
                        if dicerror[info][2 + (i * 5)] == 1:
                            draw.text((dicerror[info][3 + (i * 5)], 20),
                                      dicerror[info][1 + (i * 5)],
                                      font=font2, fill="white")
                        elif dicerror[info][2 + (i * 5)] == 2:
                            a, b = dicerror[info][1 + (i * 5)].split(";")
                            draw.text((dicerror[info][3 + (i * 5)], 10),
                                      a, font=font2, fill="white")
                            draw.text((dicerror[info][4 + (i * 5)], 45),
                                      b, font=font2, fill="white")
                        else:
                            a, b, c = dicerror[info][1 + (i * 5)].split(
                                ";")
                            draw.text((dicerror[info][3 + (i * 5)], 4), a,
                                      font=font2, fill="white")
                            draw.text((dicerror[info][4 + (i * 5)], 23),
                                      b, font=font2, fill="white")
                            draw.text((dicerror[info][5 + (i * 5)], 42),
                                      c, font=font2, fill="white")
                    _logger.debug("1")
                    time.sleep(2)
                    _logger.debug("2")
                except:
                    draw.text((20, 20), info, font=font2, fill="white")
                time.sleep(2)
        msg = "time"
    else:
        if info != "time":
            font2 = ImageFont.truetype(font_path, dic[info][5] - 2)
        else:
            font2 = ImageFont.truetype(font_path, 30)
        with canvas(device) as draw:
            # draw.rectangle(device.bounding_box, outline="white")
            if info == "time":
                hour = time.strftime("%H:%M", time.localtime())
                num_ones = hour.count('1')
                if num_ones == 0:
                    draw.text((23, 20), hour, font=font2, fill="white")
                else:
                    if num_ones == 1:
                        draw.text((25, 20), hour, font=font2, fill="white")
                    else:
                        if num_ones == 2:
                            draw.text((28, 20), hour, font=font2, fill="white")
                        else:
                            if num_ones == 3:
                                draw.text((31, 20), hour, font=font2,
                                          fill="white")
                            else:
                                draw.text((34, 20), hour, font=font2,
                                          fill="white")
            else:
                try:
                    if dic[info][2] == 1:
                        draw.text((dic[info][1],
                                   22 + (24 - dic[info][5]) / 2),
                                  dic[info][0], font=font2, fill="white")
                    elif dic[info][2] == 2:
                        a, b = dic[info][0].split(";")
                        draw.text((dic[info][1],
                                   10 + (24 - dic[info][5]) / 2), a,
                                  font=font2, fill="white")
                        draw.text((dic[info][3],
                                   37 + (24 - dic[info][5]) / 2), b,
                                  font=font2, fill="white")
                    else:
                        a, b, c = dic[info][0].split(";")
                        draw.text((dic[info][1],
                                   2 + (24 - dic[info][5]) / 2), a,
                                  font=font2, fill="white")
                        draw.text((dic[info][3],
                                   22 + (24 - dic[info][5]) / 2), b,
                                  font=font2, fill="white")
                        draw.text((dic[info][4],
                                   37 + (24 - dic[info][5]) / 2), c,
                                  font=font2, fill="white")
                except:
                    draw.text((20, 20), info, font=font2, fill="white")


def card_drawing(device, id):
    # use custom font
    font_path = os.path.abspath(os.path.join(
        '/home/pi/ras/fonts', 'Orkney.ttf'))
    font2 = ImageFont.truetype(font_path, 22)

    with canvas(device) as draw:
        # draw.rectangle(device.bounding_box, outline="white")
        try:
            draw.text(15, 20, id, font=font2, fill="white")
        except:
            draw.text((15, 20), id, font=font2, fill="white")

def welcome_msg(device, size):
    # use custom font
    font_path = os.path.abspath(os.path.join(
        '/home/pi/ras/fonts', 'Orkney.ttf'))
    font2 = ImageFont.truetype(font_path, size - 3)
    with canvas(device) as draw:
        # draw.rectangle(device.bounding_box, outline="white")
        draw.text((15, 10), "Welcome to the", font=font2, fill="white")
        draw.text((50, 28), "RFID", font=font2, fill="white")
        draw.text((1, 43), "Attendance system", font=font2, fill="white")
    time.sleep(0.5)


def welcome_logo(device):
    img_path = os.path.abspath(os.path.join(
        '/home/pi/ras/images', 'eficent.png'))
    logo = Image.open(img_path).convert("RGBA")
    fff = Image.new(logo.mode, logo.size, (0,) * 4)

    background = Image.new("RGBA", device.size, "black")
    posn = ((device.width - logo.width) // 2, 0)

    img = Image.composite(logo, fff, logo)
    background.paste(img, posn)
    device.display(background.convert(device.mode))
    time.sleep(0.5)
