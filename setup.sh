#!/bin/bash

# Step 1: Create and activate the virtual environment
if [ ! -d "lite-witness-env" ]; then
    python3 -m venv lite-witness-env
    echo "Created virtual environment: lite-witness-env"
fi

source lite-witness-env/bin/activate

# Step 2: Install the latest Python dependencies
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# Step 3: Install the latest available Chromium and Chromium-driver in Kali/Debian-based Linux systems
sudo apt-get update
sudo apt-get install -y chromium chromium-driver

# Step 4: Dynamically install the latest version of ChromeDriver using webdriver-manager
python3 -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"

echo "Setup complete. Latest versions of Chromium and ChromeDriver are installed."
