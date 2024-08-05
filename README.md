# b-parasite Auto-Calibration Routine

This repository contains an auto-calibration routine developed for the [b-parasite project](https://github.com/rbaron/b-parasite) by [rbaron](https://github.com/rbaron). The b-parasite is an open-source soil moisture and ambient temperature/humidity sensor. This routine automates the calibration process, allowing for faster and less error-prone measurements.

## Description

The auto-calibration routine is designed to simplify the calibration process of the b-parasite sensors by automating voltage sweeps and capturing the output ADC voltage. The routine is designed to capture both dry and wet calibration conditions, and directly computes the needed coefficient which insert firmware source before build.

The script depends heavily on the [ppk2-api project](https://github.com/IRNAS/ppk2-api-python) from [IRNAS](https://github.com/IRNAS) and from the original [rtt-console](https://github.com/Mcublog/rtt-console) by [Mcublog](https://github.com/Mcublog)

## Hardware
In the current state, the following hardware is needed
- b-parasite (fully populated)
- nordic semiconductor Power Profiling Kit 2 (PPK2)
- J-Link programmer (in my case an J-Link edu mini)

## Installation

To use this auto-calibration routine, follow these steps:

1. **Clone the repositories:**
   ```bash
   git clone git@github.com:SchmidL/b-parasite_autocali.git
   cd b-parasite_autocali
   ```
1. **Create and activate a virtual environment (optional but recommended):**
    ```bash
    conda create -n bparasite_autocali python=3.10
    conda activate bparasite_autocali
    ```

1. **Install the required dependencies:**
    ```bash
    pip install numpy matplotlib rich
    ```
1. **Additionall install modified rtt-console**
    ```bash
    git clone git@github.com:SchmidL/rtt-console.git
    cd rtt-console
    pip install .
    cd ../

    git clone https://github.com/IRNAS/ppk2-api-python.git
    cd ppk2-api-python
    pip install .
    cd ../
    ```

## Wiring
For the calibration, the following setup is needed.
- The b-parasite is connected to a J-Link. In the following overview it is connected via a normal pitch to half pitch converter
- The b-parasite is powered by the PPK2. This should be in the best case connected via the battery terminal. (I made a small battery dummy from scrap part)
- The "+"-terminal should be connected to VOUT on the PPK2, the "-"-terminal to GND

![wiring_overview](/docs/img/wiring_bparasite_calibration.jpeg)

## Usage

To run the auto-calibration routine, follow these steps:

1. Connect all tools and b-parasite as  [previously](#hardware-and-wiring) described.
1. Run the auto-calibration script:
    ```bash
    python autocalibration.py
    ```
    The parameters like max/min voltage for the sweep, the stationary duration, and the step size can be changed in the python file
1. It can happen that the terms and condition of the J-LINK have to be accepted. Without that no data will be logged!
1. Then follow the prompts. When you get asked to measure the "dry" condition, keep the sensor dry, in open-air.
When in "wet" condition, put it in glass of water until the marking of the silkscreen on the PCB.
Additionally, a name for the sensor can be entered for later identification of the files.
The script will automatically perform the voltage sweeps and log the data.

## Output

The routine generates the following output:

- **Log Files**: Two log files (one for dry conditions and one for wet conditions) containing the calibration data.
	- Format: `{sensor_name}_calibration_{condition}.txt`
- **JSON Settings File**: A JSON file containing the calibration parameters used during the measurement.
	- Format: `{sensor_name}_calibration_{condition}_settings.json`
- **Parameter File**: A text file containing the parameters, have to be copied into the firmware
- **Calibration Plot**: Two PNG showing the data and the calibration function fit for visual validation of the processing.

### Example Log File:

```
[00:00:00.879,730] [0m<inf> main: 3.26;496[0m
[00:00:01.379,943] [0m<inf> main: 3.28;496[0m
[00:00:03.350,250] [0m<inf> main: 3.27;497[0m
[00:00:03.850,402] [0m<inf> main: 3.27;496[0m
[00:00:04.350,585] [0m<inf> main: 3.28;497[0m
[00:00:04.850,738] [0m<inf> main: 3.28;497[0m
[00:00:05.350,891] [0m<inf> main: 3.28;495[0m
[00:00:05.851,074] [0m<inf> main: 3.28;496[0m
[00:00:06.351,226] [0m<inf> main: 3.27;498[0m
[00:00:06.851,379] [0m<inf> main: 3.28;497[0m
...
```
Example JSON Settings File:
```
{
    "sensor_name": "example_sensor",
    "condition": "dry",
    "min_voltage": 2000,
    "max_voltage": 3000,
    "step_voltage": 250,
    "wait_time": 2
}
```
## Remarks
For me several points showed up during the development:
- the maximum of data capture was 15 min, longer session were not captured anymore

## Analysis
Having this code already, I conducted some - not very research grade - test for stuff I was wandering.

#### First calibration
In a first experiment, the setup was test with a 10s stationary duration for the quasi full voltage range, which is accepted from the module.
Overall the data looks clean, besides a at very low voltage of ~1.7V where the values of the ADC are a bit higher. But I see that in general already an edge case, where the battery would need to be replaced anyway soon.
![10s_full test](/docs/img/sensor_10s_calibration_plot.png)

#### Hysteresis
I was curious if any hysteresis is present with longer operation time (no sleep). But in the plot not significant discrepancies is present. 
![hysteresis test](/docs/img/sensor_20s_hysteresis.png)

#### Glass vs Plastic Cup
A short test was also conducted if there is a difference seen using a glass or plastic cup for the calibration. I expected no big changes.
This can also be seen in the paramtere which are quite close, and e.g. show a difference due to the not so perfectly same adjusted water level.

```
wet_glass = <(-3400) 56600 (-38400)>
wet_plastic = <(-3300) 55800 (-36600)>
```
#### Consistency of the calibration curve for multiple sensors
After the first batch calibration, a comparison of the multiple calibration curves, should show if one calibration per batch, or even hardware version would be possible.
It shows that the most of the sensors are in an equal range besides 1 (sensor6). What the difference is, I cannot say for now, but will show with more sensors in use
![consistency_multiple_sensors](/docs/img/consistency_multiple_sensors.png)

## Contributing

We welcome contributions to improve the auto-calibration routine. If you have suggestions or improvements, please submit a pull request or open an issue.

## License

This project code is licensed under the MIT License - see the [LICENSE](https://opensource.org/licenses/MIT) file for details.
