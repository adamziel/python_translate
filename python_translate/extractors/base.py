# -*- coding: utf-8 -*-
"""
This file is a part of python_translate package
(c) Adam Zieliński <adam@symfony2.guru>

For the full copyright and license information, please view the LICENSE
file that were distributed with this source code.
"""

import os
from python_translate.utils import find_files


class AbstractExtractor(object):

    def __init__(self):
        self.prefix = ""

    def extract(self, resource, catalogue):
        """
        Extracts translation messages from files, a file or a directory to the catalogue.
        @type resource: str|iterable
        @param resource: files, a file or a directory

        @type catalogue: MessageCatalogue
        @param catalogue: The catalogue
        """
        raise NotImplementedError()

    def extract_translations(self, string):
        """
        Extracts translation messages from string into an array of Translation objects
        """
        raise NotImplementedError()

    def set_prefix(self, prefix):
        """
        Sets the prefix that should be used for new found messages.
        @param string $prefix The prefix
        """
        raise NotImplementedError()


class BaseExtractor(AbstractExtractor):

    """
    Base class used by classes that extract translation messages from files.
    """

    def extract_files(self, resource):
        """
            :param resource str|iterable  files, a file or a directory
            @return: iterable
        """
        if hasattr(resource, "__iter__"):
            files = [file for file in resource if self.can_be_extracted(file)]
        elif os.path.isfile(resource):
            files = [resource] if self.can_be_extracted(resource) else []
        else:
            files = self._extract_from_directory(resource)

        return files

    def extract(self, resource, catalogue):
        files = self.extract_files(resource)
        for file in files:
            with open(file, 'r') as f:
                contents = f.read()
            translations = self.extract_translations(contents)
            for t in translations:
                if not t.id or not t.id.is_literal:
                    continue
                domain = "messages" if not t.domain or not t.domain.is_literal else t.domain.value
                catalogue.add(
                    {t.id.value: "{0}{1}".format(self.prefix, t.id.value)}, domain)

    def _is_file(self, file):
        if not os.path.isfile(file):
            raise ValueError('The "%s" file doe snot exist.' % file)
        return True

    def can_be_extracted(self, file):
        raise NotImplementedError()

    def _extract_from_directory(self, resource):
        raise NotImplementedError()

    def set_prefix(self, prefix):
        self.prefix = prefix


class ExtensionBasedExtractor(BaseExtractor):

    def __init__(self, file_extensions=None):
        self.file_extensions = file_extensions if file_extensions is not None else tuple()
        super(ExtensionBasedExtractor, self).__init__()

    def can_be_extracted(self, file):
        return os.path.isfile(file) and file.endswith(tuple([e.replace('*', '') for e in self.file_extensions]))

    def _extract_from_directory(self, resource):
        return find_files(resource, self.file_extensions)


class ChainExtractor(AbstractExtractor):

    def __init__(self):
        self._extractors = {}
        super(ChainExtractor, self).__init__()

    def add_extractor(self, format, extractor):
        self._extractors[format] = extractor

    def set_prefix(self, prefix):
        for extractor in list(self._extractors.values()):
            extractor.set_prefix(prefix)

    def extract(self, resource, catalogue):
        for extractor in list(self._extractors.values()):
            extractor.extract(resource, catalogue)


class Translation(object):

    VALID = 1
    INVALID = 2
    AMBIGOUS = 3

    def __init__(
            self,
            id,
            parameters=None,
            number=None,
            domain=None,
            locale=None,
            lineno=None,
            column=None,
            file=None,
            is_transchoice=False):
        self.id = id
        self.number = number
        self.domain = domain
        self.locale = locale
        self.parameters = parameters
        self.is_transchoice = is_transchoice

        self.file = file
        self.lineno = lineno
        self.column = column

        super(Translation, self).__init__()

    def __repr__(self):
        return str("<Translation: %s>" % str(self.id)[:25])


class TransVar(object):

    LITERAL = 1
    VARNAME = 2
    UNKNOWN = 3

    def __init__(self, value, type):
        self.value = value
        self.type = type

    @property
    def is_literal(self):
        return self.type == TransVar.LITERAL

    def __str__(self):
        return (
            '"{0}"' if self.type == TransVar.LITERAL else "{0}").format(
            self.value)

    def __repr__(self):
        fmt = (
            {
                self.LITERAL: 'LITERAL',
                self.VARNAME: 'VARNAME',
                self.UNKNOWN: 'UNKNOWN'
            }[self.type],
            str(self.value)[:25]
        )
        return str("<TransVar[%s]: %s>" % fmt)
