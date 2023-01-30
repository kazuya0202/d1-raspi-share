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

import im920hat_module.im_wireless as imw
import time

# datalog
# FILE_NAME = "/../../media/pi/USB/Savelog.txt"
FILE_NAME = "./log.txt"

# i2c
SLAVE_ADR = 0x30  # hatのI2Cアドレスは0x30 ~ 0x33


# Main
if __name__ == "__main__":
    iwc = imw.IMWireClass(SLAVE_ADR)  # classの初期化

    cmd = "RDID"
    iwc.Write_920(cmd)
    time.sleep(0.5)

    rx_data = iwc.Read_920()  # 受信処理
    print(rx_data)
    iwc.gpio_clean()
    print("END")

    # try:
    #     while True:
    #         rx_data = iwc.Read_920()  # 受信処理
    #         if isinstance(rx_data, int):
    #             print("rx_data is integer")
    #             continue
    #         if len(rx_data) >= 1:  # 受信してない時は''が返り値 (長さ0)
    #             print(rx_data, end="")  # 受信データを画面表示

    #             with open(FILE_NAME, "a") as f:  # ファイルを開く
    #                 f.write(rx_data)  # 1dataをファイル末尾に書き込み

    #             if len(rx_data) >= 11:  # 11は受信データのノード番号+RSSI等の長さ
    #                 if rx_data[2] == "," and rx_data[7] == "," and rx_data[10] == ":":
    #                     rxid = rx_data[3:7]  # 子機(送信機)のIDを抽出
    #                     txbuf = "TXDA" + rxid  # コマンドにCR+LFはいらない
    #                     print(">", txbuf)
    #                     iwc.Write_920(txbuf)  # コマンドを送信

    # except KeyboardInterrupt:  # Ctrl + C End
    #     iwc.gpio_clean()
    #     print("END")
