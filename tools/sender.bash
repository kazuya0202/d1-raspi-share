#!/bin/bash
if [ "$1" == "manual" ]; then
    python3 sender/send_manual_seq.py
else
    python3 sender/send_signal.py
fi
