#!/bin/bash
# Test runner script for Secure Artifact Vault

set -e

echo "=================================================="
echo "Secure Artifact Vault - Test Suite Runner"
echo "=================================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv"
    exit 1
fi

# Activate venv
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Install/update requirements
echo "📦 Installing test dependencies..."
pip install -q pytest pytest-asyncio pytest-cov httpx

echo ""
echo "=================================================="
echo "Running All Tests"
echo "=================================================="
echo ""

# Run all tests with coverage
python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

echo ""
echo "=================================================="
echo "Test Run Complete!"
echo "=================================================="
echo ""
echo "📊 Coverage report generated in: htmlcov/index.html"
echo ""
echo "Common commands:"
echo "  pytest tests/                              # Run all tests"
echo "  pytest tests/test_config.py -v             # Run specific test file"
echo "  pytest tests/test_config.py::TestSettings -v  # Run specific test class"
echo "  pytest tests/ --cov=app --cov-report=html  # Generate HTML coverage report"
echo ""
