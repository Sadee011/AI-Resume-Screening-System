#!/bin/bash
echo "🚀 Starting AI Resume Screener Backend..."
cd "$(dirname "$0")"
pip install fastapi uvicorn scikit-learn numpy pandas pydantic python-multipart -q
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
