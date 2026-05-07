#!/bin/bash
# Deployment script for Agentic OCR

echo "Setting up deployment..."

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py --server.port=3000 --server.address=0.0.0.0
