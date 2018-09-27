FROM resin/rpi-raspbian:stretch
RUN apt update && apt install -yq \
    python3-smbus i2c-tools git python3-dev python3-pip python3-setuptools \
    libfreetype6-dev libjpeg-dev build-essential libsdl-dev \
    libportmidi-dev libsdl-ttf2.0-dev libsdl-mixer1.2-dev libsdl-image1.2-dev libopenjp2-7 && \
    apt clean && rm -rf /var/lib/apt/lists/*

 # Copy requirements.txt first for better cache on later pushes
COPY . /home/pi/ras
RUN pip3 install -r /home/pi/ras/requeriments.txt && \
    pip3 install luma.emulator

# config-server will run when container starts up on the device
#  CMD ["python3","-u","/home/pi/ras/launcher.py","&","python3","-u","/home/pi/ras/web/config-server.py","&"]

CMD ["python3","-u","/home/pi/ras/config-server.py"]

