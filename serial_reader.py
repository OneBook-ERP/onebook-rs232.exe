import serial

def open_serial(cfg):
    return serial.Serial(
        port=cfg["port"],
        baudrate=cfg["baudrate"],
        timeout=cfg["timeout"]
    )
