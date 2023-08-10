#!/bin/bash

# Install dependencies
./install_tool_dependencies.sh

# Start the app
exec uvicorn main:app --host 0.0.0.0 --port 8001 --reload
