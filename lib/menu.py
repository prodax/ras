import json
import logging
import os
import threading
import time

from lib import WORK_DIR

from . import MFRC522, PasBuz, display_drawing
from .reset_lib import (have_internet, is_wifi_active, reboot,
                        reset_to_host_mode, update_repo)

import RPi.GPIO as GPIO

_logger = logging.getLogger(__name__)

OLED1106 = display_drawing.DisplayDrawning()

error = False
card_found = False

cnt_found = 0
admin_id = "FFFFFFFF"
turn_off = False
adm = True
elapsed_time = 0.0
pos = 0
enter = False
reset = False
on_Down = False
on_OK = False
ap_mode = False

tz_dic = {'-12:00': "Pacific/Kwajalein", '-11:00': "Pacific/Samoa",
          '-10:00': "US/Hawaii", '-09:50': "Pacific/Marquesas",
          '-09:00': "US/Alaska", '-08:00': "Etc/GMT-8", '-07:00': "Etc/GMT-7",
          '-06:00': "America/Mexico_City", '-05:00': "America/Lima",
          '-04:00': "America/La_Paz", '-03:50': "Canada/Newfoundland",
          '-03:00': "America/Buenos_Aires", '-02:00': "Etc/GMT-2",
          '-01:00': "Atlantic/Azores", '+00:00': "Europe/London",
          '+01:00': "Europe/Madrid", '+02:00': "Europe/Kaliningrad",
          '+03:00': "Asia/Baghdad", '+03:50': "Asia/Tehran",
          '+04:00': "Asia/Baku", '+04:50': "Asia/Kabul",
          '+05:00': "Asia/Karachi", '+05:50': "Asia/Calcutta",
          '+05:75': "Asia/Kathmandu", '+06:00': "Asia/Dhaka",
          '+06:50': "Asia/Rangoon", '+07:00': "Asia/Bangkok",
          '+08:00': "Asia/Hong_Kong", '+08:75': "Australia/Eucla",
          '+09:00': "Asia/Tokyo", '+09:50': "Australia/Adelaide",
          '+10:00': "Pacific/Guam", '+10:50': "Australia/Lord_Howe",
          '+11:00': "Asia/Magadan", '+11:50': "Pacific/Norfolk",
          '+12:00': "Pacific/Auckland", '+12:75': "Pacific/Chatham",
          '+13:00': "Pacific/Apia", '+14:00': "Pacific/Fakaofo"}

# Create a function to run when the input is high
def inputStateDown(channel):
    global on_Down
    if on_Down == False:
        _logger.debug('Down Pressed')
        on_Down = True
    else:
        on_Down = False


def inputStateOK(channel):
    global on_OK
    if on_OK == False:
        _logger.debug('OK Pressed')
        on_OK = True
    else:
        on_OK = False


try:
    GPIO.add_event_detect(INPUT_PIN_DOWN, GPIO.FALLING, callback=inputStateDown,
                          bouncetime=200)
    GPIO.add_event_detect(INPUT_PIN_OK, GPIO.FALLING, callback=inputStateOK,
                          bouncetime=200)
except:
    _logger.debug("GPIOs related with buttons are not working")

try:
    # Create an object of the class MFRC522
    MIFAREReader = MFRC522.MFRC522()
except Exception:
    _logger.debug("Avoid SPI RFID setup")


def print_wifi_config():
    global ap_mode
    while ap_mode:
        _logger.debug("Display AP connection instructions")
        OLED1106.wifi_ap_mode_display()


def launch_ap_mode():
    global ap_mode
    reset_to_host_mode()
    _logger.debug("AP Mode Finished")
    ap_mode = False


def configure_ap_mode():
    global ap_mode, adm
    ap_mode = True
    adm = True
    _logger.debug("Starting Wifi Connect")
    try:
        Thread1 = threading.Thread(target=print_wifi_config)
        Thread2 = threading.Thread(target=launch_ap_mode)
    except:
        print("Error: unable to start thread")
    finally:
        Thread1.start()
        Thread2.start()
    while ap_mode:
        pass
    _logger.debug("Leaving configure_ap_mode")





