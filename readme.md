# phockup

Photos backup tool to organize photos from camera in folders by year, month and day

## Install (Ubuntu)
By default I install the software in `/opt`. You can change the commands below if you use different folder
```
sudo apt-get install libimage-exiftool-perl
git clone https://github.com/ivandokov/phockup.git /opt/phockup
sudo ln -s /opt/phockup/phockup.py /usr/local/bin/phockup
```
## Usage

Organize photos from one directory into another

```
phockup -i ~/Pictures/camera -o ~/Pictures/organized
```