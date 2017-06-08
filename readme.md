# Phockup
Media sorting tool to organize photos and videos from your camera in folders by year, month and day.

## How it works
The software will collect all files from the input directory and copy them to the output directory without changing the files content. It will only rename the files and place them in the proper directory for year, month and day. 

All files which are not images or videos or those which do not have creation date information will be placed in a directory called `unknown` without file name change. By doing this you can be sure that the input directory can be safely deleted after the successful process completion because **all** files from the input directory have a copy in the output directory.

## Installation
### Ubuntu
```
sudo apt-get install libimage-exiftool-perl -y
curl -L https://github.com/ivandokov/phockup/archive/v1.2.0.tar.gz -o phockup.tar.gz
tar -zxf phockup.tar.gz
mv phockup-1.2.0 /opt
sudo ln -s /opt/phockup-1.2.0/phockup.py /usr/local/bin/phockup
```
    
### Mac
Requires [Homebrew](http://brew.sh/)
```
brew tap ivandokov/homebrew-contrib
brew install phockup
```

### Windows
* Download exiftool from the official [website](http://www.sno.phy.queensu.ca/~phil/exiftool/)
* Download this package and run `phockup.py` from Command Prompt

## Usage
Organize photos from one directory into another
```
phockup ~/Pictures/camera ~/Pictures/organized
```

## Changelog
##### `v1.2.0` 
* Changed synopsis of the script. `-i|--inputdir` and `-o|--outputdir` are not required anymore. Use first argument for input directory and second for output directory.
* Do not process duplicated files located in different directories.
* Suffix duplicated file names of different files. Sha256 checksum is used for comparison of the source and target files to see if they are identical.
* Ignore `.DS_Store` and `Thumbs.db` files
* Handle case when `exiftool` returns exit code > 0. 
* Use `os.walk` instead of `iglob` to support Python < 3.5
* Handle some different date formats from exif data.
##### `v1.1.0`
* Collect all files instead only specified file types. This also enables video sorting.
##### `v1.0.0`
Initial version.