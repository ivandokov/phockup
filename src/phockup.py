#!/usr/bin/env python3
import concurrent.futures
import hashlib
import logging
import os
import re
import shutil
import sys
import time

from src.date import Date
from src.exif import Exif

logger = logging.getLogger('phockup')


ignored_files = ('.DS_Store', 'Thumbs.db')


class Phockup():
    def __init__(self, input_dir, output_dir, **args):
        start_time = time.time()
        input_dir = os.path.expanduser(input_dir)
        output_dir = os.path.expanduser(output_dir)

        if input_dir.endswith(os.path.sep):
            input_dir = input_dir[:-1]
        if output_dir.endswith(os.path.sep):
            output_dir = output_dir[:-1]

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.dir_format = args.get('dir_format') or os.path.sep.join(['%Y', '%m', '%d'])
        self.move = args.get('move', False)
        self.link = args.get('link', False)
        self.original_filenames = args.get('original_filenames', False)
        self.date_regex = args.get('date_regex', None)
        self.timestamp = args.get('timestamp', False)
        self.date_field = args.get('date_field', False)
        self.dry_run = args.get('dry_run', False)
        self.max_depth = args.get('max_depth', -1)
        # default to concurrency of one to retain existing behavior
        self.max_concurrency = args.get("max_concurrency", 1)
        if self.max_concurrency > 1:
            logger.warning(f"Using {self.max_concurrency} workers to process files.")

        self.stop_depth = self.input_dir.count(os.sep) + self.max_depth \
            if self.max_depth > -1 else sys.maxsize

        if self.dry_run:
            logger.warning("Dry-run phockup (does a trial run with no permanent changes)...")

        self.check_directories()
        files_proccesed = self.walk_directory()
        run_time = time.time() - start_time
        if files_proccesed and run_time:
            # Legacy string formatting syntax
            # pytest-mock v3.6.1  that was introduced recently.  When tests
            # are run, it throww the following error:
            # TypeError: unsupported format string passed to MagicMock.__format__
            # Revert to preferred syntax once MagicMock is updated
            logger.debug("Processed %d files in %1.2f  seconds. Average Throughput: %1.2f files/second" % (files_proccesed, run_time, files_proccesed/run_time))
            # Preferred syntax
            # logger.debug(f"Processed {files_proccesed} files in {run_time:.2f} seconds. Average Throughput: {files_proccesed/run_time:.2f} files/second")

    def check_directories(self):
        """
        Check if input and output directories exist.
        If input does not exists it exits the process.
        If output does not exists it tries to create it or exit with error.
        """

        if not os.path.isdir(self.input_dir) or not os.path.exists(self.input_dir):
            raise RuntimeError(f"Input directory '{self.input_dir}' does not exist or \
cannot be accessed")
        if not os.path.exists(self.output_dir):
            logger.warning(f"Output directory '{self.output_dir}' does not exist, creating now")
            try:
                if not self.dry_run:
                    os.makedirs(self.output_dir)
            except OSError:
                raise OSError(f"Cannot create output '{self.output_dir}' directory. No write \
access!")

    def walk_directory(self):
        """
        Walk input directory recursively and call process_file for each file
        except the ignored ones.
        """
        file_count = 0
        for root, dirnames, files in os.walk(self.input_dir):
            files.sort()
            file_paths_to_process = []
            for filename in files:
                file_count += 1
                if filename in ignored_files:
                    continue

                file_paths_to_process.append(os.path.join(root, filename))
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
                    executor.map(self.process_file, file_paths_to_process)

            if root.count(os.sep) >= self.stop_depth:
                del dirnames[:]
        return file_count
    def checksum(self, filename):
        """
        Calculate checksum for a file.
        Used to match if duplicated file name is actually a duplicated file.
        """
        block_size = 65536
        sha256 = hashlib.sha256()
        with open(filename, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                sha256.update(block)
        return sha256.hexdigest()

    def is_image_or_video(self, mimetype):
        """
        Use mimetype to determine if the file is an image or video.
        """
        pattern = re.compile('^(image/.+|video/.+|application/vnd.adobe.photoshop)$')
        if pattern.match(mimetype):
            return True
        return False

    def get_output_dir(self, date):
        """
        Generate output directory path based on the extracted date and
        formatted using dir_format.
        If date is missing from the exifdata the file is going to "unknown"
        directory unless user included a regex from filename or uses timestamp.
        """
        try:
            path = [self.output_dir, date['date'].date().strftime(self.dir_format)]
        except (TypeError, ValueError):
            path = [self.output_dir, 'unknown']

        fullpath = os.path.sep.join(path)

        if not os.path.isdir(fullpath) and not self.dry_run:
            os.makedirs(fullpath)

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
                f'{(date["date"].year):04d}',
                f'{(date["date"].month):02d}',
                f'{(date["date"].day):02d}',
                '-',
                f'{(date["date"].hour):02d}',
                f'{(date["date"].minute):02d}',
                f'{(date["date"].second):02d}',
            ]

            if date['subseconds']:
                filename.append(date['subseconds'])

            return ''.join(filename) + os.path.splitext(original_filename)[1]
        # TODO: Double check if this is correct!
        except TypeError:
            return os.path.basename(original_filename)

    def process_file(self, filename):
        """
        Process the file using the selected strategy
        If file is .xmp skip it so process_xmp method can handle it
        """
        if str.endswith(filename, '.xmp'):
            return None

        progress = f'{filename}'

        output, target_file_name, target_file_path = self.get_file_name_and_path(filename)

        suffix = 1
        target_file = target_file_path

        while True:
            if os.path.isfile(target_file):
                if self.checksum(filename) == self.checksum(target_file):
                    progress = f'{progress} => skipped, duplicated file {target_file}'
                    logger.info(progress)
                    break
            else:
                if self.move:
                    try:
                        if not self.dry_run:
                            shutil.move(filename, target_file)
                    except FileNotFoundError:
                        progress = f'{progress} => skipped, no such file or directory'
                        logger.warning(progress)
                        break
                elif self.link and not self.dry_run:
                    os.link(filename, target_file)
                else:
                    try:
                        if not self.dry_run:
                            shutil.copy2(filename, target_file)
                    except FileNotFoundError:
                        progress = f'{progress} => skipped, no such file or directory'
                        logger.warning(progress)
                        break

                progress = f'{progress} => {target_file}'
                logger.info(progress)

                self.process_xmp(filename, target_file_name, suffix, output)
                break

            suffix += 1
            target_split = os.path.splitext(target_file_path)
            target_file = f'{target_split[0]}-{suffix}{target_split[1]}'

    def get_file_name_and_path(self, filename):
        """
        Returns target file name and path
        """
        exif_data = Exif(filename).data()
        if exif_data and 'MIMEType' in exif_data \
                and self.is_image_or_video(exif_data['MIMEType']):
            date = Date(filename).from_exif(exif_data, self.timestamp, self.date_regex,
                                            self.date_field)
            output = self.get_output_dir(date)
            target_file_name = self.get_file_name(filename, date)
            if not self.original_filenames:
                target_file_name = target_file_name.lower()
            target_file_path = os.path.sep.join([output, target_file_name])
        else:
            output = self.get_output_dir(False)
            target_file_name = os.path.basename(filename)
            target_file_path = os.path.sep.join([output, target_file_name])

        return output, target_file_name, target_file_path

    def process_xmp(self, original_filename, file_name, suffix, output):
        """
        Process xmp files. These are meta data for RAW images
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
