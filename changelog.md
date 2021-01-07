# Changelog
##### `1.5.20`
* When taking the current version for snaps get the version for the current architecture and for stable channel
##### `1.5.19`
* Fixed Homebrew sha256 replacing in the deployment workflow job
##### `1.5.18`
* Move Homebrew deployment in a separate job because it was executed multiple times because of the python matrix
##### `1.5.17`
* Fixed workflow wrong step id
##### `1.5.16`
* Fixed snap deploy condition
##### `1.5.15`
* Fixed snap build volume directory
##### `1.5.14`
* Automatic snap deployment thanks to [Daniel Llewellyn's blog post](https://snapcraft.ninja/2020/08/03/snapcraft-continuous-integration-github-actions/)
##### `1.5.13`
* Fix snapcraft version extraction by [#87](https://github.com/ivandokov/phockup/issues/87)
##### `1.5.12`
* Merged [#87](https://github.com/ivandokov/phockup/issues/87)
* Merged [#88](https://github.com/ivandokov/phockup/issues/88)
##### `1.5.11`
* Added Docker support [#75](https://github.com/ivandokov/phockup/issues/75)
##### `1.5.10`
* Merged [#78](https://github.com/ivandokov/phockup/issues/78)
* Merged [#81](https://github.com/ivandokov/phockup/issues/81)
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
