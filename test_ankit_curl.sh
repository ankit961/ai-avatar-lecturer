#!/bin/bash

echo "🚀 Testing Ankit's Avatar Generation via curl"
echo "=============================================="

# Test 1: Check if server is responding
echo "1. Testing server health..."
curl -X GET "http://localhost:9000/health" | jq .

echo -e "\n2. Getting available lecturers..."
curl -X GET "http://localhost:9000/lecturers" | jq .

echo -e "\n3. Generating video with Ankit Chauhan..."
echo "This may take several minutes..."

# Generate video using form data
curl -X POST "http://localhost:9000/generate/text" \
  -F "text=Hello, my name is Ankit Chauhan. I am successfully testing the AI avatar system with my custom portrait and voice. This technology is working perfectly!" \
  -F "language=en" \
  -F "lecturer_name=Ankit Chauhan" \
  -F "speed=1.0" \
  --max-time 600 \
  | jq .

echo -e "\n✅ Test completed!"
echo "Check the outputs directory for your generated video."
