# -*- coding: utf-8 -*-

"""
raspihat_TXsample001.py : im_wireless.pyを使用し、受信データを出力かつテキスト保存
                          子機へACKを返す
                          Crlt+Cでプログラムを終了する
(C)2019 interplan Corp.

Ver. 0.010    2019/07/08   test version

本ソフトウェアは無保証です。
本ソフトウェアの不具合により損害が発生した場合でも補償は致しません。
改変・流用はご自由にどうぞ。
"""
import time
from datetime import datetime

import RPi.GPIO as GPIO
from func import parse_data

from im920hat_module import im_wireless as imw


def main():
    iwc = imw.IMWireClass(SLAVE_ADR)  # classの初期化

    # logの内容を実行時間で区切ってわかりやすく
    with open(FILE_NAME, "a") as f:
        runtime = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
        f.write(f"\n{runtime}\n")

    try:
        while True:
            rx_data = iwc.Read_920()  # 受信処理
            if isinstance(rx_data, int):
                print("rx_data is integer")
                continue

            if len(rx_data) >= 1:  # 受信してない時は''が返り値 (長さ0)
                print(rx_data, end="")  # 受信データを画面表示

                with open(FILE_NAME, "a") as f:  # ファイルを開く
                    f.write(rx_data)  # 1dataをファイル末尾に書き込み

                if len(rx_data) >= 11:  # 11は受信データのノード番号+RSSI等の長さ
                    if rx_data[2] == "," and rx_data[7] == "," and rx_data[10] == ":":
                        data = parse_data(rx_data)
                        print(f"received: {data}")
                        if data.upper() == "AA":
                            print("[DEBUG] AA -> LED turn on.")

                            p.start(50)
                            p.ChangeFrequency(261)
                            GPIO.output(15, GPIO.HIGH)
                            time.sleep(3)
                            GPIO.output(15, GPIO.LOW)

                            p.stop()

                        # * 2022/12/20 現状送り返す必要がないためコメントアウト
                        # rxid = rx_data[3:7]  # 子機(送信機)のIDを抽出
                        # txbuf = "TXDA" + rxid  # コマンドにCR+LFはいらない
                        # print(">", txbuf)
                        # iwc.Write_920(txbuf)  # コマンドを送信
        # while True:
        #     txbuf = "TXDA" + " 001C"
        #     iwc.Write_920(txbuf)
        #     time.sleep(10)

    except KeyboardInterrupt:  # Ctrl + C End
        iwc.gpio_clean()
        print("END")


# Main
if __name__ == "__main__":
    pin = 21

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(15, GPIO.OUT)
    p = GPIO.PWM(pin, 1)

    # datalog
    # FILE_NAME = "/../../media/pi/USB/Savelog.txt"
    FILE_NAME = "./log.txt"

    # i2c
    SLAVE_ADR = 0x30  # hatのI2Cアドレスは0x30 ~ 0x33
    # * 2022/11/29 `i2cdetect -y 1` で確認して30が使われていたから多分OK

    main()
