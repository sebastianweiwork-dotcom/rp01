#!/usr/bin/env python3
import os
import time
import serial
import subprocess

LOG_FILE = "/home/rp01/rp01-rp/TestBCR01_result.txt"

def log(message):
    """Print to console and write to log file."""
    print(message)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(message + "\n")
    except Exception as e:
        print(f"Failed to write log file: {e}")

def print_section(title):
    section_header = "\n" + "="*60 + "\n" + title + "\n" + "="*60
    log(section_header)

def list_usb_devices():
    print_section("Step 1: Checking USB device list")
    try:
        output = subprocess.check_output(["lsusb"]).decode()
        log(output)
        return output
    except Exception as e:
        log(f"Failed to read USB device list: {e}")
        return ""

def find_serial_ports():
    print_section("Step 2: Checking serial devices (/dev/ttyUSB* /dev/ttyACM*)")
    ports = []
    for prefix in ["/dev/ttyUSB", "/dev/ttyACM"]:
        for i in range(10):
            dev = f"{prefix}{i}"
            if os.path.exists(dev):
                ports.append(dev)
    if ports:
        log("Detected serial devices:")
        for p in ports:
            log(" - " + p)
    else:
        log("No serial devices detected")
    return ports

def test_serial_read(port):
    print_section(f"Step 3: Attempting to read from serial port ({port})")
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        log(f"Successfully opened serial port {port}")
        log("Waiting for barcode scanner data (please scan a code)...")
        data = ser.readline().decode(errors="ignore").strip()
        if data:
            log(f"Received scanner data: {data}")
            log("Test result: Scanner connection OK")
        else:
            log("No data received. Try scanning a barcode.")
            log("Test result: Serial port OK but no scanner data received")
        ser.close()
    except Exception as e:
        log(f"Failed to open serial port {port}: {e}")
        log("Test result: Serial port open failed, scanner may not be connected")

def main():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log("\n\n==================== Test Session Start ====================")
    log(f"Timestamp: {timestamp}")
    log(f"Log file path: {LOG_FILE}")

    print_section("Laser Barcode Scanner Connection Test Start")

    usb_info = list_usb_devices()
    ports = find_serial_ports()

    if not ports:
        print_section("Final Result: No serial devices detected")
        log("Possible reasons:")
        log(" - Scanner is operating in HID keyboard mode")
        log(" - USB cable is power-only and does not support data")
        log(" - Scanner is not properly connected or is damaged")
        log("Recommendation: Switch scanner to serial mode if possible")
        log("==================== Test Session End ====================\n")
        return

    for port in ports:
        test_serial_read(port)

    print_section("Test Completed")
    log("==================== Test Session End ====================\n")

if __name__ == "__main__":
    main()
