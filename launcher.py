import os

import lib.menu as menu
import lib.deletesubstring as deletesubstring
import lib.reset_lib as reset_lib

if __name__ == '__main__':
    update =  menu.m_functionality()
    print("UPDATE: " + str(update))
    if update == True:
        reset_lib.update_repo()
        deletesubstring.del_update()
        os.system('sudo reboot')

