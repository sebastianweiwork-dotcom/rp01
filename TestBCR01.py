#!/usr/bin/env python3
import os
import time
import serial
import subprocess

def print_section(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

def list_usb_devices():
    print_section("Step 1: Checking USB device list")
    try:
        output = subprocess.check_output(["lsusb"]).decode()
        print(output)
        return output
    except Exception as e:
        print(f"Failed to read USB device list: {e}")
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
        print("Detected serial devices:")
        for p in ports:
            print(" -", p)
    else:
        print("No serial devices detected")
    return ports

def test_serial_read(port):
    print_section(f"Step 3: Attempting to read from serial port ({port})")
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        print(f"Successfully opened serial port {port}")
        print("Waiting for barcode scanner data (please scan a code)...")
        data = ser.readline().decode(errors="ignore").strip()
        if data:
            print(f"Received scanner data: {data}")
            print("Test result: Scanner connection OK")
        else:
            print("No data received. Try scanning a barcode.")
            print("Test result: Serial port OK but no scanner data received")
        ser.close()
    except Exception as e:
        print(f"Failed to open serial port {port}: {e}")
        print("Test result: Serial port open failed, scanner may not be connected")

def main():
    print_section("Laser Barcode Scanner Connection Test Start")

    usb_info = list_usb_devices()

    ports = find_serial_ports()

    if not ports:
        print_section("Final Result: No serial devices detected")
        print("Possible reasons:")
        print(" - Scanner is operating in HID keyboard mode")
        print(" - USB cable is power-only and does not support data")
        print(" - Scanner is not properly connected or is damaged")
        print("Recommendation: Switch scanner to serial mode if possible")
        return

    for port in ports:
        test_serial_read(port)

    print_section("Test Completed")

if __name__ == "__main__":
    main()
