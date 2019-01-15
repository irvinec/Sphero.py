"""
"""

import os
import uuid
import pygatt

_BLE_SERVICE = uuid.UUID("22bb746f-2bb0-7554-2d6f-726568705327")
# Sending 0x01 to BLEService and WakeCharacteristic is for wake.
_BLE_SERVICE_WAKE = uuid.UUID("22bb746f-2bbf-7554-2d6f-726568705327")
_ROBOT_SERVICE = uuid.UUID('22BB746F-2BA0-7554-2D6F-726568705327')
_ROBOT_SERVICE_CONTROL = uuid.UUID('22BB746F-2BA1-7554-2D6F-726568705327')
_ROBOT_SERVICE_RESPONSE = uuid.UUID('22BB746F-2BA6-7554-2D6F-726568705327')



class BleInterface(object):
    """
    """

    def __init__(self, name='SK', port=1):
        self._name = name
        self._address = None
        self._port = port
        self._device = None

    def __del__(self):
        self.close()

    def connect(self, num_retry_attempts=1):
        """
        """
        for num_tries in range(num_retry_attempts):
            if self._address is None:
                adapter, _, self._address, _ = _find_device(self._name)

            if self._address is not None:
                pass
                # connect to the device and setup sockets.
                self._device = adapter.connect(
                    address=self._address,
                    address_type=pygatt.BLEAddressType.random
                )
                # TODO: Need to look at spherojs to understand the protocol here.
                # we might need to look for individual characteristics.
                characteristics = self._device.discover_characteristics()
                # TODO: try turn on full dev mode
                # Set TXPower
                # Send something to ANTI-DOS service/char.
                # see sphero.js
                # We probably want the bluetooth interface to convert to bytes not, spheropy
                self._device.char_write(_BLE_SERVICE_WAKE, bytearray([0x01]))
                print('Just sent wake command.')
            elif num_tries >= num_retry_attempts - 1:
                if self._address is None:
                    raise RuntimeError(
                            f'Could not find device with name {self._name} after {num_tries} tries.'
                    )
                else:
                    raise RuntimeError(
                        f'Count not connect to device {self._address} after {num_tries} tries.'
                    )

    def send(self, data):
        """
        """
        #b'\xff\xfe\x020\x00\x05\x7f\x00\x00\x01H'
        #self._device.char_write(_ROBOT_SERVICE_CONTROL, bytearray([255, 254, 2, 48, 0, 5, 127, 0, 0, 1, 72]))
        self._device.char_write(_ROBOT_SERVICE_CONTROL, data)


    def recv(self, num_bytes):
        """
        """
        return self._device.char_read(_ROBOT_SERVICE_RESPONSE, timeout=5)


    def close(self):
        """
        """
        self._device.disconnect()

def _find_device(name):
    """
    """
    found_device = False
    found_device_name = None
    found_device_address = None

    # Search for adapter (Windows only)
    adapter = None
    found_adapter = False
    if is_windows():
        for port_num in range(10):
            try:
                adapter = pygatt.BGAPIBackend(serial_port=f'COM{port_num}')
                adapter.start()
                found_adapter = True
                break
            except pygatt.exceptions.NotConnectedError:
                continue
    else:
        adapter = pygatt.backends.GATTToolBackend()
        adapter.start()
        found_adapter = True

    if not found_adapter:
        raise RuntimeError('Could not find bluetooth adapter.')

    nearby_devices = adapter.scan()
    if nearby_devices:
        for device in nearby_devices:
            if device['name'].startswith(name):
                found_device = True
                found_device_address = device['address']
                found_device_name = device['name']
                break

    if found_device:
        print(f'Found device named: {found_device_name} at {found_device_address}')

    return adapter, found_device, found_device_address, found_device_name

def is_windows():
    return os.name == 'nt'

def is_linux():
    return os.name == 'posix'