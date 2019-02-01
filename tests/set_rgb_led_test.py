"""
"""
import unittest
import asyncio
import time
import spheropy

class SetRgbLedTest(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._setUp())

    async def _setUp(self):
        is_connected = False
        self.sphero = spheropy.Sphero()
        try:
            await self.sphero.connect(num_retry_attempts=3)
            is_connected = True
        except Exception:
            pass

        if not is_connected:
            try:
                await self.sphero.connect(num_retry_attempts=3, use_ble=True)
                is_connected = True
            except Exception:
                pass

        if not is_connected:
            raise RuntimeError('Could not connect to Sphero.')

    def tearDown(self):
        self.sphero.disconnect()
        self.loop.close()

    def test_set_rgb_led(self):
        self.loop.run_until_complete(self.sphero.set_rgb_led(red=0xFF))
        time.sleep(2)
        self.loop.run_until_complete(self.sphero.set_rgb_led(green=0xFF))
        time.sleep(2)
        self.loop.run_until_complete(self.sphero.set_rgb_led(blue=0xFF))
        time.sleep(2)
        self.loop.run_until_complete(self.sphero.set_rgb_led(red=0xFF, blue=0xFF))
        time.sleep(2)
        self.loop.run_until_complete(self.sphero.set_rgb_led(0xFF, 0xFF, 0xFF))
        time.sleep(2)

if __name__ == "__main__":
    unittest.main()