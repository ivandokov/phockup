#!/usr/bin/env python3
import concurrent.futures
import filecmp
import logging
import os
import re
import shutil
import sys
import time

from tqdm import tqdm

from src.date import Date
from src.exif import Exif

logger = logging.getLogger('phockup')
ignored_files = ('.DS_Store', 'Thumbs.db')


class Phockup:
    DEFAULT_DIR_FORMAT = ['%Y', '%m', '%d']
    DEFAULT_NO_DATE_DIRECTORY = "unknown"

    def __init__(self, input_dir, output_dir, **args):
        start_time = time.time()
        self.files_processed = 0
        self.duplicates_found = 0
        self.unknown_found = 0
        self.files_moved = 0
        self.files_copied = 0

        input_dir = os.path.expanduser(input_dir)
        output_dir = os.path.expanduser(output_dir)

        if input_dir.endswith(os.path.sep):
            input_dir = input_dir[:-1]
        if output_dir.endswith(os.path.sep):
            output_dir = output_dir[:-1]

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_prefix = args.get('output_prefix' or None)
        self.output_suffix = args.get('output_suffix' or '')
        self.no_date_dir = args.get('no_date_dir') or Phockup.DEFAULT_NO_DATE_DIRECTORY
        self.dir_format = args.get('dir_format') or os.path.sep.join(Phockup.DEFAULT_DIR_FORMAT)
        self.move = args.get('move', False)
        self.link = args.get('link', False)
        self.original_filenames = args.get('original_filenames', False)
        self.date_regex = args.get('date_regex', None)
        self.timestamp = args.get('timestamp', False)
        self.date_field = args.get('date_field', False)
        self.skip_unknown = args.get("skip_unknown", False)
        self.movedel = args.get("movedel", False),
        self.rmdirs = args.get("rmdirs", False),
        self.dry_run = args.get('dry_run', False)
        self.progress = args.get('progress', False)
        self.max_depth = args.get('max_depth', -1)
        # default to concurrency of one to retain existing behavior
        self.max_concurrency = args.get("max_concurrency", 1)

        self.from_date = args.get("from_date", None)
        self.to_date = args.get("to_date", None)
        if self.from_date is not None:
            self.from_date = Date.strptime(f"{self.from_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
        if self.to_date is not None:
            self.to_date = Date.strptime(f"{self.to_date} 23:59:59", "%Y-%m-%d %H:%M:%S")

        if self.max_concurrency > 1:
            logger.info(f"Using {self.max_concurrency} workers to process files.")

        self.stop_depth = self.input_dir.count(os.sep) + self.max_depth \
            if self.max_depth > -1 else sys.maxsize
        self.file_type = args.get('file_type', None)

        if self.dry_run:
            logger.warning("Dry-run phockup (does a trial run with no permanent changes)...")

        self.check_directories()
        # Get the number of files
        if self.progress:
            file_count = self.get_file_count()
            with tqdm(desc=f"Progressing: '{self.input_dir}' ",
                      total=file_count,
                      unit="file",
                      position=0,
                      leave=True,
                      ascii=(sys.platform == 'win32')) as self.pbar:
                self.walk_directory()
        else:
            self.pbar = None
            self.walk_directory()

        if self.move and self.rmdirs:
            self.rm_subdirs()

        run_time = time.time() - start_time
        if self.files_processed and run_time:
            self.print_action_report(run_time)

    def print_action_report(self, run_time):
        logger.info(f"Processed {self.files_processed} files in {run_time:.2f} seconds. Average Throughput: {self.files_processed/run_time:.2f} files/second")
        if self.unknown_found:
            logger.info(f"Found {self.unknown_found} files without EXIF date data.")
        if self.duplicates_found:
            logger.info(f"Found {self.duplicates_found} duplicate files.")
        if self.files_copied:
            if self.dry_run:
                logger.info(f"Would have copied {self.files_copied} files.")
            else:
                logger.info(f"Copied {self.files_copied} files.")
        if self.files_moved:
            if self.dry_run:
                logger.info(f"Would have moved {self.files_moved} files.")
            else:
                logger.info(f"Moved {self.files_moved} files.")

    def check_directories(self):
        """
        Check if input and output directories exist.
        If input does not exist it exits the process.
        If output does not exist it tries to create it or exit with error.
        """

        if not os.path.exists(self.input_dir):
            raise RuntimeError(f"Input directory '{self.input_dir}' does not exist")
        if not os.path.isdir(self.input_dir):
            raise RuntimeError(f"Input directory '{self.input_dir}' is not a directory")
        if not os.path.exists(self.output_dir):
            logger.warning(f"Output directory '{self.output_dir}' does not exist, creating now")
            try:
                if not self.dry_run:
                    os.makedirs(self.output_dir)
            except OSError:
                raise OSError(f"Cannot create output '{self.output_dir}' directory. No write access!")

    def walk_directory(self):
        """
        Walk input directory recursively and call process_file for each file
        except the ignored ones.
        """

        # Walk the directory
        for root, dirnames, files in os.walk(self.input_dir):
            files.sort()
            file_paths_to_process = []
            for filename in files:
                if filename in ignored_files:
                    continue
                file_paths_to_process.append(os.path.join(root, filename))
            if self.max_concurrency > 1:
                if not self.process_files(file_paths_to_process):
                    return
            else:
                try:
                    for file_path in file_paths_to_process:
                        self.process_file(file_path)
                except KeyboardInterrupt:
                    logger.warning("Received interrupt. Shutting down...")
                    return
            if root.count(os.sep) >= self.stop_depth:
                del dirnames[:]

    def rm_subdirs(self):
        def _get_depth(sub_path):
            return sub_path.count(os.sep) - self.input_dir.count(os.sep)

        for root, dirs, files in os.walk(self.input_dir, topdown=False):
            # Traverse the tree bottom-up
            if _get_depth(root) > self.stop_depth:
                continue
            for name in dirs:
                dir_path = os.path.join(root, name)
                if _get_depth(dir_path) > self.stop_depth:
                    continue
                try:
                    os.rmdir(dir_path)  # Try to remove the dir
                    logger.info(f"Deleted empty directory: {dir_path}")
                except OSError as e:
                    logger.info(f"{e.strerror} - {dir_path} not deleted.")

    def get_file_count(self):
        file_count = 0
        for root, dirnames, files in os.walk(self.input_dir):
            file_count += len(files)
            if root.count(os.sep) >= self.stop_depth:
                del dirnames[:]
        return file_count

    def get_file_type(self, mimetype):
        """
        Check if given file_type is image or video
        Return None if other
        Use mimetype to determine if the file is an image or video.
        """
        patternImage = re.compile('^(image/.+|application/vnd.adobe.photoshop)$')
        if patternImage.match(mimetype):
            return 'image'

        patternVideo = re.compile('^(video/.*)$')
        if patternVideo.match(mimetype):
            return 'video'
        return None

    def get_output_dir(self, date):
        """
        Generate output directory path based on the extracted date and
        formatted using dir_format.
        If date is missing from the exifdata the file is going to "unknown"
        directory unless user included a regex from filename or uses timestamp.
        """
        try:
            path = [self.output_dir,
                    self.output_prefix,
                    date['date'].date().strftime(self.dir_format),
                    self.output_suffix]
        except (TypeError, ValueError):
            path = [self.output_dir,
                    self.output_prefix,
                    self.no_date_dir,
                    self.output_suffix]
        # Remove any None values that made it in the path
        path = [p for p in path if p is not None]
        fullpath = os.path.normpath(os.path.sep.join(path))

        if not os.path.isdir(fullpath) and not self.dry_run:
            os.makedirs(fullpath, exist_ok=True)

        return fullpath

    def get_file_name(self, original_filename, date):
        """
        Generate file name based on exif data unless it is missing or
        original filenames are required. Then use original file name
        """
        if self.original_filenames:
            return os.path.basename(original_filename)

        try:
            filename = [
                f'{date["date"].year :04d}',
                f'{date["date"].month :02d}',
                f'{date["date"].day :02d}',
                '-',
                f'{date["date"].hour :02d}',
                f'{date["date"].minute :02d}',
                f'{date["date"].second :02d}',
            ]

            if date['subseconds']:
                filename.append(date['subseconds'])

            return ''.join(filename) + os.path.splitext(original_filename)[1]
        # TODO: Double check if this is correct!
        except TypeError:
            return os.path.basename(original_filename)

    def process_files(self, file_paths_to_process):
        # With all the appropriate files in the directory added to the
        # list, process the directory concurrently using threads
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_concurrency) as executor:
            try:
                for _ in executor.map(self.process_file,
                                      file_paths_to_process):
                    pass
            except KeyboardInterrupt:
                logger.warning(
                        f"Received interrupt. Shutting down {self.max_concurrency} workers...")
                executor.shutdown(wait=True)
                return False
        return True

    def process_file(self, filename):
        """
        Process the file using the selected strategy
        If file is .xmp skip it so process_xmp method can handle it
        """
        if str.endswith(filename, '.xmp'):
            return None

        progress = f'{filename}'

        output, target_file_name, target_file_path, target_file_type, file_date = self.get_file_name_and_path(filename)
        suffix = 1
        target_file = target_file_path

        while True:
            if self.file_type is not None \
                    and self.file_type != target_file_type:
                progress = f"{progress} => skipped, file is '{target_file_type}' \
but looking for '{self.file_type}'"
                logger.info(progress)
                break

            date_unknown = file_date is None or output.endswith(self.no_date_dir)
            if self.skip_unknown and output.endswith(self.no_date_dir):
                # Skip files that didn't generate a path from EXIF data
                progress = f"{progress} => skipped, unknown date EXIF information for '{target_file_name}'"
                self.unknown_found += 1
                if self.progress:
                    self.pbar.write(progress)
                logger.info(progress)
                break

            if not date_unknown:
                skip = False
                if type(file_date) is dict:
                    file_date = file_date["date"]
                if self.from_date is not None and file_date < self.from_date:
                    progress = f"{progress} => {filename} skipped: date {file_date} is older than --from-date {self.from_date}"
                    skip = True
                if self.to_date is not None and file_date > self.to_date:
                    progress = f"{progress} => {filename} skipped: date {file_date} is newer than --to-date {self.to_date}"
                    skip = True
                if skip:
                    if self.progress:
                        self.pbar.write(progress)
                    logger.info(progress)
                    break

            if os.path.isfile(target_file):
                if filename != target_file and filecmp.cmp(filename, target_file, shallow=False):
                    if self.movedel and self.move and self.skip_unknown:
                        if not self.dry_run:
                            os.remove(filename)
                        progress = f'{progress} => deleted, duplicated file {target_file}'
                    else:
                        progress = f'{progress} => skipped, duplicated file {target_file}'
                    self.duplicates_found += 1
                    if self.progress:
                        self.pbar.write(progress)
                    logger.info(progress)
                    break
            else:
                if self.move:
                    try:
                        self.files_moved += 1
                        if not self.dry_run:
                            shutil.move(filename, target_file)
                    except FileNotFoundError:
                        progress = f'{progress} => skipped, no such file or directory'
                        if self.progress:
                            self.pbar.write(progress)
                        logger.warning(progress)
                        break
                elif self.link and not self.dry_run:
                    os.link(filename, target_file)
                else:
                    try:
                        self.files_copied += 1
                        if not self.dry_run:
                            shutil.copy2(filename, target_file)
                    except FileNotFoundError:
                        progress = f'{progress} => skipped, no such file or directory'
                        if self.progress:
                            self.pbar.write(progress)
                        logger.warning(progress)
                        break

                progress = f'{progress} => {target_file}'
                if self.progress:
                    self.pbar.write(progress)
                logger.info(progress)

                self.process_xmp(filename, target_file_name, suffix, output)
                break

            suffix += 1
            target_split = os.path.splitext(target_file_path)
            target_file = f'{target_split[0]}-{suffix}{target_split[1]}'

        self.files_processed += 1
        if self.progress:
            self.pbar.update(1)

    def get_file_name_and_path(self, filename):
        """
        Returns target file name and path
        """
        exif_data = Exif(filename).data()
        target_file_type = None

        if exif_data and 'MIMEType' in exif_data:
            target_file_type = self.get_file_type(exif_data['MIMEType'])

        date = None
        if target_file_type in ['image', 'video']:
            date = Date(filename).from_exif(exif_data, self.timestamp, self.date_regex,
                                            self.date_field)
            output = self.get_output_dir(date)
            target_file_name = self.get_file_name(filename, date)
            if not self.original_filenames:
                target_file_name = target_file_name.lower()
        else:
            output = self.get_output_dir([])
            target_file_name = os.path.basename(filename)

        target_file_path = os.path.sep.join([output, target_file_name])
        return output, target_file_name, target_file_path, target_file_type, date

    def process_xmp(self, original_filename, file_name, suffix, output):
        """
        Process xmp files. These are metadata for RAW images
        """
        xmp_original_with_ext = original_filename + '.xmp'
        xmp_original_without_ext = os.path.splitext(original_filename)[0] + '.xmp'

        suffix = f'-{suffix}' if suffix > 1 else ''

        xmp_files = {}

        if os.path.isfile(xmp_original_with_ext):
            xmp_target = f'{file_name}{suffix}.xmp'
            xmp_files[xmp_original_with_ext] = xmp_target
        if os.path.isfile(xmp_original_without_ext):
            xmp_target = f'{(os.path.splitext(file_name)[0])}{suffix}.xmp'
            xmp_files[xmp_original_without_ext] = xmp_target

        for original, target in xmp_files.items():
            xmp_path = os.path.sep.join([output, target])
            logger.info(f'{original} => {xmp_path}')

            if not self.dry_run:
                if self.move:
                    shutil.move(original, xmp_path)
                elif self.link:
                    os.link(original, xmp_path)
                else:
                    shutil.copy2(original, xmp_path)
