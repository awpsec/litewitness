#!/bin/bash

sudo apt update

sudo apt install -y python3 python3-pip python3-venv

sudo apt install -y firefox-esr

GECKO_VERSION="v0.33.0"
wget https://github.com/mozilla/geckodriver/releases/download/${GECKO_VERSION}/geckodriver-${GECKO_VERSION}-linux64.tar.gz
tar -xvzf geckodriver-${GECKO_VERSION}-linux64.tar.gz
sudo mv geckodriver /usr/local/bin/
rm geckodriver-${GECKO_VERSION}-linux64.tar.gz

python3 -m venv wit-env
source wit-env/bin/activate

pip install -r requirements.txt

echo "Setup completed successfully!"
echo "To activate the virtual environment, run: source wit-env/bin/activate"
