# Changelog
##### `1.13.0`
* Implement `--rmdirs` [#225](https://github.com/ivandokov/phockup/pull/225)
##### `1.12.0`
* Implement `--movedel` [#223](https://github.com/ivandokov/phockup/pull/223)
##### `1.11.3`
* Fixed wrong tag in Git
##### `1.11.2`
* Fixed [deployment to Homebrew](https://github.com/ivandokov/phockup/commit/33aec10e7506fe5f70a8e244e963304ff6f54337)
##### `1.11.1`
* Fixed code styling
##### `1.11.0`
* Added `--from-date` and `--to-datezz options to limit the processed files [#202](https://github.com/ivandokov/phockup/pull/202)
* Merged dependabot PRs
* Improved documentation
##### `1.10.1`
* Fixed python versions for tests and deployments
##### `1.10.0`
* Fixed Dependabot
* Documented AUR install [#175](https://github.com/ivandokov/phockup/pull/175)
* Timezone support [#182](https://github.com/ivandokov/phockup/pull/182)
* Implementation of Issue [#146](https://github.com/ivandokov/phockup/issues/146) to support prefix and suffix [#189](https://github.com/ivandokov/phockup/pull/189)
* Documented `--max-concurrency` [#188](https://github.com/ivandokov/phockup/pull/188)
* Make sure arguments are not split [#190](https://github.com/ivandokov/phockup/pull/190)
* Dependabot PRs
##### `1.9.2`
* Fix brew SHA256 mismatch [#169](https://github.com/ivandokov/phockup/issues/169)
* Fix deploy for buildx [#168](https://github.com/ivandokov/phockup/pull/168)
* Use Python 3.10 for Docker [#167](https://github.com/ivandokov/phockup/pull/167)
* Add dependabot to project [#166](https://github.com/ivandokov/phockup/pull/166)
* Update tests.yml [#164](https://github.com/ivandokov/phockup/pull/164)
* Bump pre-commit packages [#165](https://github.com/ivandokov/phockup/pull/165)
* Fix "WARNING: --use-feature=2020-resolver no longer has any effect..."
##### `1.9.1`
* Specify platforms for Dockerhub action
##### `1.9.0`
* Rename `unknown` folder [#141](https://github.com/ivandokov/phockup/pull/141)
* Week date format [#142](https://github.com/ivandokov/phockup/pull/142)
* [Update snap to core20](https://github.com/ivandokov/phockup/commit/69783c84fe07b94e9b2c62117cf3c0ae5ca2a29e)
* [Fixed missing dep for snap](https://github.com/ivandokov/phockup/commit/b865b56f31c6fde1eadf71540bcf66ceb7744dd3)
##### `1.8.0`
* Added support for threads (`--max-concurrency`) to speed up the process [#123](https://github.com/ivandokov/phockup/pull/123)
##### `1.7.1`
* Fix dependencies due to tqdm [#133](https://github.com/ivandokov/phockup/pull/133)
* Improve check_directories output on error [#132](https://github.com/ivandokov/phockup/pull/132)
* Other improvements [#135](https://github.com/ivandokov/phockup/pull/135), [#128](https://github.com/ivandokov/phockup/pull/128)
##### `1.7.0`
* Add `--progress` functionality [#118](https://github.com/ivandokov/phockup/pull/118)
* Add pre-commit integration [#121](https://github.com/ivandokov/phockup/pull/121)
##### `1.6.5`
* Add missing checkout step to the dockerhub deployment action
##### `1.6.4`
* Add argument "--file-type" to be able to choose between image or video [#114](https://github.com/ivandokov/phockup/issues/114)
* Improved Docker image [#117](https://github.com/ivandokov/phockup/issues/117)
* Automatically deploy new Docker image to Docker Hub [#120](https://github.com/ivandokov/phockup/issues/120)
##### `1.6.3`
* Fixed double `sed`
##### `1.6.2`
* Fixed version extraction for snaps
##### `1.6.1`
* Fixed `--log` argument ([discussion](https://github.com/ivandokov/phockup/pull/106#discussion_r642048830))
* Fixed multiple custom date fields (`-f|--date-field`) [#113](https://github.com/ivandokov/phockup/issues/113)
##### `1.6.0`
* Added `--maxdepth` mode [#104](https://github.com/ivandokov/phockup/issues/104)
* Added `--quiet` mode to hide generic output [#103](https://github.com/ivandokov/phockup/issues/103)
* Fixed tests comatibility for Windows [#102](https://github.com/ivandokov/phockup/issues/102)
* Readme updates
##### `1.5.26`
* Fixed [#98](https://github.com/ivandokov/phockup/issues/98)
* [Disabled automated snap build and deploy for linux/arm64](https://github.com/ivandokov/phockup/issues/99).
##### `1.5.25`
* Fixed [#97](https://github.com/ivandokov/phockup/issues/97)
##### `1.5.24`
* Fixed broken `--date` after the merge of [#87](https://github.com/ivandokov/phockup/issues/87)
##### `1.5.23`
* Removed s930x architecture
* Update snapcraft.yml to more simple setup
##### `1.5.22`
* Fix quotes
##### `1.5.21`
* Fix hard coded variable
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
