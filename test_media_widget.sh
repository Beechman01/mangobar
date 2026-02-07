#!/bin/bash

echo "=== Media Widget Test Script ==="

# Kill existing bar
echo "1. Killing existing bar..."
pkill -f "python config.py"
sleep 2

# Start bar without Spotify
echo "2. Starting bar without Spotify..."
python config.py > /tmp/media_test.log 2>&1 &
BAR_PID=$!
echo "   Bar PID: $BAR_PID"
sleep 3

# Check if bar is still running
if ps -p $BAR_PID > /dev/null; then
    echo "   ✓ Bar started successfully"
else
    echo "   ✗ Bar crashed on startup"
    cat /tmp/media_test.log | tail -20
    exit 1
fi

# Check for errors
if grep -i "error\|crash\|trace" /tmp/media_test.log > /dev/null; then
    echo "   ⚠ Errors found in startup:"
    grep -i "error\|crash\|trace" /tmp/media_test.log
fi

echo ""
echo "3. Testing with Spotify..."
echo "   Please start Spotify and play something, then press Enter"
read

echo "   Checking if widget should be visible..."
sleep 2

echo ""
echo "4. Testing Spotify close..."
echo "   Please close Spotify completely, then press Enter"
read

echo "   Waiting for cleanup..."
sleep 3

# Check if bar is still running
if ps -p $BAR_PID > /dev/null; then
    echo "   ✓ Bar still running after Spotify close"
else
    echo "   ✗ Bar crashed when Spotify closed"
    cat /tmp/media_test.log | tail -30
    exit 1
fi

# Check for crash errors
if grep -i "trace trap\|segfault\|core dumped" /tmp/media_test.log > /dev/null; then
    echo "   ✗ Crash detected in logs:"
    grep -i "trace trap\|segfault\|core dumped" /tmp/media_test.log
    kill $BAR_PID 2>/dev/null
    exit 1
fi

echo "   ✓ No crash detected"
echo ""
echo "=== All tests passed! ==="

# Cleanup
kill $BAR_PID 2>/dev/null
exit 0
