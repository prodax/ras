import json
import os, time
import threading

try:
    import httplib
except:
    import http.client as httplib

try:
    import RPi.GPIO as GPIO
except:
    import RPiSim as GPIO

from .demo_opts import get_device
from . import MFRC522
from .reset_lib import is_wifi_active, reset_to_host_mode, update_repo, reboot
from . import PasBuz
from . import odoo_xmlrpc
from .display_drawing import card_drawing, menu, screen_drawing, welcome_msg,\
    welcome_logo

import logging

_logger = logging.getLogger(__name__)

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
update = False
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

global PBuzzer
PinSignalBuzzer = 13  # Pin to feed the Signal to the Buzzer - Signal Pin
PinPowerBuzzer = 12  # Pin for the feeding Voltage for the Buzzer - Power Pin
PBuzzer = PasBuz.PasBuz(PinSignalBuzzer,
                        PinPowerBuzzer)  # Creating one Instance for our Passive Buzzer
try:
    GPIO.setmode(GPIO.BOARD)  # Set's GPIO pins to BCM GPIO numbering

    INPUT_PIN_DOWN = 31  # Pin for the DOWN button
    GPIO.setup(INPUT_PIN_DOWN, GPIO.IN)  # Set our input pin to be an input

    INPUT_PIN_OK = 29  # Pin for the OK button
    GPIO.setup(INPUT_PIN_OK, GPIO.IN)  # Set our input pin to be an input
except:
    _logger.debug("Avoid GPIO setmode and setup")


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
        screen_drawing(device, "Wifi4")
        time.sleep(4)
        screen_drawing(device, "1")
        time.sleep(1)
        screen_drawing(device, "Wifi1")
        time.sleep(3)
        screen_drawing(device, "2")
        time.sleep(1)
        screen_drawing(device, "Wifi2")
        time.sleep(3)


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


def have_internet():
    _logger.debug("check internet connection")
    conn = httplib.HTTPConnection("www.google.com", timeout=10)
    try:
        conn.request("HEAD", "/")
        _logger.debug("Have internet")
        conn.close()
        return True
    except Exception as e:
        _logger.debug(e)
        conn.close()
        return False


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
                _logger.debug("#################################"
                              "################################################")
                _logger.debug("PARAMETERS: " + str(host) + " / " + str(
                    port) + " / " + str(user_name) + " / " + str(
                    user_password) + " / " + str(dbname))
                _logger.debug("##################################"
                              "###############################################")
                try:
                    user_id = odoo_xmlrpc.authenticate_connection(host, port, user_name,
                        user_password, dbname, https_on)
                    object_facade = odoo_xmlrpc.connection(host, port, https_on)
                    res = object_facade.execute(
                        dbname, user_id, user_password, "hr.employee",
                        "register_attendance", card)
                    _logger.debug(res)
                    msg = res["action"]
                    _logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" + msg)
                    if res["action"] == "check_in":
                        PBuzzer.CheckIn()  # Acoustic Melody for Check In
                    if res["action"] == "check_out":
                        PBuzzer.CheckOut()  # Acoustic Melody for Check Out
                    if res["action"] == "FALSE":
                        PBuzzer.BuzError()  # Acoustic Melody for Error - RFID Card is not in Database
                    error = False
                except:
                    _logger.debug("No Odoo connection")
                    msg = "error1"
                    error = True
                time.sleep(1)
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
        screen_drawing(device, msg)
        cnt_found = cnt_found + 1
        _logger.debug("CNT_FOUND" + str(cnt_found))
        if cnt_found >= 5:
            card_found = False
    else:
        cnt_found = 0
        screen_drawing(device, "time")

    scan_card(MIFAREReader, True)


def rfid_reader():
    global card, error
    card_drawing(device, card)
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
        screen_drawing(device, "update")
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
        screen_drawing(device, "shut_down")
        time.sleep(4)
        reboot()
    else:
        back()




ops = {'0': rfid_hr_attendance, '1': rfid_reader, '2': settings, '3': back,
       '4': reset_settings, '5': update_firmware}


def main():
    global Image
    global pos
    global enter, turn_off
    global elapsed_time
    global adm, update
    global host, port, user_name, user_password, dbname
    global admin_id, https_on
    global msg, card, error
    global device
    global on_Down, on_OK
    start_time = time.time()

    if have_internet():

        on_Down_old = False
        on_OK_old = False
        pos2 = 0
        menu_sel = 1

        while adm == True and update == False:
            msg = " "
            card = " "
            error = False
            adm = False
            flag_m = 0
            # MENU
            while enter == False and turn_off == False and update == False:
                elapsed_time = time.time() - start_time
                if menu_sel == 1:
                    menu(device, "RFID - Odoo", "RFID reader", "Settings",
                         "Exit", pos)
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
                    menu(device, "WiFi Reset", "Update RAS", "Back",
                         "", pos2)
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
                while reset == False and adm == False and turn_off == False and update == False:
                    try:
                        elapsed_time = time.time() - start_time
                        if pos == 0:
                            _logger.debug("Reading data.json")
                            while not os.path.isfile(
                                    "/home/pi/ras/dicts/data.json"):
                                screen_drawing(device, "config1")
                                time.sleep(4)
                            if os.path.isfile("/home/pi/ras/dicts/data.json"):
                                json_file = open('/home/pi/ras/dicts/data.json')
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

                                if "update" not in json_data:
                                    update = False
                                else:
                                    update = True
                                    _logger.debug(
                                        "THIS IS UPDATE: " + str(update))
                                # reset_lib.test_connection(host, port, user_name, user_password, dbname)
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
                        if os.path.isfile("/home/pi/ras/dicts/data.json"):
                            json_file = open('/home/pi/ras/dicts/data.json')
                            json_data = json.load(json_file)
                            json_file.close()
                            admin_id = json_data["admin_id"][0]
                            if "update" not in json_data:
                                update = False
                            else:
                                update = True
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
    global device
    global update
    global reset
    _logger.debug("m_functionality() call")
    try:
        device = get_device()
        welcome_logo(device)
        time.sleep(4)
        welcome_msg(device, 17)
        time.sleep(4)
        main()
        if update:
            screen_drawing(device, "update")
            time.sleep(2)
            screen_drawing(device, " ")
            GPIO.cleanup()
        if reset:
            reset = False
            configure_ap_mode()
            main()
        screen_drawing(device, "shut_down")
        time.sleep(3)
        screen_drawing(device, " ")
        GPIO.cleanup()
        return update

    except KeyboardInterrupt:
        GPIO.cleanup()
        pass
