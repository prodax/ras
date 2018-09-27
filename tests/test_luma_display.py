import time

from lib.display_drawing import DisplayDrawning, dic, menus


def test_display_messages(device):
    print("Running test_display_messages")
    try:
        for msg in sorted(dic):
            device.screen_drawing(msg)
            time.sleep(0.5)
        device.screen_drawing("time")
        print("test_display_messages OK!")
    except:
        print("test_display_messages FAILED!")


def test_display_menus(device):
    print("Running test_display_menus")
    try:
        for menu in sorted(menus):
            for i in range(3):
                device.display_menu(menu, i)
                time.sleep(0.5)
        print("test_display_menus OK!")
    except:
        print("test_display_menus FAILED!")
    
def test_initial_display(device):
    print("Running test_initial_display")
    try:
        device.initial_display()
        print("test_initial_display OK!")
    except:
        print("test_initial_display FAILED!")

def test_wifi_ap_mode_display(device):
    print("Running test_wifi_ap_mode_display")
    try:
        device.wifi_ap_mode_display()
        print("test_wifi_ap_mode_display OK!")
    except:
        print("test_wifi_ap_mode_display FAILED!")

def test_shut_down(device):
    print("Running test_shut_down")
    try:
        device.shut_down()
        print("test_shut_down OK!")
    except:
        print("test_shut_down FAILED!")

def test_card_drawing(device):
    print("Running test_card_drawing")
    try:
        device.card_drawing("FFFFFFF")
        print("test_card_drawing OK!")
    except:
        print("test_card_drawing FAILED!")


if __name__ == '__main__':
    OLED1106 = DisplayDrawning()
    test_display_messages(OLED1106)
    test_display_menus(OLED1106)
    test_initial_display(OLED1106)
    test_wifi_ap_mode_display(OLED1106)
    test_shut_down(OLED1106)
    test_card_drawing(OLED1106)
