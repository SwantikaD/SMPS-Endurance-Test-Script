# SMPS-Endurance-Test-Script

## Overview
This Python script automates testing of the SMPS (Switched Mode Power Supply) PCB, which converts high voltage (HV) input to two low voltage (LV) outputs. It uses the PyVISA library to control the Sorenson XG600-1.4 power supply and Agilent 34970A Data Acquisition/Switch Unit. The Sorenson XG600-1.4 powers the SMPS PCB, while the Agilent 34970A manages the load connections, switching them on and off. The script cycles power to the SMPS and adjusts the load based on user-defined settings. Diagnostics are logged every second for reference and troubleshooting.

The repository includes the Python script for customization, and an executable (.exe) is available for direct use without additional setup in the "Releases" section.


## Features
- **Instrument communication check:** Automatically verifies connectivity with the power supply and switch unit at the start of each test.
- **User-configurable PSU settings:** Allows control of input voltage, current, and power cycle timing.
- **Switch unit control:** Automates load switching for up to 3 SMPS PCBs, enabling simultaneous testing.
- **1-second data logging:** Records voltage and current values from the power supply. (Load voltages and currents are logged using NI DAQ)
- **Retry mechanism:** Retries communication with instruments up to 3 times before aborting the test.
- **Safe shutdown:** Easily stop the test and power off all instruments with CTRL+C.


## Prerequisites 

- ***For running/customizing the Python script (SMPSEnduranceTestScript.py):***

    - Python 3.10 (or higher)
    - PyVISA (`pip install pyvisa==1.13.0` or `pip install -r requirements.txt`)
    - National Instruments VISA (or another VISA backend)
      You can download the NI-VISA drivers from the [NI website](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html).

- ***For running the Executable (SMPSEnduranceTestScript.exe):***

    - National Instruments VISA (or another VISA backend)
      You can download the NI-VISA drivers from the [NI website](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html).


## Usage
1. Download and extract `Cap-Bank-Tester-v1.0.0.zip` from the Releases section of this [repository](https://github.com/SwantikaD/SMPS-Endurance-Test-Script). The extracted folder will contain the executable. 

2. Create `Data` folder in C drive to store the test data logs. 

3. Open command prompt, navigate to the folder containing the executable and run it:
    - cd <path/to/executable>
    - SMPSEnduranceTestScript.exe

4. Enter the settings for input HV Power Supply when prompted. See example below:
    - Enter voltage setting in volts: 400
    - Enter current setting in amps: 0.8
    - Enter HV on time in sec: 900
    - Enter HV off time in sec: 900

5. The test starts automatically after configuration.

6. Press Ctrl+C to stop the test at any time. 


## Logging
Test data is logged every second and saved as `SorensonPSU-{}.csv` in the C:/Data folder. The log captures the following parameters with timestamps:

- HV Voltage (HV_V)
- HV Current (HV_I)


## Troubleshooting
1. Connection Issues
    - Ensure all hardware connections are correct and secure.
    - Verify that the instruments are using the correct serial port and GPIB addresses:
        - HV PSU: ASRL4::INSTR
        - Switch Unit: GPIB0::10::INSTR


2. Communication Errors
    If the instrument connects but fails to communicate (i.e., all 3 retry attempts fail):
    - Power cycle the instrument and rerun the script.
    - If the issue persists, use Keysight Command Expert(CE) to reset the instrument:
        - Install Keysight Command Expert.
        - Connect to the instrument and send a reset SCPI command.
        - Watch this [tutorial](https://www.youtube.com/watch?v=nHSU6RjHCqE) to set up an instrument and send SCPI commands in CE.  

