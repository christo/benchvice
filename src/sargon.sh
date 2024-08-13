#!/usr/bin/env bash

# starts the sargon python script with PYTHONPATH setup for deps in submodule

SRC_DIR=$(dirname "$0")
PYTHONPATH=.:pyvicemon:$PYTHONPATH "$SRC_DIR/sargon.py"