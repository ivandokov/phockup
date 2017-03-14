# Phockup
Media sorting and backup tool to organize photos and videos from your camera in folders by year, month and day.

## How it works
The software will collect all files from the input directory and transfer them to the output directory without changing the files content. It will only rename the files and place them in the proper directory for the year, month and day. 

All files which are not images or videos will be placed in a directory called `unknown` without file name changes. By doing this you can be sure that the input directory can be safely deleted after the successful process completion because **all** files from the input directory are now located in the output directory.

## Installation
### Ubuntu
```
sudo apt-get install libimage-exiftool-perl
wget -q https://raw.githubusercontent.com/ivandokov/phockup/master/phockup.py
chmod +x phockup.py
sudo mv phockup.py /usr/local/bin/phockup
```
### Mac
Requires [homebrew](http://brew.sh/) or download package from the official [website](http://www.sno.phy.queensu.ca/~phil/exiftool/)
```
brew install exiftool
wget -q https://raw.githubusercontent.com/ivandokov/phockup/master/phockup.py
chmod +x phockup.py
sudo mv phockup.py /usr/local/bin/phockup
```

### Windows
* Download exiftool from the official [website](http://www.sno.phy.queensu.ca/~phil/exiftool/)
* Download this package and run phockup.py from Command Prompt

## Usage
Organize photos from one directory into another
```
phockup -i ~/Pictures/camera -o ~/Pictures/organized
```

## Changelog
* **v1.1.0** - Collect all files instead only specified file types. This also enables video sorting
* **v1.0.0** - Initial version