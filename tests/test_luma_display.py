import time

from ras.lib.display_drawing import DisplayDrawning, dic, menus


def test_display_messages(device):
    for msg in dic:
        device.screen_drawing(msg)
        time.sleep(2)
    device.screen_drawing("time")


def test_display_menus(device):
    for menu in menus:
        for i in range(3):
            time.sleep(1)
            device.display_menu(menu, i)

if __name__ == '__main__':
    OLED1106 = DisplayDrawning()
    test_display_messages(OLED1106)
    test_display_menus(OLED1106)
    OLED1106.initial_display()
    OLED1106.wifi_ap_mode_display()
    OLED1106.shut_down()
    OLED1106.card_drawing("FFFFFFF")
