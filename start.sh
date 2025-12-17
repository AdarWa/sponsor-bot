#!/bin/bash

# Start FastAPI server in the backend directory
echo "Starting FastAPI server..."
uvicorn backend.app.main:app --reload &
FASTAPI_PID=$!

# Start Vue development server in the frontend directory
echo "Starting Vue development server..."
cd frontend || exit
npm run dev &
VUE_PID=$!

# Trap to kill both processes on script exit
trap "kill $FASTAPI_PID $VUE_PID" EXIT

echo "Both servers are running. Press Ctrl+C to stop."
wait