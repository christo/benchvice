#!/usr/bin/env bash

# starts the sargon python script with PYTHONPATH setup for deps in submodule

PYTHONPATH=.:pyvicemon:$PYTHONPATH src/sargon.py