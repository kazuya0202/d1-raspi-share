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

from im920hat_module import im_wireless as imw


def main():
    iwc = imw.IMWireClass(SLAVE_ADR)  # classの初期化

    try:
        while True:
            data = input("input data> ")
            cmd = f"TXDT {data}"
            iwc.Write_920(cmd)
            # 受信側の読み取り時に一つ前のバッファが出力されるようになってしまったため，
            # 少し空けて連続して同じコマンドを送信（治し方は不明）
            time.sleep(0.1)
            iwc.Write_920(cmd)
    except KeyboardInterrupt:  # Ctrl + C End
        iwc.gpio_clean()
        print("END")


if __name__ == "__main__":
    # datalog
    FILE_NAME = "./log.txt"

    # i2c
    # * 2022/11/29 `i2cdetect -y 1` で確認して30が使われていたから多分OK
    SLAVE_ADR = 0x30  # hatのI2Cアドレスは0x30 ~ 0x33

    main()
