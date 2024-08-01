import re
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime

def extract_sensor_data(file_path):
    times_in_seconds = []
    input_voltage = []
    soil_adc_output = []

    # Regular expression to match the desired pattern including time
    pattern = re.compile(r'\[(\d+:\d+:\d+\.\d+),\d+\] .*<inf> main: (\d+\.\d+);(\d+)')

    with open(file_path, 'r') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                time_str = match.group(1)  # Get the time string part without the code
                voltage = match.group(2)
                adc_output = match.group(3)


                # Convert time string to datetime object for the purpose of calculating seconds
                time_obj = datetime.strptime(time_str, '%H:%M:%S.%f')
                
                # Calculate seconds since 00:00:00
                seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1_000_000
                times_in_seconds.append(seconds)
                
                input_voltage.append(float(voltage))
                soil_adc_output.append(int(adc_output))

    return times_in_seconds, input_voltage, soil_adc_output


def format_parameter(param):
    """Formats a parameter with brackets if it's negative."""
    if param < 0:
        return f"({int(round(param))})"
    return f"{int(round(param))}"

def save_parameters(filename, parameters):
    """Saves the quadratic regression parameters to a file in the specified format and prints them."""
    with open(filename, 'w') as file:
        for condition, (a, b, c) in parameters.items():
            formatted_a = format_parameter(a)
            formatted_b = format_parameter(b)
            formatted_c = format_parameter(c)
            parameters_str = f"{condition} = <{formatted_a} {formatted_b} {formatted_c}>"
            file.write(parameters_str + '\n')
            print(parameters_str)

def round_first_digit(x):
    """Round a number to the first significant digit using a simple method."""
    if x == 0:
        return 0
    return int(x * 10) / 10.0

def quadratic_regression(voltage, output):
    # Fit a 2nd-degree polynomial (quadratic) to the data
    coefficients = np.polyfit(voltage, output, 2)
    
    # Extract coefficients (a, b, c) of the polynomial
    a_raw, b_raw, c_raw = coefficients
    
    # Round the coefficients to the first significant digit
    rounded_a = round_first_digit(a_raw)
    rounded_b = round_first_digit(b_raw)
    rounded_c = round_first_digit(c_raw)
    
    # Multiply the rounded coefficients by 1000
    a_mV = rounded_a * 1000
    b_mV = rounded_b * 1000
    c_mV = rounded_c * 1000
    
    return a_mV, b_mV, c_mV, a_raw, b_raw, c_raw




def create_plot(input_voltage, soil_adc_output, a, b, c, ax, condition):
    """Creates a scatter plot and a quadratic fit line for the given data."""
    ax.scatter(input_voltage, soil_adc_output, color='blue', label='Measurements')

    # Quadratic fit line
    fit_x = np.linspace(min(input_voltage), max(input_voltage), 100)
    fit_y = a * fit_x**2 + b * fit_x + c
    ax.plot(fit_x, fit_y, color='red', label='Quadratic Fit')

    ax.set_xlabel('Input Voltage (V)')
    ax.set_ylabel('Soil ADC Output')
    ax.set_title(f'{condition.capitalize()} Condition')
    ax.legend()
    ax.grid(True)

def hysteresis_plot(input_voltage, soil_adc_output, time):
    """
    Creates a scatter plot with x-axis as 'input_voltage', y-axis as 'soil_adc_output',
    and time represented as colors using the 'viridis' colormap.

    Parameters:
    input_voltage (list or array-like): Data for the x-axis.
    soil_adc_output (list or array-like): Data for the y-axis.
    time (list or array-like): Data for the color mapping.

    Returns:
    None
    """
    # Create the scatter plot
    plt.scatter(input_voltage, soil_adc_output, c=time, cmap='viridis', s=50, edgecolor='k', alpha=0.7)

    # Add color bar to show the mapping of time to colors
    cbar = plt.colorbar()
    cbar.set_label('Time [s]')

    # Add labels and title
    plt.xlabel('Input Voltage [V]')
    plt.ylabel('Soil ADC Output [a.u.]')
    plt.title('Input Voltage vs ADC Voltage over time')

    # Show the plot
    plt.show()



def process_measurements(sensor_name, output_dir='output'):
    dry_file = os.path.join(output_dir, f"{sensor_name}_calibration_dry.txt")
    wet_file = os.path.join(output_dir, f"{sensor_name}_calibration_wet.txt")

    parameters = {}

    numb_files = sum([os.path.exists(dry_file),os.path.exists(wet_file)])
    fig, axs = plt.subplots(1, numb_files, figsize=(12, 6))  # Create a subplot with 1 row and 2 columns

    if os.path.exists(dry_file):
        print("Processing dry dataset...")
        _, input_voltage_dry, soil_adc_output_dry = extract_sensor_data(dry_file)
        a_dry, b_dry, c_dry, a_dry_raw, b_dry_raw, c_dry_raw = quadratic_regression(input_voltage_dry, soil_adc_output_dry)
        parameters['dry'] = (a_dry, b_dry, c_dry)
        if numb_files==1:
            create_plot(input_voltage_dry, soil_adc_output_dry, a_dry_raw, b_dry_raw, c_dry_raw, axs, 'dry')
        else:
            create_plot(input_voltage_dry, soil_adc_output_dry, a_dry_raw, b_dry_raw, c_dry_raw, axs[0], 'dry')
    else:
        print(f"Dry dataset file {dry_file} does not exist.")
    
    if os.path.exists(wet_file):
        print("Processing wet dataset...")
        _, input_voltage_wet, soil_adc_output_wet = extract_sensor_data(wet_file)
        a_wet, b_wet, c_wet, a_wet_raw, b_wet_raw, c_wet_raw = quadratic_regression(input_voltage_wet, soil_adc_output_wet)
        parameters['wet'] = (a_wet, b_wet, c_wet)
        if numb_files==1:
            create_plot(input_voltage_wet, soil_adc_output_wet, a_wet_raw, b_wet_raw, c_wet_raw, axs, 'wet')
        else:
            create_plot(input_voltage_wet, soil_adc_output_wet, a_wet_raw, b_wet_raw, c_wet_raw, axs[1], 'wet')
    else:
        print(f"Wet dataset file {wet_file} does not exist.")

    # Save parameters to a single file

    save_parameters(os.path.join(output_dir, f"{sensor_name}_calibration_parameters.txt"), parameters)

    plt.tight_layout()  # Adjust subplot parameters to give some padding
    plt.savefig(os.path.join(output_dir, f"{sensor_name}_calibration_plot.png"))
    plt.close()
    # plt.show()  # Display plots interactively



