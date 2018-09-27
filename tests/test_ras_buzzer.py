from ras.lib import PasBuz
import time

if __name__ == '__main__':
    # Pin to feed the Signal to the Buzzer - Signal Pin
    PinSignalBuzzer = 13
    # Pin for the feeding Voltage for the Buzzer - Power Pin
    PinPowerBuzzer = 12
    # Creating one Instance for our Passive Buzzer
    PBuzzer = PasBuz.PasBuz(PinSignalBuzzer, PinPowerBuzzer)
    PBuzzer.CheckIn()
    time.sleep(1)
    PBuzzer.CheckOut()
    time.sleep(1)
    PBuzzer.BuzError()
