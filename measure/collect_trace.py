#! /usr/bin/env python3

"""Demo of the AnalogIn "Record" acquisition mode.

Summary
-------

This demo generates signals on two AnalogOut instrument channels and captures them on two AnalogIn instrument
channels, displaying the result as a graph using matplotlib.

For this demo to work as intended, connect analog-out channel #1 to analog-in channel #1 and analog-out
channel #2 to analog-in channel #2.

Description
-----------

When using the AnalogIn instrument with the "Record" acquisition mode, we prepare the analog input channel and
(if desired) trigger settings, then start the acquisition using a call to analogIn.configure().

Next, we enter a loop where we continuously fetch data from the instrument by calling analogIn.status(True).
This is repeated until analogIn.status() returns DwfState.Done. Note that this last status() call also transfers
acquisition data that needs to be processed.

After each status() call, we get information on the acquisition status by calling statusRecord(). This call
returns three numbers: counts of available, lost, and corrupted samples.

For perfect acquisition, the lost and corrupt counts should be zero. If the acquisition requires more bandwidth than
can be accommodated on the USB-2 link to the device (i.e., the sample frequency is too high), or if we fetch data too
slowly from our user program, we may see non-zero lost and corrupted counts.

If this happens, the documentation provides no guidance on handling this other than to suggest that the acquisition
sample rate should be lowered, and/or the process should fetch data more quickly. The examples provided by Digilent
suggest that the way to handle nonzero "lost" samples is to skip over them; this is what we do in the program below
(filling the lost samples with NaNs).

Assuming the lost and corrupt counts are zero, the 'available' count gives the number of valid samples available in
the local (PC-side) buffer. These samples can be obtained using calls to statusData(), statusData2(), or
statusData16(). The pydwf library implements these functions by having them allocate a sufficiently-sized local
numpy array, reading the sample data into it, and returning that array.

At the end of the acquisition, i.e., after the status()  function returns DwfState.Done, these sub-arrays are
concatenated to deliver the full sample record of the acquisition.

At that point, we discard all but the last (record_length * sample_frequency) samples that constitute the requested
recording length. The preceding samples were received from the device, but the first few samples may be garbled,
and the total number of samples received will generally exceed the number of samples requested, sometimes by a
considerable margin.

The discarding process is also needed to make sure that the trigger position is in a predictable and reproducible
place. After discarding the first samples of the acquisition to get the requested length, the first remaining
sample is at the time, measured in seconds, returned by the analogIn.triggerPositionStatus() call, relative to
the trigger moment.
"""

import argparse
import time
import numpy as np
import matplotlib.pyplot as plt

from pydwf import (DwfLibrary, DwfEnumConfigInfo, DwfAnalogOutNode, DwfAnalogOutFunction, DwfAcquisitionMode,
                   DwfTriggerSource, DwfAnalogInTriggerType, DwfTriggerSlope, DwfState, DwfAnalogInFilter,
                   PyDwfError)
from pydwf.utilities import openDwfDevice


def configure_analog_output(analogOut, analog_out_frequency, analog_out_amplitude, analog_out_offset):
    """Configure a cosine signal on channel 1, and a sine signal on channel 2."""

    # This channel will carry a 'cosine' (i.e., precede channel 2 by 90 degrees).
    CH1 = 0
    CH2 = 1  # This channel will carry a 'sine'.

    node = DwfAnalogOutNode.Carrier

    analogOut.reset(-1)  # Reset both channels.

    analogOut.nodeEnableSet(CH1, node, True)
    analogOut.nodeFunctionSet(CH1, node, DwfAnalogOutFunction.Sine)
    analogOut.nodeFrequencySet(CH1, node, analog_out_frequency)
    analogOut.nodeAmplitudeSet(CH1, node, analog_out_amplitude)
    analogOut.nodeOffsetSet(CH1, node, analog_out_offset)
    analogOut.nodePhaseSet(CH1, node, 90.0)

    analogOut.nodeEnableSet(CH2, node, True)
    analogOut.nodeFunctionSet(CH2, node, DwfAnalogOutFunction.Sine)
    analogOut.nodeFrequencySet(CH2, node, analog_out_frequency)
    analogOut.nodeAmplitudeSet(CH2, node, analog_out_amplitude)
    analogOut.nodeOffsetSet(CH2, node, analog_out_offset)
    analogOut.nodePhaseSet(CH2, node, 0.0)

    # Synchronize second channel to first channel. This ensures that they will start simultaneously.
    analogOut.masterSet(CH2, CH1)

    # Start output on both channels.
    analogOut.configure(CH1, True)


