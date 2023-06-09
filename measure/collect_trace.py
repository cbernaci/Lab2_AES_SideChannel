#! /usr/bin/env python3

"""
This Python script is used to measure the trace of an FPGA board

wire connection:
    connect oscilloscope ch1 across the 0.25-ohm resistor
    connect oscilloscope ch2 to the ground and digital pin 0
    connect digital pin 0 to the FPGA board as a trigger for the next AES 
    encryption connects FPGA to Arduino (SPI), connect Arduino to PC (UART)

Description:
    The code pulse digital pin 0 to high to signal the FPGA to start AES 
    encryption, meanwhile start the Analog Discovery 2 to measure the voltage 
    across the 0.25-ohm resistor. When the Serial receives the data from 
    Arduino, it means the AES encryption is done, and the sent data is the plain
    text for the encryption. The voltage trace will be stored in a .npy file 
    with the name the same as the plain text. Further analysis will be done in 
    other scripts.
"""

import argparse
import time
import numpy as np
import serial

import port_helper
from aes import AES

from pydwf import (DwfLibrary, DwfEnumConfigInfo, DwfAcquisitionMode,
                   DwfTriggerSource, DwfAnalogInTriggerType, DwfTriggerSlope,
                   DwfAnalogInFilter, PyDwfError)
from pydwf.utilities import openDwfDevice

DEFAULT_SAMPLE_FREQUENCY = 1.0e6  # TODO: tune this after pyserial done
DEFAULT_RECORD_LENGTH = 0
DEFAULT_MEASURE_RANGE = 3.3
DEFAULT_OUTPUT_PIN = 0
DEFAULT_PORT = 'COM5'  # TODO: change COM port to match your setup
DEFAULT_BAUDRATE = 115200
DEFAULT_TIMEOUT = 0.1

data_path = r"C:\Users\Jerry\OneDrive - nyu.edu\temp\data\meas2"


aes = AES(False, False)
KNOWN_KEY = "80000000000000000000000000000000"


def save_trace(receive, trace):
    """
    Save the trace to a .npy file with the name the same as the plain text.
    """
    if len(receive) != 64:
        print("WARNING - receive text length not 64, trace not saved")
        return
    plain_text = receive[:32]
    cipher_text = receive[32:]
    res = aes.encrypt_string(plain_text, KNOWN_KEY)
    if res != AES.string_to_block(cipher_text):
        print(f"plain text {plain_text} and cipher text {cipher_text}")
        print(
            f"WARNING - cipher text {cipher_text} and expectation "
            f"{AES.block_to_string(res)} not match, trace not saved")
        return

    np.save(f"{data_path}/{plain_text.zfill(32)}.npy", trace)


def open_serial(port, baudrate, timeout):
    # open serial connection
    try:
        return serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
    except serial.SerialException:
        print("Serial port not found, please check available port below")
        port_helper.main()
        return None


def run_demo(device, sample_frequency, record_length, trigger_flag, measure_range, output_pin, ser):
    """Configure the analog input, and perform repeated acquisitions and present them graphically."""

    analogIn = device.analogIn
    digitalIO = device.digitalIO

    # setup digital io as output, and output low
    digitalIO.reset()
    digitalIO.outputEnableSet(output_pin)
    digitalIO.outputSet(0)

    if trigger_flag:
        # Position of the first sample relative to the trigger.
        trigger_position = -0.001  # record data 1ms before the trigger
        # Trigger level, in Volts
        trigger_level = 0.5

    # Configure analog input instrument acquisition.

    CH1 = 0
    CH2 = 1

    channels = (CH1, CH2)

    for channel_index in channels:
        analogIn.channelEnableSet(channel_index, True)
        analogIn.channelFilterSet(channel_index, DwfAnalogInFilter.Average)
        analogIn.channelRangeSet(channel_index, measure_range)

    analogIn.acquisitionModeSet(DwfAcquisitionMode.Record)
    analogIn.frequencySet(sample_frequency)
    analogIn.recordLengthSet(record_length)

    if trigger_flag:
        # Set up trigger for the analog input instrument.
        # We will trigger on the rising transitions of CH2
        analogIn.triggerSourceSet(DwfTriggerSource.DetectorAnalogIn)
        analogIn.triggerChannelSet(CH2)
        analogIn.triggerTypeSet(DwfAnalogInTriggerType.Edge)
        analogIn.triggerConditionSet(DwfTriggerSlope.Rise)
        analogIn.triggerPositionSet(trigger_position)
        analogIn.triggerLevelSet(trigger_level)

    print("Start measuring")

    try:
        while True:
            # Start acquisition sequence
            analogIn.configure(False, True)
            time.sleep(0.1)

            if ser.inWaiting() > 0:
                print("extra data read from serial: ",
                      ser.read(ser.inWaiting()))

            samples = []

            total_samples_lost = total_samples_corrupted = 0

            # send high to start the next AES encryption on FPGA
            # output high
            digitalIO.outputSet(output_pin)

            # timeout measure traces
            start_time = time.perf_counter()

            # Inner loop: single acquisition, receive data from AnalogIn
            while True:

                # status is not used, only to read data
                _ = analogIn.status(True)
                (current_samples_available, current_samples_lost,
                 current_samples_corrupted) = analogIn.statusRecord()

                total_samples_lost += current_samples_lost
                total_samples_corrupted += current_samples_corrupted

                if current_samples_available != 0:
                    # Append samples read from both channels.
                    # Note that we read the samples separately for each channel;
                    # We then put them into the same 2D array with shape (current_samples_available, 2).
                    current_samples = np.vstack([analogIn.statusData(channel_index, current_samples_available)
                                                for channel_index in channels]).transpose()
                    samples.append(current_samples)

                # stop acquisition when serial port receives data
                if ser.inWaiting() > 0:
                    # Stop acquisition sequence
                    analogIn.configure(False, False)
                    # output low
                    digitalIO.outputSet(0)

                    # read plain text (HEX format) from serial port
                    receive_text = ser.readline().decode("utf-8").strip()
                    print("Text received: {}".format(receive_text))

                    if total_samples_lost != 0:
                        print(
                            f"WARNING - {total_samples_lost} samples were lost! Reduce sample frequency.")
                        print("Not saving this data")
                    elif total_samples_corrupted != 0:
                        print(
                            f"WARNING - {total_samples_corrupted} samples could be corrupted! Reduce sample frequency.")
                        print("Not saving this data")
                    else:
                        # Concatenate all acquired samples
                        samples = np.concatenate(samples).T
                        save_trace(receive=receive_text, trace=samples)
                    break
                elif time.perf_counter() - start_time > 1:
                    # output low
                    digitalIO.outputSet(0)
                    print("timeout!!! not saving data")
                    break

    except KeyboardInterrupt:
        print("Stop measuring")


