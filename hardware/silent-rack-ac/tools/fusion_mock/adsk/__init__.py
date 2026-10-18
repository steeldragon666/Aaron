"""Minimal stand-in for Autodesk Fusion's `adsk` package (test harness only).

Implements just the API surface SilentRackAC.py uses, backed by CadQuery/OCC,
so the script's control flow, cm/mm handling, Y-up transform and volume
cross-check can be exercised outside Fusion.  NOT a Fusion emulator.
"""
from . import core, fusion  # noqa: F401

_events = 0


def doEvents():
    global _events
    _events += 1
