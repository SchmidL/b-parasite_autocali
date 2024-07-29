import asyncio

import time
import re
import subprocess
import datetime
import json
import os
import threading

from ppk2_api.ppk2_api import PPK2_API
from rich.progress import Progress


def list_ppk2_devices():
    ppk2s_connected = PPK2_API.list_devices()
    if len(ppk2s_connected) == 1:
        return ppk2s_connected[0]
    elif len(ppk2s_connected) > 1:
        print("Multiple PPK2 devices found:")
        for i, device in enumerate(ppk2s_connected):
            print(f"{i + 1}: Port={device[0]}, Serial={device[1]}")
        while True:
            try:
                choice = int(input("Select the PPK2 device to use (1, 2, ...): ")) - 1
                if 0 <= choice < len(ppk2s_connected):
                    return ppk2s_connected[choice]
                else:
                    print("Invalid choice, please try again.")
            except ValueError:
                print("Invalid input, please enter a number.")
    else:
        raise Exception("No PPK2 devices found.")

def setup_ppk2():
    ppk2_port, ppk2_serial = list_ppk2_devices()
    print(f"Found PPK2 at {ppk2_port} with serial number {ppk2_serial}")
    ppk2_test = PPK2_API(ppk2_port, timeout=1, write_timeout=1, exclusive=True)
    ppk2_test.get_modifiers()
    ppk2_test.set_source_voltage(3300)
    ppk2_test.use_source_meter()  # set source meter mode
    ppk2_test.toggle_DUT_power("ON")  # enable DUT power
    return ppk2_test

def strip_ansi_escape_codes(text):
    """Remove ANSI escape codes from the given text."""
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x0e-\x1f])(?:[\x20-\x7e]{1,2}|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def clean_log_line(line):
    """Cleans a log line by removing unwanted characters and lines with only > and spaces."""
    clean_line = strip_ansi_escape_codes(line)
    clean_line = clean_line.strip()
    if not clean_line or clean_line.startswith(">") or clean_line.startswith(" "):
        return None
    return clean_line

rtt_process = None
logging_thread = None

def start_rtt_logging(output_file):
    global rtt_process, logging_thread

    # Initialize rtt_process
    rtt_process = subprocess.Popen(['rtt-console'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def log_output():
        global rtt_process
        with open(output_file, 'w') as f:
            while True:
                if rtt_process.poll() is not None:
                    break  # Exit loop if process has ended
                output = rtt_process.stdout.readline()
                if output == '':
                    break  # End of file reached
                if output:
                    decoded_output = output.strip()
                    cleaned_output = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', decoded_output)  # Strip ANSI escape codes
                    cleaned_output = cleaned_output.strip('>')
                    if cleaned_output.strip():  # Ensure the line is not empty or whitespace
                        f.write(cleaned_output + '\n')  # Ensure proper newlines
                        f.flush()  # Ensure the content is written to file immediately

    logging_thread = threading.Thread(target=log_output)
    logging_thread.start()

def stop_rtt_logging():
    global rtt_process
    if rtt_process:
        rtt_process.terminate()
        rtt_process.wait()
        rtt_process = None
    if logging_thread and logging_thread.is_alive():
        logging_thread.join()  # Ensure the logging thread is stopped

def prompt_user(message):
    while True:
        try:
            user_input = input(message).strip().lower()
            if user_input in ['ok', 'yes', 'y']:
                return True
            elif user_input in ['no', 'n']:
                return False
        except KeyboardInterrupt:
            print("\nProcess interrupted by user")
            raise

def save_parameters(sensor_name, condition, min_voltage, max_voltage, step_voltage, wait_time):
    parameters = {
        "sensor_name": sensor_name,
        "condition": condition,
        "min_voltage": min_voltage,
        "max_voltage": max_voltage,
        "step_voltage": step_voltage,
        "wait_time": wait_time
    }
    filename = f"{sensor_name}_calibration_{condition}_settings.json"
    with open(filename, 'w') as f:
        json.dump(parameters, f, indent=4)
    
    print(f"Parameters saved to {filename}")

def perform_measurement(sensor_name, condition, min_voltage=1700, max_voltage=3000, step_voltage=100, wait_time=10):
    # Save parameters to json file
    save_parameters(sensor_name, condition, min_voltage, max_voltage, step_voltage, wait_time)

    # Create a unique filename with the sensor name and condition
    log_file = f"{sensor_name}_calibration_{condition}.txt"
    
    # Start RTT logging in a separate thread
    start_rtt_logging(log_file)

    try:
        voltages = list(range(max_voltage, min_voltage, -step_voltage)) + list(range(min_voltage, max_voltage + step_voltage, step_voltage))
        
        for voltage in voltages:
            print(f"Setting voltage to {voltage / 1000.0}V")
            ppk2_test.set_source_voltage(voltage)
            time.sleep(wait_time)
            
    finally:
        stop_rtt_logging()

def main():
    global ppk2_test
    ppk2_test = setup_ppk2()

    # Prompt user for the sensor name
    sensor_name = input("Enter the sensor name: ").strip()

    # Ask user for the measurement condition
    condition = input("Do you want to measure in 'dry' or 'wet' conditions? ").strip().lower()
    if condition not in ['dry', 'wet']:
        print("Invalid condition. Please enter 'dry' or 'wet'.")
        return

    # Prompt user to setup sensor
    if prompt_user(f"Setup sensor in {condition} condition and type 'OK' when ready: "):
        perform_measurement(sensor_name, condition, min_voltage=2900, max_voltage=3000, step_voltage=100, wait_time=200)
        print(f"Measurement for {condition} condition completed successfully.")
    else:
        print("Measurement was not completed.")

if __name__ == "__main__":
    main()