def main():
    """Parse arguments and start demo."""

    parser = argparse.ArgumentParser(
        description="Demonstrate analog input recording with triggering.")

    parser.add_argument(
        "-sn", "--serial-number-filter",
        type=str,
        nargs='?',
        dest="serial_number_filter",
        help="serial number filter to select a specific Digilent Waveforms device"
    )

    parser.add_argument(
        "-fs", "--sample-frequency",
        type=float,
        default=DEFAULT_SAMPLE_FREQUENCY,
        help="sample frequency, in samples per second (default: {} Hz)".format(
            DEFAULT_SAMPLE_FREQUENCY)
    )

    parser.add_argument(
        "-r", "--record-length",
        type=float,
        default=DEFAULT_RECORD_LENGTH,
        help="record length, in seconds (default: {} s)".format(
            DEFAULT_RECORD_LENGTH)
    )

    parser.add_argument(
        "-mr", "--measure-range",
        type=float,
        default=DEFAULT_MEASURE_RANGE,
        help="measured voltage range, in volt (default: {} v)".format(
            DEFAULT_MEASURE_RANGE)
    )

    parser.add_argument(
        "-x", "--disable-trigger",
        action="store_false",
        dest="trigger",
        help="disable triggering (default: enabled)"
    )

    parser.add_argument(
        "--output-pin",
        type=int,
        default=DEFAULT_OUTPUT_PIN,
        help="digital output pin (default: {})".format(DEFAULT_OUTPUT_PIN)
    )

    parser.add_argument(
        "-p", "--port",
        type=str,
        nargs='?',
        default=DEFAULT_PORT,
        help="serial port for Arduino (default: {})".format(DEFAULT_OUTPUT_PIN)
    )

    parser.add_argument(
        "--baudrate",
        type=int,
        default=DEFAULT_BAUDRATE,
        help="baudrate for UART (default: {})".format(DEFAULT_BAUDRATE)
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="timeout for serial read (default: {})".format(DEFAULT_TIMEOUT)
    )

    args = parser.parse_args()

    # open UART connection with Arduino
    ser = open_serial(args.port, args.baudrate, args.timeout)
    if ser is None:
        return

    dwf = DwfLibrary()

    def maximize_analog_in_buffer_size(configuration_parameters):
        """Select the configuration with the highest possible analog in buffer size."""
        return configuration_parameters[DwfEnumConfigInfo.AnalogInBufferSize]

    try:

        with openDwfDevice(dwf, serial_number_filter=args.serial_number_filter,
                           score_func=maximize_analog_in_buffer_size) as device:

            # Wait for a bit to ensure the stability of the analog output signals.
            time.sleep(2.0)

            run_demo(device,
                     args.sample_frequency,
                     args.record_length,
                     args.trigger,
                     args.measure_range,
                     1 << args.output_pin,
                     ser)

    except PyDwfError as exception:
        print("PyDwfError:", exception)
    finally:
        ser.close()
        print("Closed")


if __name__ == "__main__":
    main()
