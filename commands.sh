#!/bin/sh
cwd=$(pwd)
#sudo apt-get install build-essential
cd ~
mkdir tmp
cd tmp
if [ -d "/usr/bin/zlib" ] 
then
    printf "zlib already installed.\n...Continuing" 
else
    printf "Error: Directory /usr/bin/zlib does not exist.\n...Installing zlib."
    wget http://www.zlib.net/zlib-1.2.11.tar.gz > /dev/null
    tar -xvzf zlib-1.2.11.tar.gz > /dev/null
    cd zlib-1.2.11
    ./configure --prefix=$HOME/opt/zlib > /dev/null
    make install > /dev/null
    export PATH="$HOME/opt:$PATH"
fi
cd ~/tmp
printf "Installing Python 3.8.5"
wget https://www.python.org/ftp/python/3.8.5/Python-3.8.5.tgz > /dev/null
tar zxvf Python-3.8.5.tgz > /dev/null
cd Python-3.8.5 
./configure --prefix=$HOME/opt/python-3.8.5 > /dev/null
make > /dev/null
make install > /dev/null
python3 -m pip install --upgrade pip > /dev/null
pip install virtualenv > /dev/null
pip install --upgrade setuptools > /dev/null
cd $cwd
rm -r ~/tmp
. ~/.bash_profile
printf "Generating Python Zooniverse virtual environment."
virtualenv -p /home/$USER/opt/python-3.8.5/bin/python3 zoonienv
printf "Activating Python Zooniverse virtual environment."
source zoonienv/bin/activate
printf "Installing required Python libraries."
pip install -r requirements.txt > /dev/null
python3 --version
