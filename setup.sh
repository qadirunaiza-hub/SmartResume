#!/usr/bin/env bash
set -e

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python -m spacy download en_core_web_sm

cp .env.example .env
echo "Setup complete. Edit .env and add your ANTHROPIC_API_KEY."
echo "Run: streamlit run app.py"
