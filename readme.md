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
Requires [Homebrew](http://brew.sh/)
```
brew tap ivandokov/homebrew-contrib
brew install phockup
```

### Windows
* Download exiftool from the official [website](http://www.sno.phy.queensu.ca/~phil/exiftool/)
* Download this package and run phockup.py from Command Prompt

## Usage
Organize photos from one directory into another
```
phockup ~/Pictures/camera ~/Pictures/organized
```

## Changelog
##### `v1.2.0` 
* Changed synopsis of the script. `-i|--inputdir` and `-o|--outputdir` are not required anymore. Use first argument for input directory and second for output directory.
* Do not process duplicated files located in different directories.
* Prefix duplicated target file names of different files. Sha256 checksum is used for comparison of the source and target files.
* Ignore `.DS_Store` and `Thumbs.db` files
* Handle case when `exiftool` returns exit code > 0. 
* Use `os.walk` instead of `iglob` to support Python < 3.5
* Handle some different date formats from exif data.
##### `v1.1.0`
* Collect all files instead only specified file types. This also enables video sorting.
##### `v1.0.0`
Initial version.