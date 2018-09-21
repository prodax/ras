import os

import lib.menu as menu
import lib.deletesubstring as deletesubstring
import lib.reset_lib as reset_lib
import logging
_logger = logging.getLogger(__name__)

if __name__ == '__main__':
    update =  menu.m_functionality()
    _logger.debug("UPDATE: " + str(update))
    if update == True:
        reset_lib.update_repo()
        deletesubstring.del_update()
        os.system('sudo reboot')

