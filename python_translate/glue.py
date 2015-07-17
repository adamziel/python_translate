# -*- coding: utf-8 -*-
"""
This file is a part of python_translate package
(c) Adam Zieliński <adam@symfony2.guru>

This file is derived from Symfony package.
(c) Fabien Potencier <fabien@symfony.com>

For the full copyright and license information, please view the LICENSE and LICENSE_SYMFONY_TRANSLATION
files that were distributed with this source code.
"""

import os
from python_translate.utils import find_files

class TransationLoader(object):

    """
    TranslationWriter loads translation messages from a given directory.
    """

    def __init__(self):
        self.loaders = {}  # Loaders used for import.

    def add_loader(self, format, loader):
        """
        Adds a loader to the the translation extractor.

        @type format: string
        @param format: The format of the loader

        @type loader: Loader
        @param loader: The loader
        """
        self.loaders[format] = loader

    def load_messages(self, directory, catalogue):
        """
        Loads translation found in a directory.

        @type directory: string
        @param directory: The directory to search

        @type catalogue: MessageCatalogue
        @param catalogue: The message catalogue to dump

        @raises: ValueError
        """
        if not os.path.isdir(directory):
            raise ValueError("{0} is not a directory".format(directory))

        for format, loader in list(self.loaders.items()):
            extension = "{0}.{1}".format(catalogue.locale, format)
            files = find_files(directory, "*.{0}".format(extension))
            for file in files:
                domain = file.split("/")[-1][:-1 * len(extension) - 1]
                catalogue.add_catalogue(
                    loader.load(
                        file,
                        catalogue.locale,
                        domain))


class TranslationWriter(object):

    """
    TranslationWriter writes translation messages.
    """

    def __init__(self):
        self.dumpers = {}  # Dumpers used for export.

    def add_dumper(self, format, dumper):
        """
        Adds a dumper to the writer.

        @type format: string
        @param format: The format of the dumper

        @type dumper: Dumper
        @param dumper: The dumper
        """
        self.dumpers[format] = dumper

    def disable_backup(self):
        """
        Disables dumper backup.
        """
        for dumper in list(self.dumpers.values()):
            dumper.set_backup(False)

    def get_formats(self):
        """
        Obtains the list of supported formats.

        @rtype: list
        """
        return list(self.dumpers.keys())

    def write_translations(self, catalogue, format, options={}):
        """
        Writes translation from the catalogue according to the selected format.

        @type catalogue: MessageCatalogue
        @param catalogue: The message catalogue to dump

        @type format: string
        @param format: The format to use to dump the messages

        @type options: array
        @param options: Options that are passed to the dumper

        @raises: ValueError
        """
        if format not in self.dumpers:
            raise ValueError(
                'There is no dumper associated with format "{0}"'.format(format))

        dumper = self.dumpers[format]
        if "path" in options and not os.path.isdir(options['path']):
            os.mkdir(options['path'])

        dumper.dump(catalogue, options)
