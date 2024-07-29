import time
import re
import subprocess
import json
import os
import threading


from ppk2_api.ppk2_api import PPK2_API

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

    # Start RTT logging using rtt-console with the new arguments
    rtt_process = subprocess.Popen(
        ['rtt-console', '--log-file', log_file, '--no-input'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        voltages = list(range(max_voltage, min_voltage, -step_voltage)) + list(range(min_voltage, max_voltage + step_voltage, step_voltage))
        
        with Progress() as progress:
            task = progress.add_task(f"[green]Measuring {condition} condition...", total=len(voltages))

            for voltage in voltages:
                print(f"Setting voltage to {voltage / 1000.0}V")
                ppk2_test.set_source_voltage(voltage)
                time.sleep(wait_time)
                progress.advance(task)

            
    finally:
        rtt_process.terminate()
        rtt_process.wait()

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

def main():
    global ppk2_test
    ppk2_test = setup_ppk2()

    # Prompt user for the sensor name
    sensor_name = input("Enter the sensor name: ").strip()

    # Dry condition measurement
    if prompt_user("Setup sensor in 'dry' (air) condition and type 'OK' when ready: "):
        perform_measurement(sensor_name, 'dry', min_voltage=2900, max_voltage=3000, step_voltage=100, wait_time=10)
        print("Measurement for 'dry' condition completed successfully.")
    else:
        print("Measurement for 'dry' condition was not completed.")
        return

    # Wet condition measurement
    if prompt_user("Setup sensor in 'wet' (water) condition and type 'OK' when ready: "):
        perform_measurement(sensor_name, 'wet', min_voltage=2900, max_voltage=3000, step_voltage=100, wait_time=10)
        print("Measurement for 'wet' condition completed successfully.")
    else:
        print("Measurement for 'wet' condition was not completed.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()