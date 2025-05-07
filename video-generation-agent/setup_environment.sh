#!/bin/bash

echo "[+] Installing Python 3.10.13 using pyenv..."
pyenv install 3.10.13
pyenv virtualenv 3.10.13 video_env_310
pyenv activate video_env_310

echo "[+] Upgrading pip and core tools..."
pip install --upgrade pip setuptools wheel

echo "[+] Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "[+] Downloading spaCy language models..."
python -m spacy download en_core_web_sm
python -m spacy download ko_core_news_sm

echo "[✔] Environment setup complete!"