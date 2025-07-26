# SolarEdge Inverter Monitoring via Modbus TCP

This project provides a Python class to interact with and monitor SolarEdge inverters using the Modbus TCP protocol. It allows you to read a wide range of data, from general inverter information to detailed electrical parameters, including automatic handling of scale factors.


## Prerequisites

Before using this class, ensure you meet the following requirements:

### 1\. Python and `pymodbus` Library

  * You'll need **Python 3.x** installed on your system.

  * Install the `pymodbus` library. **This project was developed and tested with `pymodbus` version 3.9.2.** It is highly recommended to use this specific version to ensure compatibility.

    ```bash
    pip install pymodbus==3.9.2
    ```

### 2\. SolarEdge Inverter Modbus TCP Configuration

  * **Enabling Modbus TCP Communication:**
    Modbus TCP communication on your SolarEdge inverter might not be enabled by default. To activate it, you have a few options:
      * **Via an installer:** A certified SolarEdge installer can enable the Modbus TCP functionality directly from the inverter using the **SetApp** application.
      * **Via SolarEdge online support:** You can contact SolarEdge's online customer support. By providing them with the necessary information about your installation, they can enable Modbus TCP communication **remotely** as well.
  * **Port Verification:**
    Once enabled, ensure that the Modbus TCP port is open and accessible. SolarEdge inverters typically use **port 1502** for Modbus TCP. However, **port 502** is also a common default for Modbus. Consult your specific inverter's documentation or network settings to confirm the correct port. Without the correct port open, the connection will fail.


## Installation

Clone this repository to your local system:

```bash
git clone https://github.com/YourUsername/YourRepoName.git
cd YourRepoName/solaredge_class
```


## Usage

The `SolarEdgeInverter` class is located in the `py_solaredge.py` file. You can import it into your Python script to start monitoring your inverter.

### Example Usage

```python
from solaredge_class.py_solaredge import SolarEdgeInverter

# Replace with your SolarEdge inverter's IP address
INVERTER_HOST = "192.168.1.XXX"
INVERTER_PORT = 1502  # Default Modbus TCP port for SolarEdge (verify with your inverter's settings)
INVERTER_UNIT_ID = 1  # Default Modbus unit ID

inverter = None
try:
    inverter = SolarEdgeInverter(host=INVERTER_HOST, port=INVERTER_PORT, unit_id=INVERTER_UNIT_ID)
    inverter.connect()
    print("Connection to SolarEdge inverter established.")

    # Example of reading common data
    print(f"\n--- Inverter Common Data ---")
    print(f"Manufacturer: {inverter.get_manufacturer()}")
    print(f"Model: {inverter.get_model()}")
    print(f"Serial Number: {inverter.get_serial_number()}")
    print(f"Firmware Version: {inverter.get_version()}")
    print(f"Modbus Device ID: {inverter.get_device_address()}")

    # Example of reading specific inverter data
    print(f"\n--- Inverter Electrical Data ---")
    ac_currents = inverter.get_ac_currents()
    print(f"Total AC Current: {ac_currents['total']:.2f} A")
    print(f"AC Power: {inverter.get_ac_power():.2f} W")
    print(f"AC Frequency: {inverter.get_ac_frequency():.2f} Hz")
    print(f"Total Lifetime Energy: {inverter.get_total_energy_wh():.2f} Wh")
    print(f"DC Voltage: {inverter.get_dc_voltage():.2f} V")
    print(f"DC Power: {inverter.get_dc_power():.2f} W")
    print(f"Heat Sink Temperature: {inverter.get_temperature_sink():.2f} °C")
    print(f"Operating Status: {inverter.get_status()}")

except ConnectionError as ce:
    print(f"Connection error: {ce}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if inverter:
        inverter.close()
```
Output:

```bash
Connection established successfully.

--- Inverter Common Data ---
Manufacturer: SolarEdge
Model: SE4000H-RW000BEN4
Serial Number: 123ABC12
Firmware Version: 0004.0023.0027
Modbus Device ID: 1

--- Inverter Electrical Data ---
Total AC Current: 9.11 A
AC Power: 2199.00 W
AC Frequency: 50.01 Hz
Total Lifetime Energy: 7578077.00 Wh
DC Voltage: 370.30 V
DC Power: 2233.40 W
Heat Sink Temperature: 41.61 °C
Operating Status: 4

Connection closed.
```
