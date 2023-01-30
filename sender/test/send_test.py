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

import im_wireless as imw
import keyboard


def main():
    iwc = imw.IMWireClass(SLAVE_ADR)  # classの初期化

    try:
        while True:
            if keyboard.is_pressed("s"):
                print("pressed key: s")
                cmd = f"TXDT 10"
                iwc.Write_920(cmd)
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
                        rxid = rx_data[3:7]  # 子機(送信機)のIDを抽出
                        txbuf = "TXDA" + rxid  # コマンドにCR+LFはいらない
                        print(">", txbuf)
                        iwc.Write_920(txbuf)  # コマンドを送信
        # while True:
        #     txbuf = "TXDA" + " 001C"
        #     iwc.Write_920(txbuf)
        #     time.sleep(10)

    except KeyboardInterrupt:  # Ctrl + C End
        iwc.gpio_clean()
        print("END")


if __name__ == "__main__":
    # datalog
    FILE_NAME = "./log.txt"

    # i2c
    # * 2022/11/29 `i2cdetect -y 1` で確認して30が使われていたから多分OK
    SLAVE_ADR = 0x30  # hatのI2Cアドレスは0x30 ~ 0x33
