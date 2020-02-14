# Phockup

[![Phockup](https://snapcraft.io/phockup/badge.svg)](https://snapcraft.io/phockup)
[![Snap Status](https://build.snapcraft.io/badge/ivandokov/phockup.svg)](https://build.snapcraft.io/user/ivandokov/phockup)
[![Build Status](https://travis-ci.org/ivandokov/phockup.svg?branch=master)](https://travis-ci.org/ivandokov/phockup)

Media sorting tool to organize photos and videos from your camera in folders by year, month and day.

## How it works
The software will collect all files from the input directory and copy them to the output directory without changing the files content. It will only rename the files and place them in the proper directory for year, month and day.

All files which are not images or videos or those which do not have creation date information will be placed in a directory called `unknown` without file name change. By doing this you can be sure that the input directory can be safely deleted after the successful process completion because **all** files from the input directory have a copy in the output directory.

## Installation
### Linux (snap)
Requires [snapd](https://snapcraft.io/docs/core/install)
```
sudo snap install phockup
```
*Note: snap applications can access files only in your **home and `/media` directories** for security reasons. If your media files are not located in these directories you should use the installation method below.  
If your files are in `/media` you should run the following command to allow access:*
```
sudo snap connect phockup:removable-media
```

### Linux (without snap)
If you are using distro which doesn't support [snapd](https://snapcraft.io/docs/core/install) or you don't want to download the snap you can use the following commands to download the source and set it up
```
sudo apt-get install python3 libimage-exiftool-perl -y
curl -L https://github.com/ivandokov/phockup/archive/latest.tar.gz -o phockup.tar.gz
tar -zxf phockup.tar.gz
sudo mv phockup-* /opt/phockup
sudo ln -s /opt/phockup/phockup.py /usr/local/bin/phockup
```

### Mac
Requires [Homebrew](http://brew.sh/)
```
brew tap ivandokov/homebrew-contrib
brew install phockup
```

### Windows
* Download and install latest stable [Python 3](https://www.python.org/downloads/windows/)
* Download Phockup's [latest release](https://github.com/ivandokov/phockup/archive/latest.tar.gz) and extract the archive
* Download exiftool from the official [website](https://exiftool.org/) and extract the archive
* Rename `exiftool(-k).exe` to `exiftool.exe`
* Move `exiftool.exe` to phockup folder
* Open Command Prompt and `cd` to phockup folder
* Use the command below (use `phockup.py` instead of `phockup`)

## Usage
Organize photos from one directory into another
```
phockup INPUTDIR OUTPUTDIR
```

`INPUTDIR` is the directory where your photos are located.
`OUTPUTDIR` is the directory where your **sorted** photos will be stored. It could be a new not existing directory.

Example:
```
phockup ~/Pictures/camera ~/Pictures/sorted
```

### Date format
If you want to change the output directories date format you can do it by passing the format as `-d | --date` argument.
You can choose different year format (e.g. 17 instead of 2017) or decide
        to skip the day directories and have all photos sorted in year/month.

```
Supported formats:
    YYYY - 2016, 2017 ...
    YY   - 16, 17 ...
    MM   - 07, 08, 09 ...
    M    - July, August, September ...
    m    - Jul, Aug, Sept ...
    DD   - 27, 28, 29 ... (day of month)
    DDD  - 123, 158, 365 ... (day of year)

Example:
    YYYY/MM/DD -> 2011/07/17
    YYYY/M/DD  -> 2011/July/17
    YYYY/m/DD  -> 2011/Jul/17
    YY/m-DD    -> 11/Jul-17
```

### Missing date information in EXIF
If any of the photos does not have date information you can use the `-r | --regex` option to specify date format for date extraction from filenames:
```
--regex="(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})[_-]?(?P<hour>\d{2})\.(?P<minute>\d{2})\.(?P<second>\d{2})"
```

As a last resort, specify the `-t` option to use the file modification timestamp. This may not be accurate in all cases but can provide some kind of date if you'd rather it not go into the `unknown` folder. 

### Move files
Instead of copying the process will move all files from the INPUTDIR to the OUTPUTDIR by using the flag `-m | --move`. This is useful when working with a big collection of files and the remaining free space is not enough to make a copy of the INPUTDIR.

### Link files
Instead of copying the process will create hard link all files from the INPUTDIR into new structure in OUTPUTDIR by using the flag `-l | --link`. This is useful when working with good structure of photos in INPUTDIR (like folders per device).

### Original filenames
Organize the files in selected format or using the default year/month/day format but keep original filenames by using the flag `-o | --original-names`.

### Fix incorrect dates
If date extracted from photos is incorrect, you can use the `-f | --date-field` option to set the correct exif field to get date information from. Use this command to list which fields are available for a file:
```
exiftool -time:all -mimetype -j file.jpg
```
The output may look like this, but with more fields:
```
[{
  "DateTimeOriginal": "2017:10:06 01:01:01",
  "CreateDate": "2017:01:01 01:01:01",
]}
```
If the correct date is in `DateTimeOriginal`, you can include the option `--date-field=DateTimeOriginal` to get date information from it.
To set multiple fields to be tried in order until a valid date is found, just join them with spaces in a quoted string like `"CreateDate FileModifyDate"`.

## Development

### Running tests
To run the tests, first install the dev dependencies using

```bash
pip3 install -r requirements-dev.txt
```

Then run the tests using

```bash
pytest
```

## Changelog
##### `1.5.9`
* Fixed [#70](https://github.com/ivandokov/phockup/issues/70) related to Windows issues 
##### `1.5.8` 
* Add `--date-field` option to set date extraction fields  [#54](https://github.com/ivandokov/phockup/issues/54)
* Handle regex with optional hour information  [#62](https://github.com/ivandokov/phockup/issues/62)
* Fix regex support for incomplete time on filename  [#55](https://github.com/ivandokov/phockup/issues/55)
* Fix to handle files with illegal characters [#53](https://github.com/ivandokov/phockup/issues/53)
##### `1.5.7` 
* Resolved [#44](https://github.com/ivandokov/phockup/issues/44)
##### `1.5.6` 
* Add `-o | --original-names` option to allow keeping the original filenames
##### `1.5.5` 
* Add `-t` option to allow using file modification time as a last resort
* Workaround EXIF DateTaken time of all-zeros
##### `1.5.4`
* Handle gracefully files without MIMEType
##### `1.5.3`
* Handle broken symlinks
##### `1.5.2`
* Add `SubSecCreateDate` and `SubSecDateTimeOriginal` EXIF dates to the list of allowed ones because exiftool changed the default behavior to not include the subseconds for `CreateDate` and `DateTimeOriginal`
##### `1.5.1`
* Handle filenames with spaces
##### `1.5.0`
* Major refactoring.
* Updated all tests.
* Added TravisCI.
##### `1.4.1`
* Add `-l | --link` flag to link files instead of copy.
##### `1.4.0`
* Add `-m | --move` flag to move files instead of copy.
##### `1.3.2`
* More snapcraft.yaml fixes (removed architecture which were producing wrong snaps for amd64).
* Catch some possible write permission for directories and expand absolute path and home directory on *nix
##### `1.3.1`
* Fixed issue with the snap application and simplified the snapcraft.yaml
##### `1.3.0`
* Allow different output directories date format with `-d | --date` option.
##### `1.2.2`
* Allow access to removable media (external HDD, USB, etc) for snap the application
* Continue execution even if date attribute is not present [[#6](https://github.com/ivandokov/phockup/pull/6)]
##### `1.2.1`
* Windows compatibility fixes
##### `1.2.0`
* Changed synopsis of the script. `-i|--inputdir` and `-o|--outputdir` are not required anymore. Use first argument for input directory and second for output directory.
* Do not process duplicated files located in different directories.
* Suffix duplicated file names of different files. Sha256 checksum is used for comparison of the source and target files to see if they are identical.
* Ignore `.DS_Store` and `Thumbs.db` files
* Handle case when `exiftool` returns exit code > 0.
* Use `os.walk` instead of `iglob` to support Python < 3.5
* Handle some different date formats from exif data.
##### `1.1.0`
* Collect all files instead only specified file types. This also enables video sorting.
##### `1.0.0`
Initial version.
