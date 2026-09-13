# sampling_1.py
# Basic ADC sampling example
# Digital Communications
# Telecommunications Engineering Program
# Universidad Militar Nueva Granada - UMNG
# Raspberry Pi Pico 2 W
# jose.rugeles@unimilitar.edu.co

import machine
import utime
import array

# ------------------------------------------------------------
# Hardware configuration
# ------------------------------------------------------------
ADC_PIN = 26
SAMPLE_MARKER_PIN = 15
VREF = 3.3

adc = machine.ADC(ADC_PIN)
sample_marker = machine.Pin(SAMPLE_MARKER_PIN, machine.Pin.OUT)
sample_marker.value(0)

# ------------------------------------------------------------
# Sampling parameters
# ------------------------------------------------------------
FS_TARGET = 1000  # Desired sampling frequency [Hz]
SAMPLE_PERIOD_US = int(1_000_000 / FS_TARGET)
NUM_SAMPLES = 10000

# Output file.
# IMPORTANT: The file is written AFTER the acquisition so that
# filesystem operations do not disturb the sampling interval.
FILENAME = "datos400hz.csv"

# Compact buffers:
#   times_us    -> 32-bit timestamps
#   raw_samples -> 16-bit ADC values returned by read_u16()
times_us = array.array("I")
raw_samples = array.array("H")

print("----------------------------------------------------")
print("Basic ADC sampling")
print("----------------------------------------------------")
print("ADC input            : GP{}".format(ADC_PIN))
print("Sampling marker      : GP{}".format(SAMPLE_MARKER_PIN))
print("Target Fs            : {} Hz".format(FS_TARGET))
print("Target sampling time : {} us".format(SAMPLE_PERIOD_US))
print("Number of samples    : {}".format(NUM_SAMPLES))
print("Starting acquisition...")

# ------------------------------------------------------------
# Data acquisition
# ------------------------------------------------------------
# Each sample is scheduled relative to the same initial time.
# This avoids accumulating the execution time of the loop from
# sample to sample, as would happen with a simple sleep() after
# every ADC reading.
#
# The rising edge on GP15 marks the instant immediately before
# the ADC reading. Connect GP15 to an oscilloscope or logic
# analyzer to measure the real sampling frequency experimentally.
# ------------------------------------------------------------
start = utime.ticks_us()

for i in range(NUM_SAMPLES):
    target = utime.ticks_add(start, i * SAMPLE_PERIOD_US)

    # Wait until the programmed sampling instant.
    while utime.ticks_diff(target, utime.ticks_us()) > 0:
        pass

    # Sampling marker:
    # rising edge immediately before the ADC reading.
    sample_marker.value(1)

    t_sample = utime.ticks_us()
    raw_value = adc.read_u16()

    sample_marker.value(0)

    # Store data in RAM.
    # File writing is intentionally postponed until the end.
    times_us.append(utime.ticks_diff(t_sample, start))
    raw_samples.append(raw_value)

print("Acquisition completed.")

# ------------------------------------------------------------
# Estimate the real sampling frequency from recorded timestamps
# ------------------------------------------------------------
if NUM_SAMPLES > 1:
    elapsed_us = times_us[-1] - times_us[0]

    mean_period_us = elapsed_us / (NUM_SAMPLES - 1)
    fs_software = 1_000_000 / mean_period_us

    min_period_us = times_us[1] - times_us[0]
    max_period_us = min_period_us

    for i in range(2, NUM_SAMPLES):
        dt = times_us[i] - times_us[i - 1]

        if dt < min_period_us:
            min_period_us = dt

        if dt > max_period_us:
            max_period_us = dt

    print("----------------------------------------------------")
    print("Timing results")
    print("----------------------------------------------------")
    print("Target Fs             : {:.2f} Hz".format(FS_TARGET))
    print("Software-estimated Fs : {:.2f} Hz".format(fs_software))
    print("Mean sample period    : {:.2f} us".format(mean_period_us))
    print("Minimum period        : {} us".format(min_period_us))
    print("Maximum period        : {} us".format(max_period_us))
    print("")
    print("Measure GP{} with the oscilloscope to obtain Fs_osc.".format(
        SAMPLE_MARKER_PIN
    ))

# ------------------------------------------------------------
# Save data AFTER acquisition
# ------------------------------------------------------------
# CSV columns:
#   Sample      -> sample number
#   Time_us     -> sampling instant relative to the start
#   Raw_u16     -> MicroPython ADC reading scaled to 0...65535
#   Voltage_V   -> approximate voltage using VREF = 3.3 V
# ------------------------------------------------------------
conversion_factor = VREF / 65535

with open(FILENAME, "w") as f:
    f.write("Sample,Time_us,Raw_u16,Voltage_V\n")

    for i in range(NUM_SAMPLES):
        voltage = raw_samples[i] * conversion_factor

        f.write("{},{},{},{:.6f}\n".format(
            i,
            times_us[i],
            raw_samples[i],
            voltage
        ))

print("----------------------------------------------------")
print("Data saved in: {}".format(FILENAME))
print("Program finished.")
