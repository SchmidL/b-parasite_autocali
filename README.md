# b-parasite Auto-Calibration Routine

This repository contains an auto-calibration routine developed for the b-parasite project. The b-parasite is an open-source soil moisture and ambient temperature/humidity sensor. This routine automates the calibration process, allowing for faster and less error-prone measurements.

## Description

The auto-calibration routine is designed to simplify the calibration process of the b-parasite sensors by automating voltage sweeps and capturing the output ADC voltage. The routine is designed to capture both dry and wet calibration conditions, and directly computes the needed coefficient which insert firmware source before build.

The script depends heavily on the ppk2-api project https://github.com/IRNAS/ppk2-api-python from https://github.com/IRNAS and from the original rtt-console https://github.com/Mcublog/rtt-console by https://github.com/Mcublog

## Hardware
In the current state, the following hardware is needed
- b-parasite (fully populated)
- nrf Power Profiling Kit 2 (PPK2)
- J-Link programmer (in my case an J-Link edu mini)

## Installation

To use this auto-calibration routine, follow these steps:

1. **Clone the repositories:**
   ```bash
   git clone https://github.com/SchmidL/b-parasite-autocalibration.git
   cd b-parasite-autocalibration

   ```
1. **Create and activate a virtual environment (optional but recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

1. **Install the required dependencies:**
    ```bash
    pip install numpy, matplotlib, ppk2-api
    ```
1. **Additionall install modified rtt-console**
    ```bash
    git clone https://github.com/SchmidL/rtt-console
    cd rtt-console
    pip install .
    cd ../
    ```

## Wiring
For the calibration, the following setup is needed.
- The b-parasite is connected to a J-Link. In the following overview it is connected via a normal pitch to half pitch converter
- The b-parasite is powered by the nrf PPK2. This should be in the best case connected via the battery terminal. (I made a small battery dummy from scrap part)
- The "+"-terminal should be connected to VOUT on the PPK2, the "-"-terminal to GND

![wiring_overview](/docs/img/wiring_bparasite_calibration.jpeg)

## Usage

To run the auto-calibration routine, follow these steps:

1. Connect all tools and b-parasite as  [previously](#hardware-and-wiring) described.
1. Run the auto-calibration script:
    ```bash
    python autocalibration.py
    ```
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
## Analysis

Coming soon...

## Contributing

We welcome contributions to improve the auto-calibration routine. If you have suggestions or improvements, please submit a pull request or open an issue.

## License

This project code is licensed under the MIT License - see the [LICENSE](https://opensource.org/licenses/MIT) file for details.