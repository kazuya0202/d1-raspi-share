from im920hat_module import im_wireless as imw


if __name__ == "__main__":
    SLAVE_ADR = 0x30  # hatのI2Cアドレスは0x30 ~ 0x33
    iwc = imw.IMWireClass(SLAVE_ADR)  # classの初期化
    iwc.Reboot_920()
