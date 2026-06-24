#!/usr/bin/env python3
import sys
import re

def validate_dbc_file(file_path):
    print(f"[*] Commencing automated verification on: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"[CRITICAL] Targeted DBC file not found at path: {file_path}")
        return False
    except Exception as e:
        print(f"[CRITICAL] Failed to read file: {e}")
        return False

    errors = 0
    warnings = 0
    message_count = 0
    signal_count = 0

    # Regex patterns for tracking standard J1939/CAN DBC architecture
    bo_pattern = re.compile(r'^BO_\s+(\d+)\s+(\w+)\s*:\s*(\d+)\s+(\w+)')
    sg_pattern = re.compile(r'^\s*SG_\s+(\w+)\s*(?:[\w\s]*)\s*:\s*(\d+)\|(\d+)@(\d+)([\+-])\s+\(([\d\.-]+),([\d\.-]+)\)\s+\[([\d\.-]+)\|([\d\.-]+)\]\s+"([^"]*)"\s+(\w+)')

    current_msg_id = None
    current_msg_name = None
    current_msg_dlc = 0
    allocated_bits = {}

    for line_num, raw_line in enumerate(lines, 1):
        line = raw_line.strip()

        # Skip empty lines or standard comments
        if not line or line.startswith('CM_') or line.startswith('VAL_'):
            continue

        # 1. Validate Message Definitions (BO_)
        if line.startswith('BO_'):
            match = bo_pattern.match(line)
            if not match:
                print(f"[ERROR] Line {line_num}: Malformed Message Definition (BO_).")
                errors += 1
                continue

            can_id = int(match.group(1))
            msg_name = match.group(2)
            dlc = int(match.group(3))

            message_count += 1
            current_msg_id = can_id
            current_msg_name = msg_name
            current_msg_dlc = dlc
            allocated_bits[can_id] = set() # Reset bit tracker for this message scope

            # Check for invalid CAN IDs (Extended identifiers capped at 29-bit)
            if can_id > 536870911:
                print(f"[ERROR] Line {line_num}: CAN ID {can_id} for '{msg_name}' exceeds maximum 29-bit limit.")
                errors += 1
            elif dlc > 64: # Accommodate both standard CAN (8) and CAN-FD (64) boundaries
                print(f"[ERROR] Line {line_num}: Data Length Code (DLC) of {dlc} is structurally invalid.")
                errors += 1

        # 2. Validate Signal Definitions (SG_)
        elif line.startswith('SG_'):
            if current_msg_id is None:
                print(f"[ERROR] Line {line_num}: Orphaned Signal definition found outside a valid Message scope.")
                errors += 1
                continue

            match = sg_pattern.match(raw_line) # Use raw_line to preserve whitespace layout
            if not match:
                print(f"[ERROR] Line {line_num}: Malformed Signal Definition (SG_). Check scaling brackets or separators.")
                errors += 1
                continue

            sig_name = match.group(1)
            start_bit = int(match.group(2))
            bit_length = int(match.group(3))
            endianness = int(match.group(4)) # 0 = Big Endian (Motorola), 1 = Little Endian (Intel)

            signal_count += 1

            # Total payload bounding check based on Message DLC
            max_payload_bits = current_msg_dlc * 8
            if start_bit + bit_length > max_payload_bits and endianness == 1:
                print(f"[ERROR] Line {line_num}: Signal '{sig_name}' slips past Message boundaries (DLC={current_msg_dlc} bytes).")
                errors += 1

            # 3. Overlapping Bit Analysis (Critical for reverse engineering errors)
            signal_bits = set(range(start_bit, start_bit + bit_length))
            overlap = signal_bits.intersection(allocated_bits[current_msg_id])
            if overlap:
                print(f"[CRITICAL OVERLAP] Line {line_num}: Signal '{sig_name}' attempts to map to bits already claimed in message '{current_msg_name}' (ID: {current_msg_id}). Overlapping bit indices: {list(overlap)}")
                errors += 1
            else:
                allocated_bits[current_msg_id].update(signal_bits)

    # Final summary reports back to the GitHub Actions workflow engine
    print(f"\n================ Verification Summary ================")
    print(f"[✓] Parsed {message_count} messages containing {signal_count} unique signals.")
    print(f"[!] Compilation anomalies found: {errors} Errors, {warnings} Warnings.")

    if errors > 0:
        print("[FAIL] DBC structure contains structural defects. Blocking deployment to vehicle.")
        return False
    else:
        print("[SUCCESS] DBC dictionary file conforms to network validation parameters.")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_dbc.py <path_to_dbc_file>")
        sys.exit(1)

    target_file = sys.argv[1]
    success = validate_dbc_file(target_file)

    # Return exit code 0 on success, or 1 on failure to signal the GitHub runner
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
