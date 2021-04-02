#!/bin/sh
python3 -m pip install --upgrade pip 
pip install virtualenv 
pip install --upgrade setuptools 
#printf "Generating Python Zooniverse virtual environment."
#virtualenv -p /content/drive/MyDrive/researchAssistant/zooniverseTutorial/zooniversePackage/python-3.8.5/bin/python3 /content/drive/MyDrive/researchAssistant/zooniverseTutorial/zooniversePackage/zoonienv
#printf "Activating Python Zooniverse virtual environment."
source /content/drive/MyDrive/researchAssistant/zooniverseTutorial/zooniversePackage/zoonienv/bin/activate
printf "Installing required Python libraries."
pip install -r requirements.txt
python3 --version
