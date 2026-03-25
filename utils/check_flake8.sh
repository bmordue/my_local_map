#!/bin/bash
# check_flake8.sh - PEP8 compliance checker using flake8
#
# This script enforces PEP8 compliance for the my_local_map project.
# It runs flake8 with appropriate settings to ensure code quality.
#
# Exit codes:
#   0 - All checks passed
#   1 - Critical errors found (must be fixed)
#   2 - PEP8 violations found (should be fixed)

echo "🔍 Running flake8 for PEP8 compliance..."
echo ""

# First, check for critical errors that MUST be fixed
# These include syntax errors and undefined names
echo "Step 1: Checking for critical errors (syntax, undefined names)..."
if ! flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics; then
    echo ""
    echo "❌ CRITICAL: Syntax errors or undefined names found!"
    echo "These must be fixed before proceeding."
    exit 1
fi
echo "✓ No critical errors found"

# Then run full PEP8 check
# Using max-line-length=88 (Black's default)
# Ignoring E203 (whitespace before ':') and W503 (line break before binary operator)
# as these conflict with Black formatter
echo ""
echo "Step 2: Checking full PEP8 compliance..."
if ! flake8 . --count --show-source --statistics \
    --max-line-length=88 \
    --extend-ignore=E203,W503; then
    echo ""
    echo "⚠️  PEP8 violations found. Please fix them to maintain code quality."
    exit 2
fi

echo ""
echo "✅ All PEP8 checks passed!"
exit 0
