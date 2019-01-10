"""
"""

import bluetooth # pybluez
import bluetooth.ble as ble

class BleInterface(object):
    """
    """

    def __init__(self, target_name='SK', port=1):
        self._target_name = target_name
        self._target_address = None
        self._port = port
        self._requester = None

    def __del__(self):
        self.close()

    def connect(self, num_retry_attempts=1):
        """
        """
        for num_tries in range(num_retry_attempts):
            if self._target_address is None:
                _, self._target_address, _ = _find_device(self._target_name)

            if self._target_address is not None:
                self._requester = ble.GATTRequester(self._target_address, True) # True means connect to the device
                #self._response = ble.GATTResponse(self._target_address)
                result = self._requester.discover_characteristics()
                print (f'Result of discover_characteristics(): {result}')
            elif num_tries >= num_retry_attempts:
                if self._target_address is None:
                    raise RuntimeError(
                            f'Could not find device with name {self._target_name} after {num_tries} tries.'
                    )
                else:
                    raise RuntimeError(
                        f'Count not connect to device {self._target_address} after {num_tries} tries.'
                    )

    def send(self, data):
        """
        """
        pass


    def recv(self, num_bytes):
        """
        """
        pass


    def close(self):
        """
        """
        pass

def _find_device(name):
    """
    """
    found_device = False
    found_device_name = None
    found_device_address = None
    discovery_service = ble.DiscoveryService()
    nearby_devices = discovery_service.discover(2)
    if nearby_devices:
        for address, name in nearby_devices.items():
            if name.startswith(name):
                found_device = True
                found_device_address = address
                found_device_name = name
                break

    if found_device:
        print(f'Found device named: {found_device_name} at {found_device_address}')

    return found_device, found_device_address, found_device_name