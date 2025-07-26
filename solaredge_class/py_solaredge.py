from pymodbus.client.tcp import ModbusTcpClient

class SolarEdgeInverter:
    
    def __init__(self, host, port=1502, unit_id=1):
        self.client = ModbusTcpClient(host=host, port=port)
        self.unit_id = unit_id

    def connect(self):
        try:
            self.client.connect()
            print("Connection established successfully.")

            if not self.client.is_socket_open():
                raise ConnectionError(f"Failed to establish connection to Modbus server.")
                
        except Exception as e:
            raise ConnectionError(f"Unable to connect to the Modbus server: {e}")

    def close(self):
        self.client.close()
        self.unit_id = None
        self.client = None
        print("Connection closed.")

    def _read_modbus_value(self, address, datatype, count, sf_address=None, sf_datatype=ModbusTcpClient.DATATYPE.INT16):
        result = self.client.read_holding_registers(address=address, count=count)
        if result.isError():
            raise Exception(f"Failed to read {count} registers at address {address}")
        value = self.client.convert_from_registers(result.registers, datatype, word_order="big")

        # Apply scale factor if provided
        if sf_address is not None:
            sf_result = self.client.read_holding_registers(address=sf_address, count=1)
            if sf_result.isError():
                raise Exception(f"Failed to read scale factor at address {sf_address}")
            sf = self.client.convert_from_registers(sf_result.registers, sf_datatype, "big")
            return value * 10 ** sf
        return value
    
        # --- Funzioni per leggere i dati comuni (SunSpec Model 1) ---

    def get_sunspec_id(self) -> int:
        """ Value = "SunS" (0x53756e53). Uniquely identifies this as a SunSpec MODBUS
 Mapv"""
        return self._read_modbus_value(address=0, datatype=ModbusTcpClient.DATATYPE.UINT32, count=2)

    def get_common_sunspec_did(self) -> int:
        """Value = 0x0001. Uniquely identifies this as a SunSpec Common Model Block."""
        return self._read_modbus_value(address=2, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1)

    def get_common_sunspec_length(self) -> int:
        """65 = Length of block in 16-bit registers."""
        return self._read_modbus_value(address=3, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1)

    def get_manufacturer(self) -> str:
        """Value Registered with SunSpec = "SolarEdge "."""
        return self._read_modbus_value(address=4, datatype=ModbusTcpClient.DATATYPE.STRING, count=16) # 32 bytes = 16 registers

    def get_model(self) -> str:
        """SolarEdge Specific Value."""
        return self._read_modbus_value(address=20, datatype=ModbusTcpClient.DATATYPE.STRING, count=16) # 32 bytes = 16 registers

    def get_version(self) -> str:
        """SolarEdge Specific Value."""
        return self._read_modbus_value(address=44, datatype=ModbusTcpClient.DATATYPE.STRING, count=8) # 16 bytes = 8 registers

    def get_serial_number(self) -> str:
        """SolarEdge Unique Value."""
        return self._read_modbus_value(address=52, datatype=ModbusTcpClient.DATATYPE.STRING, count=16) # 32 bytes = 16 registers

    def get_device_address(self) -> int:
        """Value MODBUS Unit ID."""
        return self._read_modbus_value(address=68, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1)

    # --- Functions to read specific inverter data ---

    def get_sunspec_did(self) -> int:
        """ 101 = single phase
            102 = split phase
            103 = three phase."""
        return self._read_modbus_value(address=69, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1)

    def get_sunspec_length(self) -> int:
        """50 = Length of model block. Units: Registers"""
        return self._read_modbus_value(address=70, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1) 

    def get_ac_currents(self) -> dict:
        """
        AC currents values (total and per phase). Units: Amps.
        Keys: 'total', 'phase_a', 'phase_b', 'phase_c'.
        """
        sf_address = 75
        return {
            "total": self._read_modbus_value(address=71, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=sf_address),
            "phase_a": self._read_modbus_value(address=72, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=sf_address),
            "phase_b": self._read_modbus_value(address=73, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=sf_address),
            "phase_c": self._read_modbus_value(address=74, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=sf_address),
        }

    def get_ac_voltages(self) -> dict:
        """
        AC voltages values (line-to-line and line-to-neutral). Units: Volts.
        Keys: 'ab', 'bc', 'ca', 'an', 'bn', 'cn'.
        """
        sf_address = 82
        return {
            "ab": self._read_modbus_value(address=76, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=sf_address),
            "bc": self._read_modbus_value(address=77, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=sf_address),
            "ca": self._read_modbus_value(address=78, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=sf_address),
            "an": self._read_modbus_value(address=79, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=sf_address),
            "bn": self._read_modbus_value(address=80, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=sf_address),
            "cn": self._read_modbus_value(address=81, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=sf_address),
        }

    def get_ac_power(self) -> float:
        """AC power value. Units: Watts."""
        return self._read_modbus_value(address=83, datatype=ModbusTcpClient.DATATYPE.INT16, count=1, sf_address=84)

    def get_ac_frequency(self) -> float:
        """AC frequency value. Units: Hz."""
        return self._read_modbus_value(address=85, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=86)

    def get_ac_apparent_power(self) -> float:
        """Apparent power value. Units: VA."""
        return self._read_modbus_value(address=87, datatype=ModbusTcpClient.DATATYPE.INT16, count=1, sf_address=88)

    def get_ac_reactive_power(self) -> float:
        """Reactive power value. Units: VAR."""
        return self._read_modbus_value(address=89, datatype=ModbusTcpClient.DATATYPE.INT16, count=1, sf_address=90)

    def get_ac_power_factor(self) -> float:
        """Power factor value. Units: %"""
        return self._read_modbus_value(address=91, datatype=ModbusTcpClient.DATATYPE.INT16, count=1, sf_address=92)

    def get_total_energy_wh(self) -> float:
        """ AC Lifetime Energy production. Units: WattHours."""
        return self._read_modbus_value(address=93, datatype=ModbusTcpClient.DATATYPE.UINT32, count=2, sf_address=95)

    def get_dc_current(self) -> float:
        """DC current value. Units: Amps."""
        return self._read_modbus_value(address=96, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=97)

    def get_dc_voltage(self) -> float:
        """DC voltage value. Units: Volts."""
        return self._read_modbus_value(address=98, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1, sf_address=99)

    def get_dc_power(self) -> float:
        """DC power value. Units: Watts."""
        return self._read_modbus_value(address=100, datatype=ModbusTcpClient.DATATYPE.INT16, count=1, sf_address=101)

    def get_temperature_sink(self) -> float:
        """Heat Sink Temperature. Units: Degree C."""
        return self._read_modbus_value(address=103, datatype=ModbusTcpClient.DATATYPE.INT16, count=1, sf_address=106)

    def get_status(self) -> int:
        """Operating State."""
        return self._read_modbus_value(address=107, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1)

    def get_status_vendor(self) -> int:
        """Vendor-defined operating state and error codes. 
        For error description, meaning, and troubleshooting, 
        refer to the SolarEdge Installation Guide."""
        return self._read_modbus_value(address=108, datatype=ModbusTcpClient.DATATYPE.UINT16, count=1)

    def get_status_vendor4(self) -> int:
        """ Vendor-defined operating state and
        error codes. For error description,
        meaning, and troubleshooting, refer
        to the SolarEdge Installation Guide,
        16MSB for controller type (3x, 8x,
        18x) and 16 LSB for error code."""
        return self._read_modbus_value(address=119, datatype=ModbusTcpClient.DATATYPE.UINT32, count=2)
    