def scan_card(MIFAREReader, odoo):
    global object_facade
    global user_id
    global user_password
    global db_name
    global card
    global card_found
    global user_name
    global host
    global port
    global msg
    global adm, turn_off
    global admin_id
    global error

    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        _logger.debug("Card detected")
        card_found = True

    # Get the UID of the card
    (status, uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # _logger.debug(UID)
        _logger.debug(
            "Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
        card = hex(int(uid[0])).split('x')[-1] + hex(int(uid[1])).split('x')[
            -1] + hex(int(uid[2])).split('x')[-1] + hex(int(uid[3])).split('x')[
            -1]

        _logger.debug(card)
        if card == admin_id:
            adm = True
            # turn_off = True
        # This is the default key for authentication
        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key,
                                           uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
            if odoo:
                odoo.check_attendance(card)
            else:
                error = False
        else:
            _logger.debug("Authentication error")
            # msg = "error2"
            # error = True
    else:
        _logger.debug("Scan Card loop")
        error = False


def rfid_hr_attendance():
    global error, cnt_found, card_found
    # hour = time.strftime("%H:%M")
    if card_found:
        OLED1106.screen_drawing(msg)
        cnt_found = cnt_found + 1
        _logger.debug("CNT_FOUND" + str(cnt_found))
        if cnt_found >= 5:
            card_found = False
    else:
        cnt_found = 0
        OLED1106.screen_drawing("time")

    scan_card(MIFAREReader, True)


def rfid_reader():
    global card, error
    OLED1106.card_drawing(card)
    scan_card(MIFAREReader, False)


def reset_settings():
    global reset
    _logger.debug("Reset Settings selected")
    reset = True


def back():
    global turn_off
    _logger.debug("Back selected")
    turn_off = True


def settings():
    _logger.debug("Other settings selected")


def updating_repo():
    global updating
    update_repo()
    _logger.debug("Update finished")
    updating = False


def print_update_repo():
    global updating
    while updating:
        _logger.debug("Display updating firmware")
        OLED1106.screen_drawing("update")
        time.sleep(4)


def update_firmware():
    if have_internet():
        global updating
        _logger.debug("Updating repository")
        updating = True
        try:
            Thread3 = threading.Thread(target=print_update_repo)
            Thread4 = threading.Thread(target=updating_repo)
        except:
            print("Error: unable to start thread")
        finally:
            Thread3.start()
            Thread4.start()
        while updating:
            pass
        _logger.debug("Leaving update_firmware and rebooting")
        OLED1106.screen_drawing("shut_down")
        time.sleep(4)
        reboot()
    else:
        back()


ops = {'0': rfid_hr_attendance, '1': rfid_reader, '2': settings, '3': back,
       '4': reset_settings, '5': update_firmware}


def main():
    global pos
    global enter, turn_off
    global elapsed_time
    global adm
    global host, port, user_name, user_password, dbname
    global admin_id, https_on
    global msg, card, error
    global on_Down, on_OK
    start_time = time.time()

    if have_internet():

        on_Down_old = False
        on_OK_old = False
        pos2 = 0
        menu_sel = 1

        while adm:
            msg = " "
            card = " "
            error = False
            adm = False
            flag_m = 0
            # MENU
            while enter == False and turn_off == False:
                elapsed_time = time.time() - start_time
                if menu_sel == 1:
                    OLED1106.display_menu('Main', pos)
                    try:
                        # Check if the OK button is pressed
                        if on_OK != on_OK_old:
                            enter = True
                            on_OK_old = on_OK
                        else:
                            enter = False
                        # Check if the DOWN button is pressed
                        if on_Down != on_Down_old:
                            pos = pos + 1
                            if pos > 3:
                                pos = 0
                            on_Down_old = on_Down
                    except KeyboardInterrupt:
                        break
                else:
                    OLED1106.display_menu('Settings', pos2)
                    try:
                        # Check if the OK button is pressed
                        if on_OK != on_OK_old:
                            enter = True
                            if pos2 == 2:
                                adm = True
                                pos = 0
                            else:
                                flag_m = 1
                            on_OK_old = on_OK
                        else:
                            enter = False
                        # Check if the DOWN button is pressed
                        if on_Down != on_Down_old:
                            pos2 = pos2 + 1
                            if pos2 > 2:
                                pos2 = 0
                            on_Down_old = on_Down
                    except KeyboardInterrupt:
                        break
            # CHOSEN FUNCTIONALITY
            if enter:
                enter = False
                if pos == 2:
                    adm = True
                    menu_sel = 2
                else:
                    menu_sel = 1
                while reset == False and adm == False and turn_off == False:
                    try:
                        elapsed_time = time.time() - start_time
                        if pos == 0:
                            _logger.debug("Reading data.json")
                            while not os.path.isfile(
                                    os.path.abspath(
                                        os.path.join(WORK_DIR, 'dicts/data.json'))):
                                OLED1106.screen_drawing("config1")
                                time.sleep(4)
                            if os.path.isfile(os.path.abspath(
                                    os.path.join(WORK_DIR, 'dicts/data.json'))):
                                json_file = open(os.path.abspath(
                                    os.path.join(WORK_DIR, 'dicts/data.json')))
                                json_data = json.load(json_file)
                                json_file.close()
                                host = json_data["odoo_host"][0]
                                port = json_data["odoo_port"][0]
                                user_name = json_data["user_name"][0]
                                user_password = json_data["user_password"][0]
                                dbname = json_data["db"][0]
                                admin_id = json_data["admin_id"][0]
                                timezone = json_data["timezone"][0]
                                os.environ['TZ'] = tz_dic[timezone]
                                time.tzset()
                                if "https" not in json_data:
                                    https_on = False
                                else:
                                    https_on = True
                            else:
                                raise ValueError("It is not a file!")
                        else:
                            _logger.debug("POS " + str(pos))
                        if flag_m == 0:
                            ops[str(pos)]()  # rfid_hr_attendance()
                        else:
                            ops[str(pos2 + 4)]()
                            if pos2 == 1:
                                adm = True
                        if os.path.isfile(os.path.abspath(
                                os.path.join(WORK_DIR, 'dicts/data.json'))):
                            json_file = open(os.path.abspath(
                                os.path.join(WORK_DIR, 'dicts/data.json')))
                            json_data = json.load(json_file)
                            json_file.close()
                            admin_id = json_data["admin_id"][0]
                        if adm:
                            _logger.debug(str(adm))
                    except KeyboardInterrupt:
                        break
                pos = 0
                _logger.debug("on_OK_old: " + str(on_OK_old))
                _logger.debug("on_OK: " + str(on_OK))

    else:
        if not is_wifi_active():
            configure_ap_mode()
            main()


def m_functionality():
    _logger.debug("Starting up RAS")
    try:
        OLED1106.initial_display()
        main()
        OLED1106.shut_down()
        GPIO.cleanup()
    except KeyboardInterrupt:
        GPIO.cleanup()
