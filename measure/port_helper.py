# note: pip install pyserial if below import fails
import serial.tools.list_ports


def main():
    ports = serial.tools.list_ports.comports()

    for port, desc, _ in sorted(ports):
        print(f"{port}: {desc}")


if __name__ == '__main__':
    main()
