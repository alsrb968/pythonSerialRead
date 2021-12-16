import os
import time
from datetime import datetime

import serial

ser1 = serial.Serial('/dev/tty.usbserial-FTHFJNY0', 115200)
ser2 = serial.Serial('/dev/tty.usbserial-A92T0ESS', 115200)

errors = {
    'Error Packet',
    'Error Check Sum',
    'Error Flash Addr',
    'Error ERR_SF_ERASE',
    'Error ERR_SF_WRITE',
    'Error ERR_SF_VERIFY'
}

cycle_count = 0
file_name_full_cpu = 'log_full_cpu.txt'
file_name_full_mcu = 'log_full_mcu.txt'
file_name_count = 'log_count.txt'


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def print(self, color, content: str):
        print(color + content + self.ENDC)


cp = bcolors()

boot_flag = False

while True:
    while ser1.in_waiting:
        line = str(ser1.readline().strip().decode('utf-8'))
        now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S.%f]")
        log = now + '[CPU] : ' + line
        print(log)

        with open(file_name_full_cpu, 'a') as _file:
            _file.write(log + '\n')

    while ser2.in_waiting:  # Or: while ser.inWaiting():
        line = str(ser2.readline().strip().decode('utf-8'))
        now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S.%f]")
        log = now + '[MCU] : ' + line
        cp.print(cp.OKBLUE, log)

        with open(file_name_full_mcu, 'a') as _file:
            _file.write(log + '\n')

        if 'clear_setup' in line:
            with open(file_name_count, 'a') as the_file:
                the_file.write(
                    now + '---' + str(cycle_count) + '---' + line + '\n')
                cycle_count += 1

        if 'SendBootData' in line:
            boot_flag = True

    if boot_flag:
        boot_flag = False
        file_name_full_adb = 'log_full_adb' + datetime.now().strftime('_%Y%m%d_%H%M%S') + '.txt'
        ser1.write(bytes('su\n', 'utf-8'))
        ser1.write(bytes('setprop sys.usb.config adb\n', 'utf-8'))
        time.sleep(2)
        os.system('adb pull /data/log.txt {}'.format(file_name_full_adb))
        time.sleep(3)
        ser1.write(bytes('input tap 400 240\n', 'utf-8'))
        ser1.write(bytes('logcat > /data/log.txt\n', 'utf-8'))