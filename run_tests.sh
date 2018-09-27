#!/bin/bash

cd /home/pi/ras
python3 -m tests.test_luma_display -d sh1106
python3 -m tests.test_ras_buzzer
python3 -m tests.test_xmlrpc