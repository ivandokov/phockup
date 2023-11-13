# Phockup

[![Tests](https://github.com/ivandokov/phockup/actions/workflows/tests.yml/badge.svg)](https://github.com/ivandokov/phockup/actions/workflows/tests.yml)
[![Deploy](https://github.com/ivandokov/phockup/actions/workflows/deploy.yml/badge.svg)](https://github.com/ivandokov/phockup/actions/workflows/deploy.yml)
[![Lint](https://github.com/ivandokov/phockup/actions/workflows/lint.yml/badge.svg)](https://github.com/ivandokov/phockup/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](license)

Media sorting tool to organize photos and videos from your camera in folders by year, month and day.

## How it works
The software will collect all files from the input directory and copy them to the output directory without changing the files content. It will only rename the files and place them in the proper directory for year, month and day.

All files which are not images or videos or those which do not have creation date information will be placed in a directory called `unknown` without file name change. By doing this you can be sure that the input directory can be safely deleted after the successful process completion because **all** files from the input directory have a copy in the output directory.

If the target file already exists, its checksum is compared with the source to determine if it is a duplicate. If the checksums are different, we do not have a duplicate and the target filename will be suffixed with a number, for example "-1". If the checksums match, the copy operation will be skipped.

## Installation

### Docker

The docker container supports two operation modes. The first allows for a single execution of phockup. In this mode, the container will be stopped after the execution is complete. The second mode allows for execution in intervals. In this mode, the container will continue running until the user decides to stop it.

#### Single execution mode
In this mode, all phockup parameters need to be passed as direct parameters within the docker run command. As you define a complete set of phockup parameters for this execution mode, this includes the paths to the input and output folders within the container.
To execute phockup only once, use the following command:

```
docker run -v ~/Pictures:/mnt ivandokov/phockup:latest /mnt/input /mnt/output [PHOCKUP ARGUMENTS]
```

#### Continuous execution mode
In this mode, all relevant settings are defined through environment variables and volume mappings. The folders where phockup moves files are always /mnt/input and /mnt/output within the container and can not be changed. You can of course map any folder on your host system to those folders within the container.

The `-v ~/Pictures/input:/mnt/input` part of the command mounts your `~/Pictures/input` directory to `/mnt/input` inside the container. The same is done for the output folder. You can pass any **absolute** path to be mounted to the container and later on be used as paths for the `phockup` command. The example above provides your `~/Pictures/input` as `INPUTDIR` and `~/Pictures/output` as `OUTPUDIR`. You can pass additional arguments through the `OPTIONS` environment variable.

To keep the container running and execute phockup in intervals, use the following command:

```
docker run -v ~/Pictures/input:/mnt/input -v ~/Pictures/output:/mnt/output -e "CRON=* * * * *" -e "OPTIONS=[PHOCKUP ARGUMENTS]" ivandokov/phockup:latest
```

This will execute phockup once every minute (as defined by the [value of the CRON environment variable](https://crontab.guru/#*_*_*_*_*)). However, the container will not spawn a new phockup process if another phockup process is still running. You can define other intervals for execution using the usual cron syntax. If you want to pass further arguments to phockup, use the OPTIONS environment variable. In this execution mode, phockup will always use the directories mounted to `/mnt/input` and `/mnt/output` and ignore arguments passed in the style of the single execution mode.

### Mac
Requires [Homebrew](http://brew.sh/)
```
brew tap ivandokov/homebrew-contrib
brew install phockup
```

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
cd /opt/phockup
pip3 install -r requirements.txt
sudo ln -s /opt/phockup/phockup.py /usr/local/bin/phockup
```

### Linux (AUR)

If you are an arch user you can install from the [aur](https://aur.archlinux.org/packages/phockup).

For example using [yay](https://github.com/Jguer/yay):

```bash
yay -S phockup
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

### Version
If you want to view the version of phockup use the flag `-v | --version`.

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
    U    - 00, 01, 53 ... (week of the year, Sunday first day of week)
    W    - 00, 01, 53 ... (week of the year, Monday first day of week)

Example:
    YYYY/MM/DD -> 2011/07/17
    YYYY/M/DD  -> 2011/July/17
    YYYY/m/DD  -> 2011/Jul/17
    YY/m-DD    -> 11/Jul-17
    YYYY/U     -> 2011/30
    YYYY/W     -> 2011/28
```

### Prefix/Suffix
In order to support both aggregation and finer granularity of files
sorted, you can specify a prefix or suffix (or both) to aid in storing
files in directories beyond strictly date.

*NOTE:* Prefixes and suffixes will also apply to the **'unknown'** folder to
isolate files that cannot be processed into their respective folders.
This creates a bit more chaos for 'unknown' files, but should allow
them to be managed by whomever they "belong" to.

#### Prefix
`--output-prefix` flag can be used to specify a directory to be
appended to the `OUTPUTDIR`, and thus prepended to the date.

For example:
```
phockup ~/Pictures/camera /mnt/sorted --output_prefix=nikon
```
would place files in folders similar to:
```
/mnt/sorted/nikon/2011/07/17
/mnt/sorted/nikon/unknown
```

While it may seem to be redundant with `OUTPUTDIR`, this flag is
intended to add support for more cleanly determining the output
directory at run-time via environment variable expansion (i.e. use
$USER, %USERNAME%, $HOSTNAME, etc. to aggregate files)

For example:
```
phockup ~/Pictures/camera /mnt/sorted --output_prefix=$USER
```

would yield an output directory of
```
/mnt/sorted/ivandokov/2011/07/17
/mnt/sorted/ivandokov/unknown
```

This allows the same script to be deployed to multiple users/machines
and allows sorting into their respective top level directories.

#### Suffix
`--output-suffix` flag can be used to specify a directory within the
target date directory for a file.  This allows files to be sorted in
their respective date/time folders while additionally adding a
directory based on the suffix value for additional metadata.

For example:
```
phockup ~/Pictures/DCIM/NIKOND40 /mnt/sorted --output_suffix=nikon
phockup ~/Pictures/DCIM/100APPLE /mnt/sorted --output_suffix=iphone
```

This would allow files to be stored in the following structure:

```
/mnt/sorted/2011/07/17/nikon/DCS_0001.NEF
...
/mnt/sorted/2011/07/17/nikon/DCS_0099.NEF
/mnt/sorted/unknown/nikon/

/mnt/sorted/2011/07/17/iphone/ABIL6163.HEIC
...
/mnt/sorted/2011/07/17/iphone/YZYE9497.HEIC
/mnt/sorted/unknown/iphone/
```

The output suffix also allows for environment variable expansion (e.g.
$USER, $HOSTNAME, %USERNAME%, etc.) allowing dynamic folders to
represent additional metadata about the images.

For example:

```
phockup ~/Pictures/ /mnt/sorted --output_suffix=$HOSTNAME

or

phockup ~/Pictures/ /mnt/sorted --output_suffix=$USER
```
could be used to sort images based on the source computer or user,
perventing hetrogenous collections of images from disparate sources
saving to the same central respository.

The two options above can be used to help sort/store images

#### Limit files processed by date
`--from-date` flag can be used to limit the operations to the files that are newer than the provided date (inclusive).
The date must be specified in format YYYY-MM-DD. Files with unknown date won't be skipped.

For example:
```
phockup ~/Pictures/DCIM/NIKOND40 ~/Pictures/sorted --from-date="2017-01-02"
```
`--to-date` flag can be used to limit the operations to the files that are older than the provided date (inclusive).
The date must be specified in format YYYY-MM-DD. Files with unknown date won't be skipped.

For example:
```
phockup ~/Pictures/DCIM/NIKOND40 ~/Pictures/sorted --to-date="2017-01-02"
```

`--from-date` and `--to-date` can be combined for better control over the files that are processed.

For example:
```
phockup ~/Pictures/DCIM/NIKOND40 ~/Pictures/sorted --from-date="2017-01-02" --to-date="2017-01-03"
```

### Missing date information in EXIF
If any of the photos does not have date information you can use the `-r | --regex` option to specify date format for date extraction from filenames:
```
--regex="(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})[_-]?(?P<hour>\d{2})\.(?P<minute>\d{2})\.(?P<second>\d{2})"
```

As a last resort, specify the `-t | --timestamp` option to use the file modification timestamp. This may not be accurate in all cases but can provide some kind of date if you'd rather it not go into the `unknown` folder.

### Move files
Instead of copying the process will move all files from the INPUTDIR to the OUTPUTDIR by using the flag `-m | --move`. This is useful when working with a big collection of files and the remaining free space is not enough to make a copy of the INPUTDIR.

### Link files
Instead of copying the process will create hard link all files from the INPUTDIR into new structure in OUTPUTDIR by using the flag `-l | --link`. This is useful when working with good structure of photos in INPUTDIR (like folders per device).

### Original filenames
Organize the files in selected format or using the default year/month/day format but keep original filenames by using the flag `-o | --original-names`.

### File Type
By default, Phockup addresses both image and video files. If you want to restrict your command to either images or videos only, use `--file-type=[image|video]`.

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

### Dry run
If you want phockup to run without any changes (don't copy/move any files) but just show which changes would be done, enable this feature by using the flag `-y | --dry-run`.

### Log
If you want phockup to run and store the output in a log file use the flag `--log`. This flag can be used in conjunction with the flags `--quiet` or `--progress`.
```
--log=<PATH>/log.txt
```

### Quiet run
If you want phockup to run without any output (displaying only error messages, and muting all progress messages) use the flag `--quiet`.

### Progress run
If you want phockup to run with a progressbar (displaying only the progress and muting all progress messages (including errors)) use the flag `--progress`.


### Limit directory traversal depth
If you would like to limit how deep the directories are traversed, you can use the `--maxdepth` option to specify the maximum number of levels below the input directory to process.  In order to process only the input directory, you can disable sub-directory processing with:
`--maxdepth=0`  The current implementation is limited to a maximum depth of 255.

### Improving throughput with concurrency
If you want to allocate additional CPUs/cores to the image processing
operations, you can specify additional resources via the
`--max-concurrency` flag. Specifying `--max-concurrency=n`, where `n`
represents the maximum number of operations to attempt
concurrently, will leverage the additional CPU resources to start
additional file operations while waiting for file I/O.  This can lead
to significant increases in file processing throughput.

Due to how concurrency is implemented in Phockup (specifically
`ThreadPoolExecutor`), this option has the greatest impact on
directories with a large numbers of files in them,
versus many directories with small numbers of files in each.  As a
general rule, the concurrency _should not_ be set higher than the
core-count of the system processing the images.

`--max-concurrency=1` has the default behavior of no concurrency while
processing the files in the directories.  Beginning with 50% of the
cores available is a good start.  Larger numbers can have
diminishing returns as the number of concurrent operations saturate
the file I/O of the system.

Concurrently processing files does have an impact on the order that
messages are written to the console/log and the ability to quickly
terminate the program, as the execution waits for all in-flight
operations to complete before shutting down.

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

To run the tests with coverage reports run
```bash
pytest --cov-report term-missing:skip-covered --cov=src tests/
```

Please add the necessary tests when committing a feature or improvement.


### Pre-commit checks
We leverage the [pre-commit](https://pre-commit.com/) framework to automate some general linting/quality checks.

To install the hooks, from within the activated virtualenv run:

```bash
pre-commit install
```

To manually execute the hooks, run:

```bash
pre-commit run -a
```

### Style Guide Ruleset
Please make sure that the code is compliant as described below when committing a feature or improvement.

#### Flake8
We use [flake8](https://flake8.pycqa.org/en/latest/) to check the PEP 8 ruleset.

Code style for the line length are following the description of the tool [black](https://black.readthedocs.io/en/stable/the_black_code_style.html#line-length)
In a nutshell, this comes down to 88 characters per line. This number was found to produce significantly shorter files.

#### isort
We also use [isort](https://github.com/PyCQA/isort) to check if import are sorted alphabetically, separated into sections and by type.

##### single-quotes and double-quotes
We try to adhere to the following as much as possible:
Use single-quotes for string literals, e.g. 'my-identifier', but use double-quotes for strings that are likely to contain single-quote characters as part of the string itself (such as error messages, or any strings containing natural language), e.g. "You've got an error!".

Single-quotes are easier to read and to type, but if a string contains single-quote characters then double-quotes are better than escaping the single-quote characters or wrapping the string in double single-quotes.
