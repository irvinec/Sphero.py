"""
"""

import bluetooth # pybluez

class BluetoothInterface(object):
    """
    """

    def __init__(self, target_name='Sphero', target_address=None, port=1):
        self._target_name = target_name
        self._port = port
        self._target_address = target_address
        self._sock = None

    def __del__(self):
        self.close()

    def connect(self, num_retry_attempts=1):
        """
        """
        for num_tries in range(num_retry_attempts):
            if self._target_address is None:
                _, self._target_address, _ = _find_device(self._target_name)

            if self._target_address is not None:
                self._sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self._sock.connect((self._target_address, self._port))
                break
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
        self._sock.send(data)


    def recv(self, num_bytes):
        """
        """
        return self._sock.recv(num_bytes)


    def close(self):
        """
        """
        if self._sock is not None:
            self._sock.close()

def _find_device(name):
    """
    """
    found_device = False
    found_device_name = None
    found_device_address = None
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    if nearby_devices:
        for address, name in nearby_devices:
            if name.startswith(name):
                found_device = True
                found_device_address = address
                found_device_name = name
                break

    if found_device:
        print(f'Found device named: {found_device_name} at {found_device_address}')

    return found_device, found_device_address, found_device_name
