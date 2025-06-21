#!/bin/bash
echo "Formatting code with Black..."
black ./src/ *.py

echo "Running pylint..."
pylint ./src/ *.py