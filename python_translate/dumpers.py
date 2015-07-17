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
import sys
import shutil

import json
import yaml

# For python 2 compatibility
try:
    unicode
except NameError:
    unicode = str
    
class Dumper(object):

    """
    Dumper is the abstract class that all translation dumpers are supposed to extend
    There is no common option.
    """

    def dump(self, catalogue, options={}):
        """
        Dumps the message catalogue.

        @type catalogue: MessageCatalogue
        @param catalogue: The message catalogue

        @type options: dict
        @param options:  Options that are used by the dumper
        """
        raise NotImplementedError()


class FileDumper(Dumper):

    """
    FileDumper is an implementation of Dumper that dump a message catalogue to file(s).
    Performs backup of already existing files.

    Options:
        - path (mandatory): the directory where the files should be saved

    Attributes:
        backup                   bool  Make file backup before the dump
        relative_path_template   str   A template for the relative paths to files
    """

    backup = True
    relative_path_template = '{domain}.{locale}.{extension}'

    def dump(self, catalogue, options={}):
        if "path" not in options:
            raise ValueError("The file dumper needs a path option.")

        # save file for each domain
        for domain in catalogue.get_domains():
            full_path = os.path.join(
                options['path'],
                self.get_relative_path(
                    domain,
                    catalogue.locale))
            if os.path.isfile(full_path):
                if self.backup:
                    shutil.copyfile(full_path, full_path + "~")
            else:
                dir = os.path.dirname(full_path)
                if not os.path.isdir(dir):
                    os.mkdir(dir)

            with open(full_path, 'w+b') as f:
                text = self.format(catalogue, domain)
                if isinstance(text, unicode):
                    f.write(text.decode('UTF-8') if hasattr(text, 'decode') else bytes(text, 'UTF-8'))
                else:
                    f.write(text)

            # ? delete backup ?

    def format(self, catalogue, domain):
        """
        Transforms a domain of a message catalogue to its string representation.

        @type catalogue: MessageCatalogue
        @type domain: str

        @rtype: str
        @return: representation
        """
        raise NotImplementedError()

    def get_extension(self):
        """
        Gets the file extension of the dumper.

        @rtype: str
        @return: file extension
        """
        raise NotImplementedError()

    def get_relative_path(self, domain, locale):
        """
        Gets the relative file path using the template.

        @type domain: str
        @param domain: The domain

        @type locale: str
        @param locale: The locale

        @rtype: string
        @return: The relative file path
        """
        return self.relative_path_template.format(
            domain=domain,
            locale=locale,
            extension=self.get_extension()
        )


class JSONFileDumper(FileDumper):

    def format(self, catalogue, domain):
        return json.dumps(catalogue.all(domain), indent=4)

    def get_extension(self):
        return 'json'


class YamlFileDumper(FileDumper):

    def format(self, catalogue, domain):
        return yaml.safe_dump(
            catalogue.all(domain),
            encoding='utf-8',
            allow_unicode=True,
            default_flow_style=False).decode('utf-8')

    def get_extension(self):
        return 'yml'


class PoFileDumper(FileDumper):

    def format(self, catalogue, domain):
        return self._build_po_file(
            catalogue,
            domain).__unicode__().encode("utf-8")

    def _build_po_file(self, catalogue, domain):
        try:
            import polib
        except ImportError as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            msg = "You need to install polib to use PoFileDumper or MoFileDumper"
            msg = msg + \
                "\nOriginal message: {0} {1}".format(exc_type.__name__, exc_value)
            raise ImportError(msg) #, None, exc_traceback

        po = polib.POFile()
        po.metadata = {
            # 'msgid': '',
            # 'msgstr': '',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
            'Language': catalogue.locale,
        }

        for source, target in list(catalogue.all(domain).items()):
            po.append(polib.POEntry(
                msgid=source,
                msgstr=target
            ))

        return po

    def get_extension(self):
        return 'po'


class MoFileDumper(PoFileDumper):

    def format(self, catalogue, domain):
        po = self._build_po_file(catalogue, domain)
        po.metadata = {}
        return po.to_binary()

    def get_extension(self):
        return 'mo'
