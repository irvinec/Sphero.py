"""Sphero

Interact with Sphero devices.
"""

import threading

import sphero.packets
import sphero.commands

__all__ = ['Sphero', 'CommandTimedOutError']

class CommandTimedOutError(Exception):
    """Exception thrown when a command times out."""

    def __init__(self):
        Exception.__init__(self)

class Sphero(object):
    """The main Sphero class that is used for interacting with a Sphero device.
    """

    def __init__(self, bluetooth_interface, default_response_timeout_in_seconds=0.5):
        self._bluetooth_interface = bluetooth_interface
        self._default_response_timeout_in_seconds = default_response_timeout_in_seconds
        self._command_sequence_number = 0x00
        self._commands_waiting_for_response = {}

        # setup thread for receiving responses
        self._class_destroy_event = threading.Event()
        self._receive_thread = threading.Thread(target=self._receive_thread_run)
        self._receive_thread.daemon = True
        self._receive_thread.start()

        # declare private event listeners
        self._on_ping_response = None


    def __del__(self):
        self._class_destroy_event.set()


    async def ping(
            self,
            wait_for_response=True,
            reset_inactivity_timeout=True,
            response_timeout_in_seconds=None):
        """Sends ping command to the Sphero

        The Ping command is used to verify both a solid data link with the client
        and that Sphero is awake and dispatching commands.

        Args:
            wait_for_response (bool, True):
                If True, will wait for a response from the Sphero
            reset_inactivity_timeout (bool, True):
                If True, will reset the inactivity timer on the Sphero.
            response_timeout_in_seconds (float, None):
                The amount of time to wait for a response.
                If not specified or None, uses the default timeout
                passed in the constructor of this Sphero object.
        """

        sequence_number = self._get_and_increment_command_sequence_number()
        ping_command = sphero.commands.create_ping_command(
            sequence_number,
            wait_for_response,
            reset_inactivity_timeout)

        # Ping has no data so don't in response,
        # so no need tp return anything.
        await self._send_command(
            ping_command,
            sequence_number=sequence_number,
            wait_for_response=wait_for_response,
            response_timeout_in_seconds=response_timeout_in_seconds)


    async def set_rgb_led(
            self,
            red=0,
            green=0,
            blue=0,
            save_as_user_led_color=False,
            wait_for_response=True,
            reset_inactivity_timeout=True,
            response_timeout_in_seconds=None):
        """Sets the main LED RGB color of the Sphero.

        The composite value is stored as the "application LED color"
        and immediately driven to the LED
        (if not overridden by a macro or orbBasic operation).
        If save_as_user_led_color is True, the value is also saved
        as the "user LED color" which persists across power cycles
        and is rendered in the gap between an application connecting
        and sending this command.

        Args:
            red (int):
                The red channel value.
                Valid range is [0, 255].
            green (int):
                The green channel value.
                Valid range is [0, 255].
            blue (int):
                The blue channel value.
                Valid range is [0, 255].
            save_as_user_led_color (bool, False):
                If True, the color will be saved as the user color
                and will persist across power cycles.
            wait_for_response (bool, True):
                If True, will wait for a response from the Sphero
            reset_inactivity_timeout (bool, True):
                If True, will reset the inactivity timer on the Sphero.
            response_timeout_in_seconds (float, None):
                The amount of time to wait for a response.
                If not specified or None, uses the default timeout
                passed in the constructor of this Sphero object.
        """

        sequence_number = self._get_and_increment_command_sequence_number()
        set_rgb_led_command = sphero.commands.create_set_rgb_led_command(
            red,
            green,
            blue,
            save_as_user_led_color,
            sequence_number,
            wait_for_response,
            reset_inactivity_timeout)

        await self._send_command(
            set_rgb_led_command,
            sequence_number=sequence_number,
            wait_for_response=wait_for_response,
            response_timeout_in_seconds=response_timeout_in_seconds)


    async def get_rgb_led(
            self,
            reset_inactivity_timeout=True,
            response_timeout_in_seconds=None):
        """Retrieves the user LED color in RGB.

        The user LED color is the color that persisists across reboots.
        This may or may not be the active RGB LED color.
        The user LED color is set by calling set_rgb_led
        with save_as_user_led_color=True.

        Returns:
            The user LED color as a list in the form
            [red, green, blue].
        """

        sequence_number = self._get_and_increment_command_sequence_number()
        get_rgb_led_command = sphero.commands.create_get_rgb_led_command(
            sequence_number,
            wait_for_response=True, # must wait for the response to get the result.
            reset_inactivity_timeout=reset_inactivity_timeout)

        response_packet = await self._send_command(
            get_rgb_led_command,
            sequence_number=sequence_number,
            wait_for_response=True,
            response_timeout_in_seconds=response_timeout_in_seconds)

        return response_packet.get_data()


    async def roll(
            self,
            speed,
            heading_in_degrees,
            wait_for_response=True,
            reset_inactivity_timeout=True,
            response_timeout_in_seconds=None):
        """Sends the roll command to the Sphero with given heading and speed.

        This commands Sphero to roll along the provided vector
        determined by heading_in_degrees and speed.
        The heading is relative to the last calibrated direction.

        The heading follows the 360 degrees on a circle, relative to the Sphero:
            * 0 is straight ahead.
            * 90 is to the right.
            * 180 is back.
            * 270 is to the left.

        Args:
            speed (int):
                The relative speed with which to roll the Sphero.
                The valid range is [0, 255].
            heading_in_degrees (int):
                The relative heading in degrees.
                The valid range is [0, 359]
            wait_for_response (bool, True):
                If True, will wait for a response from the Sphero
            reset_inactivity_timeout (bool, True):
            If True, will reset the inactivity timer on the Sphero.
            response_timeout_in_seconds (float, None):
                The amount of time to wait for a response.
                If not specified or None, uses the default timeout
                passed in the constructor of this Sphero object.
        """

        sequence_number = self._get_and_increment_command_sequence_number()
        roll_command = sphero.commands.create_roll_command(
            speed,
            heading_in_degrees,
            sequence_number=sequence_number,
            wait_for_response=wait_for_response,
            reset_inactivity_timeout=reset_inactivity_timeout)

        await self._send_command(
            roll_command,
            sequence_number=sequence_number,
            wait_for_response=wait_for_response,
            response_timeout_in_seconds=response_timeout_in_seconds)


    async def _send_command(
            self,
            command,
            sequence_number,
            wait_for_response=True,
            response_timeout_in_seconds=None):
        """
        """

        response_event = threading.Event()
        response_packet = None
        if wait_for_response:
            # define a generic response handler
            # TODO: might need the ability to pass a custom handler
            def handle_response(received_response_packet):
                nonlocal response_packet
                response_packet = received_response_packet
                nonlocal response_event
                response_event.set()

            # Register the response handler for this commands sequence number
            if sequence_number in self._commands_waiting_for_response:
                raise RuntimeError(
                    "A response handler was already registered for the sequence number {}"
                    .format(sequence_number)
                )
            self._commands_waiting_for_response[sequence_number] = handle_response

        self._bluetooth_interface.send(command.get_bytes())

        # Wait for the response if necessary
        if wait_for_response:
            if response_timeout_in_seconds is None:
                response_timeout_in_seconds = self._default_response_timeout_in_seconds

            timed_out = not response_event.wait(response_timeout_in_seconds)
            del self._commands_waiting_for_response[sequence_number]
            response_event.clear()
            if timed_out:
                raise CommandTimedOutError()

        return response_packet


    def _receive_thread_run(self):
        receive_buffer = []
        while not self._class_destroy_event.is_set():
            receive_buffer.extend(self._bluetooth_interface.recv(1024))
            response_packet = None
            while len(receive_buffer) >= sphero.packets.MIN_PACKET_LENGTH:
                try:
                    response_packet = sphero.packets.SpheroResponsePacket(receive_buffer)
                    # we have a valid response to handle
                    # break out of the inner while loop to handle
                    # the response
                    break
                except sphero.packets.BufferNotLongEnoughError:
                    # break out of inner loop so we can fetch more data
                    break
                except sphero.packets.PacketParseError:
                    # this is an error in the packet format
                    # remove one byte from the buffer and try again
                    receive_buffer.pop(0)
                    continue

            # TODO: need to refactor this loop
            # to not have so many breaks and continues.
            if response_packet is None:
                continue

            if response_packet.is_async():
                pass # TODO: implement logic from here down
            else:
                # for ACK/sync responses we only need to call the registered callback.
                sequence_number = response_packet.get_sequence_number()
                if sequence_number in self._commands_waiting_for_response:
                    self._commands_waiting_for_response[sequence_number](response_packet)
                    # NOTE: it is up to the callback/waiting function to remove the handler.
            # remove the packet we just handled
            del receive_buffer[:response_packet.get_packet_length()]

    def _get_and_increment_command_sequence_number(self):
        result = self._command_sequence_number
        self._command_sequence_number += 1

        # Check if we have overflowed our sequence number byte.
        # If we have, start the sequence back at 0.
        if self._command_sequence_number > 0xFF:
            self._command_sequence_number = 0x00

        return result
