#!/usr/bin/env python3
import socket
import struct
import sys

def parse_can_frame(can_id, data):
    """
    Decodes raw hex data based on reverse-engineered J1939/Proprietary IDs.
    Add or modify these conditions as your AI agent maps out the system.
    """
    # Example ID 0x240: 6kW Chiller Telemetry
    if can_id == 0x240:
        # Assuming Byte 0-1 is an unsigned 16-bit int for cooling fluid temperature (Scaled x10)
        # Assuming Byte 2 is an unsigned 8-bit int for Compressor RPM (Scaled x100)
        fluid_temp_raw, compressor_rpm_raw = struct.unpack('>HB', data[0:3])
        fluid_temp = fluid_temp_raw / 10.0
        compressor_rpm = compressor_rpm_raw * 100

        print(f"[CHILLER] Fluid Temp: {fluid_temp}°C | Compressor Speed: {compressor_rpm} RPM")
        return {"type": "chiller", "temp": fluid_temp, "rpm": compressor_rpm}

    # Example ID 0x310: Horizon Master FC Controller Status
    elif can_id == 0x310:
        # Assuming Byte 0-1 is Stack 1 Temperature, Byte 2-3 is Stack 2 Temperature
        stack1_temp, stack2_temp = struct.unpack('>HH', data[0:4])
        # Scale adjustment assuming 0.1°C per bit resolution
        s1_celsius = stack1_temp * 0.1
        s2_celsius = stack2_temp * 0.1

        print(f"[FUEL_CELL] Stack 1 Heat: {s1_celsius}°C | Stack 2 Heat: {s2_celsius}°C")
        return {"type": "fuel_cell", "stack1": s1_celsius, "stack2": s2_celsius}

    return None

def start_socketcan_listener(interface="can0"):
    print(f"[*] Initialising SocketCAN stream on interface: {interface}")

    # 1. Create a raw network socket for CAN communications
    try:
        s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    except OSError as e:
        print(f"[CRITICAL] Kernel SocketCAN layer unavailable: {e}")
        print("Ensure virtual or physical CAN interface is active (e.g., 'sudo ip link set can0 up type can')")
        sys.exit(1)

    # 2. Bind the socket directly to the vehicle's network interface link
    try:
        s.bind((interface,))
    except OSError:
        print(f"[ERROR] Could not bind to interface: {interface}. Check wiring or down state.")
        sys.exit(1)

    # 3. Standard CAN frame structural format specification
    # can_id: 4-byte int, can_dlc: 1-byte char, data: 8 bytes of padding/payload
    can_frame_format = "=IB3x8s"
    frame_size = struct.calcsize(can_frame_format)

    print(f"[✓] Active Network Listener Engaged. Monitoring data traffic...")

    try:
        while True:
            # Block and wait for a single packet arrival over the bus
            raw_frame = s.recv(frame_size)
            can_id, dlc, data = struct.unpack(can_frame_format, raw_frame)

            # Mask out J1939 extended bitflags to isolate the base CAN ID
            clean_id = can_id & socket.CAN_EFF_MASK

            # Slice trailing empty data bytes based on the frame's true payload size
            actual_payload = data[:dlc]

            # Process payload variables
            parse_can_frame(clean_id, actual_payload)

    except KeyboardInterrupt:
        print("\n[*] Halting SocketCAN listener thread. Closing interface socket.")
        s.close()

if __name__ == "__main__":
    # Allows switching to virtual interfaces (vcan0) easily during desktop simulation
    target_interface = sys.argv[1] if len(sys.argv) > 1 else "can0"
    start_socketcan_listener(target_interface)
