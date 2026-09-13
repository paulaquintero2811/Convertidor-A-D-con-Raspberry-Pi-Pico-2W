# ============================================================
# sampling_2.py
# Raspberry Pi Pico 2 W (RP2350) - MicroPython
# Statistical characterization of a DC input using the ADC
# Digital Communications
# Telecommunications Engineering Program
# Universidad Militar Nueva Granada - UMNG
# Raspberry Pi Pico 2 W
# jose.rugeles@unimilitar.edu.co

# Purpose:
#   - Acquire N DC measurements
#   - Calculate mean, sample variance, sample standard deviation
#   - Calculate minimum, maximum, and range
#   - Build a histogram using approximate 12-bit ADC codes
#   - Save raw samples and histogram as CSV files
#
# ============================================================

from machine import ADC
from array import array
import math
import gc

try:
    import os
except ImportError:
    os = None

ADC_PIN = 26
VREF = 3.3
NUM_SAMPLES = 10000
BUFFER_SAMPLES = 100

adc = ADC(ADC_PIN)
LSB_12_V = VREF / 4095.0


def free_space_bytes():
    if os is None:
        return None
    try:
        stat = os.statvfs("/")
        return stat[0] * stat[3]
    except Exception:
        return None


print()
print("----------------------------------------------------")
print("ADC statistical characterization")
print("Raspberry Pi Pico 2 W")
print("----------------------------------------------------")
print("ADC input       : GP{}".format(ADC_PIN))
print("Number samples  : {}".format(NUM_SAMPLES))
print("Assumed VREF    : {:.3f} V".format(VREF))
print("Ideal 12-bit LSB: {:.3f} mV".format(LSB_12_V * 1000))
print()

test_id = input("Test number (1-5): ").strip()
if test_id not in ("1", "2", "3", "4", "5"):
    print("Invalid test number. Using test_1.")
    test_id = "1"

reference_text = input(
    "DC voltage measured with DMM [V] (Enter to skip): "
).strip()

reference_voltage = None
if reference_text:
    try:
        reference_voltage = float(reference_text)
    except ValueError:
        print("Invalid reference voltage. DMM comparison will be skipped.")
        reference_voltage = None

sample_filename = "samples_test_{}.csv".format(test_id)
hist_filename = "histogram_test_{}.csv".format(test_id)

free_bytes = free_space_bytes()
if free_bytes is not None:
    print("Free filesystem space: {:.1f} kB".format(free_bytes / 1024))

print()
print("Files to be created:")
print("  {}".format(sample_filename))
print("  {}".format(hist_filename))
print()

# Welford statistical variables
n = 0
mean_v = 0.0
M2 = 0.0
min_v = None
max_v = None
min_code12 = 4095
max_code12 = 0
count_code_0 = 0
count_code_4095 = 0

# 4096 nominal 12-bit bins; 16-bit counts are enough for 10000 samples.
histogram = array("H", [0] * 4096)
gc.collect()

print("Starting acquisition...")

try:
    with open(sample_filename, "w") as sample_file:
        # Compact file: students convert Raw_u16 to voltage in MATLAB/Python.
        sample_file.write("Sample,Raw_u16\n")
        buffer = []

        for i in range(NUM_SAMPLES):
            raw_u16 = adc.read_u16()
            voltage = raw_u16 * VREF / 65535.0
            code12 = raw_u16 >> 4

            # Welford online statistics
            n += 1
            delta = voltage - mean_v
            mean_v += delta / n
            delta2 = voltage - mean_v
            M2 += delta * delta2

            if min_v is None or voltage < min_v:
                min_v = voltage
            if max_v is None or voltage > max_v:
                max_v = voltage

            if code12 < min_code12:
                min_code12 = code12
            if code12 > max_code12:
                max_code12 = code12

            histogram[code12] += 1

            if code12 == 0:
                count_code_0 += 1
            if code12 == 4095:
                count_code_4095 += 1

            buffer.append("{},{}\n".format(i, raw_u16))

            if len(buffer) >= BUFFER_SAMPLES:
                sample_file.write("".join(buffer))
                buffer = []

            if (i + 1) % 1000 == 0:
                print("  {} / {} samples".format(i + 1, NUM_SAMPLES))

        if buffer:
            sample_file.write("".join(buffer))

except OSError as exc:
    print()
    print("ERROR while writing sample file:", exc)
    print("Delete old files from the Pico filesystem and run the test again.")
    raise

if n > 1:
    variance_v = M2 / (n - 1)
    std_v = math.sqrt(variance_v)
else:
    variance_v = 0.0
    std_v = 0.0

range_v = max_v - min_v
std_mv = std_v * 1000.0
std_lsb = std_v / LSB_12_V

# Histogram mode
mode_code12 = 0
mode_count = histogram[0]
for code in range(1, 4096):
    if histogram[code] > mode_count:
        mode_code12 = code
        mode_count = histogram[code]

mode_voltage = mode_code12 * LSB_12_V

try:
    with open(hist_filename, "w") as hist_file:
        hist_file.write("Code12,Count,Voltage_equiv_V\n")
        for code in range(4096):
            count = histogram[code]
            if count > 0:
                voltage_equiv = code * LSB_12_V
                hist_file.write(
                    "{},{},{:.6f}\n".format(code, count, voltage_equiv)
                )
except OSError as exc:
    print()
    print("ERROR while writing histogram file:", exc)
    print("Delete old files from the Pico filesystem and run the test again.")
    raise

print()
print("----------------------------------------------------")
print("Statistical results")
print("----------------------------------------------------")
print("N                         : {}".format(n))
print("Mean V_bar                : {:.6f} V".format(mean_v))
print("Sample variance s^2       : {:.10e} V^2".format(variance_v))
print("Sample std. deviation s   : {:.6f} V".format(std_v))
print("Sample std. deviation s   : {:.3f} mV".format(std_mv))
print("Std. deviation            : {:.3f} LSB".format(std_lsb))
print("Minimum V_min             : {:.6f} V".format(min_v))
print("Maximum V_max             : {:.6f} V".format(max_v))
print("Range R                   : {:.6f} V".format(range_v))
print("Minimum nominal code      : {}".format(min_code12))
print("Maximum nominal code      : {}".format(max_code12))
print("Mode nominal code         : {}".format(mode_code12))
print("Mode count                : {}".format(mode_count))
print("Mode equivalent voltage   : {:.6f} V".format(mode_voltage))
print("Code 0 occurrences        : {}".format(count_code_0))
print("Code 4095 occurrences     : {}".format(count_code_4095))

if reference_voltage is not None:
    error_v = mean_v - reference_voltage
    error_mv = error_v * 1000.0

    print()
    print("DMM reference             : {:.6f} V".format(reference_voltage))
    print("Mean error ADC - DMM      : {:+.6f} V".format(error_v))
    print("Mean error ADC - DMM      : {:+.3f} mV".format(error_mv))

    if reference_voltage != 0:
        error_percent = 100.0 * error_v / reference_voltage
        print("Relative mean error        : {:+.3f} %".format(error_percent))

print()
print("----------------------------------------------------")
print("Files saved")
print("----------------------------------------------------")
print(sample_filename)
print(hist_filename)
print()
print("Copy both files to the computer before the next test.")
print("Delete old test files from the Pico if storage space is limited.")
print("----------------------------------------------------")