def run_demo(device, sample_frequency, record_length, trigger_flag, measure_range, output_pin):
    """Configure the analog input, and perform repeated acquisitions and present them graphically."""

    analogIn = device.analogIn
    digitalIO = device.digitalIO

    # setup digital io as output, and output low
    digitalIO.reset()
    digitalIO.outputEnableSet(output_pin)
    digitalIO.outputSet(0)

    def send_pulse():
        # output high
        digitalIO.outputSet(output_pin)

    if trigger_flag:
        # Position of first sample relative to the trigger.
        trigger_position = 0
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

    # TODO: might be able to remove trigger completely
    if trigger_flag:
        # Set up trigger for the analog input instrument.
        # We will trigger on the rising transitions of CH2 (the "cosine" channel) through 0V.
        analogIn.triggerSourceSet(DwfTriggerSource.DetectorAnalogIn)
        analogIn.triggerChannelSet(CH2)
        analogIn.triggerTypeSet(DwfAnalogInTriggerType.Edge)
        analogIn.triggerConditionSet(DwfTriggerSlope.Rise)
        analogIn.triggerPositionSet(trigger_position)
        analogIn.triggerLevelSet(trigger_level)

    # Outer loop: perform repeated acquisitions.
    acquisition_nr = 0

    counter = 0  # TODO: delete

    print("Start measuring")

    while True:

        acquisition_nr += 1  # Increment acquisition number.

        samples = []

        total_samples_lost = total_samples_corrupted = 0

        print("start")
        # Start acquisition sequence
        analogIn.configure(False, True)

        # send a pulse to start measurement
        send_pulse()
        start = time.perf_counter()

        # Inner loop: single acquisition, receive data from AnalogIn instrument and display it.
        while True:

            _ = analogIn.status(True)  # status is not used, only to read data
            (current_samples_available, current_samples_lost,
             current_samples_corrupted) = analogIn.statusRecord()

            total_samples_lost += current_samples_lost
            total_samples_corrupted += current_samples_corrupted

            if current_samples_lost != 0:
                # Append NaN samples as placeholders for lost samples.
                # This follows the Digilent example.
                # We haven't verified yet that this is the proper way to handle lost samples.
                lost_samples = np.full((current_samples_lost, 2), np.nan)
                samples.append(lost_samples)

            if current_samples_available != 0:
                # Append samples read from both channels.
                # Note that we read the samples separately for each channel;
                # We then put them into the same 2D array with shape (current_samples_available, 2).
                current_samples = np.vstack([analogIn.statusData(channel_index, current_samples_available)
                                             for channel_index in channels]).transpose()
                samples.append(current_samples)

            # TODO: receive plain text from serial port
            if time.perf_counter() - start > 0.2:
                plain_text = counter
                # Stop acquisition sequence
                analogIn.configure(False, False)
                # output low
                digitalIO.outputSet(0)
                print("Plain text received: {}".format(plain_text))
                # Concatenate all acquired samples. The result is an (n, 2) array of sample values.
                samples = np.concatenate(samples).T
                # TODO: save data to a npy file
                np.save("data/{}.npy".format(plain_text), samples)
                break

        if total_samples_lost != 0:
            print("[{}] - WARNING - {} samples were lost! Reduce sample frequency.".format(
                acquisition_nr, total_samples_lost))

        if total_samples_corrupted != 0:
            print("[{}] - WARNING - {} samples could be corrupted! Reduce sample frequency.".format(
                acquisition_nr, total_samples_corrupted))

        if counter < 3:
            counter += 1
        else:
            break


def main():
    """Parse arguments and start demo."""

    parser = argparse.ArgumentParser(
        description="Demonstrate analog input recording with triggering.")

    DEFAULT_SAMPLE_FREQUENCY = 1.0e6  # TODO: tune this after pyserial done
    DEFAULT_RECORD_LENGTH = 0
    DEFAULT_MEASURE_RANGE = 3.3
    DEFAULT_OUTPUT_PIN = 0

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
        "-op", "--output-pin",
        type=int,
        default=DEFAULT_OUTPUT_PIN,
        help="digital output pin (default: {})".format(DEFAULT_OUTPUT_PIN)
    )

    args = parser.parse_args()

    dwf = DwfLibrary()

    def maximize_analog_in_buffer_size(configuration_parameters):
        """Select the configuration with the highest possible analog in buffer size."""
        return configuration_parameters[DwfEnumConfigInfo.AnalogInBufferSize]

    try:

        with openDwfDevice(dwf, serial_number_filter=args.serial_number_filter,
                           score_func=maximize_analog_in_buffer_size) as device:

            # We want to see 5 full cycles in the acquisition window.
            analog_out_frequency = 1000

            # Signal amplitude in Volt.
            # The AnalogOut instrument can do 10 Vpp centered around 0 V.
            # However, we use the AnalogIn instrument with a ~ 5 Vpp range centered around 0 V,
            #   so for our example we set the analog output signal amplitude to 2.5 V.
            analog_out_amplitude = 1

            # Signal offset in Volt.
            analog_out_offset = 0.0

            configure_analog_output(
                device.analogOut, analog_out_frequency, analog_out_amplitude, analog_out_offset)

            # Wait for a bit to ensure the stability of the analog output signals.
            time.sleep(2.0)

            run_demo(device,
                     args.sample_frequency,
                     args.record_length,
                     args.trigger,
                     args.measure_range,
                     1 << args.output_pin)

    except PyDwfError as exception:
        print("PyDwfError:", exception)
    finally:
        print("Closed")


if __name__ == "__main__":
    main()
