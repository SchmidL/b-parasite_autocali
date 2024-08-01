from autocalibration_dataprocessing import *

if __name__ == "__main__":

    # ### 15 min stationary, dry

    # times_15min_dry, input_voltage_15min_dry, soil_adc_output_15min_dry = extract_sensor_data('data_analysis/sensor_dry_15min_calibration_dry.txt')

    # # hysteresis_plot(input_voltage_15min_dry, soil_adc_output_15min_dry,times_15min_dry)


    # ### 20s stationary, full voltage range, dry
    # times_20s_dry, input_voltage_20s_dry, soil_adc_output_20s_dry = extract_sensor_data('data_analysis/sensor_long_20s_dry_calibration_dry.txt')

    # hysteresis_plot(input_voltage_20s_dry, soil_adc_output_20s_dry,times_20s_dry)
    
    # process_measurements('sensor_long_20s_dry', output_dir='./data_analysis')


    # ### 10s stationary, full voltage range, both conditions


    # times_10s_dry, input_voltage_10s_dry, soil_adc_output_10s_dry = extract_sensor_data('data_analysis/sensor_10s_calibration_dry.txt')
    # times_10s_wet, input_voltage_10s_wet, soil_adc_output_10s_wet = extract_sensor_data('data_analysis/sensor_10s_calibration_wet.txt')


    ### 10s stationary, full voltage range, wet in plastic instead of glass
    process_measurements('sensor_10s_plastic', output_dir='./data_analysis')




    # # print("Wet Calibration - Input Voltage:", input_voltage_wet)
    # # print("Wet Calibration - Soil ADC Output:", soil_adc_output_wet)

    # # print("Dry Calibration - Input Voltage:", input_voltage_dry)
    # # print("Dry Calibration - Soil ADC Output:", soil_adc_output_dry)

    # # a_wet, b_wet, c_wet, _, _, _ =  quadratic_regression(input_voltage_wet, soil_adc_output_wet)
    # # a_dry, b_dry, c_dry, _, _, _ =  quadratic_regression(input_voltage_dry, soil_adc_output_dry)
    # # print(f"Final parameter - wet: a={a_wet:.0f}, b={b_wet:.0f}, c={c_wet:.0f}")
    # # print(f"Final parameter - dry: a={a_wet:.0f}, b={b_wet:.0f}, c={c_wet:.0f}")

    hysteresis_plot(input_voltage_10s_dry, soil_adc_output_10s_dry,times_10s_dry)
    hysteresis_plot(input_voltage_10s_wet, soil_adc_output_10s_wet,times_10s_wet)

    # #process_measurements('sensor1', output_dir='.')
    process_measurements('sensor_10s', output_dir='./data_analysis')


