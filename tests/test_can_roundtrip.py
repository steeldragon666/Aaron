#!/usr/bin/env python3
"""
Offline round-trip test for the CAN simulation suite.

A live SocketCAN/vcan0 interface needs a kernel vcan module and `ip` tooling,
which aren't present in every CI runner. Rather than skip coverage, this test
exercises the *exact* packing code from can_injector.create_can_frame and the
*exact* parsing code from can_listener.parse_can_frame, plus the frame
unpacking the listener performs on the wire. If a developer changes a scale
factor, byte order, or struct layout on one side and not the other, this fails.
"""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "network"))

import can_injector
import can_listener

# This mirrors can_listener.start_socketcan_listener's wire format.
CAN_FRAME_FORMAT = "=IB3x8s"
CAN_EFF_MASK = 0x1FFFFFFF


def wire_decode(frame_bytes):
    """Replicates the listener's recv() -> unpack -> mask -> slice pipeline."""
    can_id, dlc, data = struct.unpack(CAN_FRAME_FORMAT, frame_bytes)
    clean_id = can_id & CAN_EFF_MASK
    return clean_id, can_listener.parse_can_frame(clean_id, data[:dlc])


class TestFrameRoundTrip(unittest.TestCase):
    def test_frame_is_kernel_sized(self):
        frame = can_injector.create_can_frame(0x310, struct.pack(">HH", 0, 0))
        # SocketCAN struct can_frame is 16 bytes: 4 (id) + 1 (dlc) + 3 (pad) + 8 (data)
        self.assertEqual(len(frame), 16)
        self.assertEqual(len(frame), struct.calcsize(CAN_FRAME_FORMAT))

    def test_fuel_cell_roundtrip(self):
        s1, s2 = 64.0, 71.5  # degrees C
        fc_data = struct.pack(">HH", int(s1 * 10), int(s2 * 10))
        frame = can_injector.create_can_frame(0x310, fc_data)

        clean_id, decoded = wire_decode(frame)
        self.assertEqual(clean_id, 0x310)
        self.assertEqual(decoded["type"], "fuel_cell")
        self.assertAlmostEqual(decoded["stack1"], s1, places=4)
        self.assertAlmostEqual(decoded["stack2"], s2, places=4)

    def test_chiller_roundtrip(self):
        temp, rpm = 23.4, 25000  # degC, RPM
        chiller_data = struct.pack(">HB", int(temp * 10), int(rpm / 100))
        frame = can_injector.create_can_frame(0x240, chiller_data)

        clean_id, decoded = wire_decode(frame)
        self.assertEqual(clean_id, 0x240)
        self.assertEqual(decoded["type"], "chiller")
        self.assertAlmostEqual(decoded["temp"], temp, places=4)
        # RPM is quantised to the nearest 100 by the x100 scale factor.
        self.assertEqual(decoded["rpm"], 25000)

    def test_unknown_id_returns_none(self):
        frame = can_injector.create_can_frame(0x123, struct.pack(">HH", 1, 2))
        _, decoded = wire_decode(frame)
        self.assertIsNone(decoded)

    def test_dlc_matches_payload(self):
        # Chiller payload is 3 bytes; fuel cell is 4. The DLC byte the listener
        # uses to slice the payload must reflect that.
        chiller = can_injector.create_can_frame(0x240, struct.pack(">HB", 234, 250))
        fc = can_injector.create_can_frame(0x310, struct.pack(">HH", 640, 715))
        self.assertEqual(chiller[4], 3)
        self.assertEqual(fc[4], 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
