#!/bin/bash

# create and activate the virtual environment
if [ ! -d "lite-witness-env" ]; then
    python3 -m venv lite-witness-env
    echo "created virtual environment: lite-witness-env"
fi

source lite-witness-env/bin/activate

# install the latest Python dependencies
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# install the latest available Chromium and Chromium-driver in Kali/Debian-based Linux systems
sudo apt-get update
sudo apt-get install -y chromium chromium-driver

# dynamically install the latest version of ChromeDriver using webdriver-manager
python3 -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"

echo "setup complete, the virtual environment has been created and dependencies are installed."
