#!/usr/bin/env python3
import socket
import struct
import time
import sys
import random

def create_can_frame(can_id, data):
    """
    Packs a standard or extended CAN ID and up to 8 bytes of data
    into the exact structural byte alignment required by the Linux kernel.
    """
    dlc = len(data)
    # Pad payload to exactly 8 bytes as required by standard SocketCAN layout
    padded_data = data.ljust(8, b'\x00')
    # Struct format: = (native alignment), I (4-byte ID), B (1-byte DLC), 3x (3 padding bytes), 8s (8-byte payload)
    return struct.pack("=IB3x8s", can_id, dlc, padded_data)

def run_simulation(interface="vcan0"):
    print(f"[*] Starting Tri-Brid Vehicle Telemetry Simulation on: {interface}")

    # 1. Open raw network socket for CAN traffic transmission
    try:
        s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        s.bind((interface,))
    except OSError as e:
        print(f"[CRITICAL] Failed to bind to interface {interface}: {e}")
        print("To create a virtual loopback: 'sudo ip link add dev vcan0 type vcan && sudo ip link set up vcan0'")
        sys.exit(1)

    print(f"[✓] Injection node online. Simulating vehicle operation...")

    # Initialize variables to simulate moving profiles
    s1_temp = 55.0
    s2_temp = 56.5
    chiller_temp = 24.0
    compressor_rpm = 25000

    try:
        while True:
            # -------------------------------------------------------------
            # Simulation 1: Horizon Master FC Controller Status (ID: 0x310)
            # -------------------------------------------------------------
            # Add random walk fluctuations to simulate real-world thermal drift
            s1_temp += random.uniform(-0.3, 0.4)
            s2_temp += random.uniform(-0.2, 0.5)

            # Boundary caps to simulate system limits
            s1_temp = max(50.0, min(s1_temp, 78.0))
            s2_temp = max(50.0, min(s2_temp, 78.0))

            # Convert engineering units back to raw hex integers (Scale: Value * 10)
            raw_s1 = int(s1_temp * 10)
            raw_s2 = int(s2_temp * 10)

            # Pack into two 16-bit unsigned big-endian integers (4 bytes total used)
            fc_data = struct.pack(">HH", raw_s1, raw_s2)
            frame_fc = create_can_frame(0x310, fc_data)
            s.send(frame_fc)

            # -------------------------------------------------------------
            # Simulation 2: 6kW Chiller Telemetry Output (ID: 0x240)
            # -------------------------------------------------------------
            # Simulate chiller reacting to fuel cell heat load
            if s1_temp > 65.0:
                chiller_temp -= random.uniform(0.1, 0.3)
                compressor_rpm = min(85000, compressor_rpm + 1500)
            else:
                chiller_temp += random.uniform(-0.1, 0.2)
                compressor_rpm = max(12000, compressor_rpm - 800)

            chiller_temp = max(15.0, min(chiller_temp, 35.0))

            raw_chiller_temp = int(chiller_temp * 10)
            raw_rpm = int(compressor_rpm / 100) # Compressed scale factor

            # Pack into one 16-bit int and one 8-bit int (3 bytes total used)
            chiller_data = struct.pack(">HB", raw_chiller_temp, raw_rpm)
            frame_chiller = create_can_frame(0x240, chiller_data)
            s.send(frame_chiller)

            # Print monitor updates to console screen
            print(f"[TX] Injected 0x310 (FC Stacks: {s1_temp:.1f}°C / {s2_temp:.1f}°C) | 0x240 (Chiller: {chiller_temp:.1f}°C / {compressor_rpm} RPM)")

            # Broadcast interval pacing (simulate a 500ms transmission update rate)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[*] Stopping injection stream. Closing loopback socket connection.")
        s.close()

if __name__ == "__main__":
    target_interface = sys.argv[1] if len(sys.argv) > 1 else "vcan0"
    run_simulation(target_interface)
