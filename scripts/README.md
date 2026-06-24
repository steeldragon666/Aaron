# CAN Bus Tooling & Desktop Simulation Suite

Tooling for the tri-brid (hydrogen fuel cell + chiller) UGV telemetry work.
All scripts use the native Linux SocketCAN interface and standard Python — no
locked binary libraries — so an agentic layer can read their stdout or pipe it
into InfluxDB/Redis.

## Contents

| Path | Purpose |
|------|---------|
| `scripts/validate_dbc.py` | CI gate. Validates a `.dbc` data dictionary for malformed `BO_`/`SG_` lines, out-of-bounds 29-bit CAN IDs, invalid DLC, signals that slip past message boundaries, and overlapping bit allocations. Exit 0 = clean, exit 1 = blocking defect. |
| `network/can_listener.py` | Real-time ingestion node. Binds a raw `AF_CAN` socket and decodes known frames (0x240 chiller, 0x310 fuel-cell stacks) into engineering units. |
| `network/can_injector.py` | Desktop simulator. Injects mock chiller/fuel-cell telemetry with a thermal random-walk onto a virtual CAN interface for offline testing. |
| `tests/` | Fixtures + automated tests (see below). |

## Running the validator

```bash
python3 scripts/validate_dbc.py network/chiller_fan_matrix.dbc
```

## Desktop integration test (requires a CAN interface)

A live run needs the kernel `vcan` module and `iproute2`, so it must be run on
a host/VM that allows loading kernel modules (not a restricted container):

```bash
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# Terminal 1 — receiver
python3 network/can_listener.py vcan0
# Terminal 2 — simulator
python3 network/can_injector.py vcan0
```

## Automated tests (no CAN interface needed)

```bash
# DBC validator across known-good and known-bad fixtures
for f in valid overlap badid boundary malformed orphan; do
  python3 scripts/validate_dbc.py tests/fixtures/$f.dbc
done

# Injector <-> listener encode/decode round-trip
python3 tests/test_can_roundtrip.py
```

`test_can_roundtrip.py` calls the real `create_can_frame` (injector) and
`parse_can_frame` (listener) functions plus the listener's wire-unpack
pipeline, so a mismatched scale factor, byte order, or struct layout between
the two scripts will fail the build even without a live `vcan0`.
