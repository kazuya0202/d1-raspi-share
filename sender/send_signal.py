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
from typing import Any

from gmail_api_class import GmailRequest, ResponseFlags
from im920hat_module import im_wireless as imw


def send_signal(iwc: Any, cmd: str) -> None:
    # 受信側の読み取り時に一つ前のバッファが出力されるようになってしまったため，
    # 少し空けて連続して同じコマンドを送信（治し方は不明）
    iwc.Write_920(cmd)
    time.sleep(0.1)
    iwc.Write_920(cmd)


def main():
    iwc = imw.IMWireClass(SLAVE_ADR)  # classの初期化

    # 変数名は変更不可（ライブラリの方で参照されてるっぽいから、グローバルにアクセスできる必要がある）
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    gr = GmailRequest(SCOPES)

    keyword = "土砂災害"

    try:
        # for _ in range(3):
        while True:
            gr.fetch_messages()
            if gr.response_flag.value != ResponseFlags.NO_INBOX.value:
                gr.check_messages(keyword)

            print(gr.get_status())

            if gr.response_flag.value == ResponseFlags.WILL_SEND_START.value:
                cmd = f"TXDT A{gr.level}"
                send_signal(iwc, cmd)
            elif gr.response_flag.value == ResponseFlags.WILL_SEND_END.value:
                cmd = "TXDT BB"
                send_signal(iwc, cmd)
            time.sleep(5)
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
