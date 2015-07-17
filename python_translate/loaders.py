# -*- coding: utf-8 -*-
"""
This file is a part of python_translate package
(c) Adam Zieliński <adam@symfony2.guru>

This file is derived from Symfony package.
(c) Fabien Potencier <fabien@symfony.com>

For the full copyright and license information, please view the LICENSE and LICENSE_SYMFONY_TRANSLATION
files that were distributed with this source code.
"""


import sys
import os.path
import yaml
import json
import collections
import python_translate.translations

class NotFoundResourceException(Exception):
    pass


class InvalidResourceException(Exception):
    pass


class Loader(object):

    """
    Loader is the abstract class that all translation loaders are supposed to extend
    """

    def load(self, resource, locale, domain='messages'):
        """
        Loads a locale.

        @type resource: mixed
        @param resource: A resource

        @type locale: str
        @param locale: A locale

        @type domain: str
        @param domain: The domain

        @rtype: MessageCatalogue
        @return: A MessageCatalogue instance

        @raises: NotFoundResourceException when the resource cannot be found
        @raises: InvalidResourceException  when the resource cannot be loaded
        """
        raise NotImplementedError()


class FileMixin(object):

    """
    FileMixin is a class that has some helper methods for file-based loaders
    """

    def assert_valid_path(self, path):
        """
        Ensures that the path represents an existing file

        @type path: str
        @param path: path to check

        """
        if not isinstance(path, str):
            raise NotFoundResourceException(
                "Resource passed to load() method must be a file path")

        if not os.path.isfile(path):
            raise NotFoundResourceException(
                'File "{0}" does not exist'.format(path))

    def read_file(self, path):
        """
        Reads a file into memory and returns it's contents

        @type path: str
        @param path: path to load
        """

        self.assert_valid_path(path)

        with open(path, 'r') as file:
            contents = file.read()

        return contents

    def rethrow(self, msg, _type=InvalidResourceException):
        """
        Raises an exception with custom type and modified error message.
        Raised exception is based on current exc_info() and carries it's traceback

        @type msg: str
        @param msg: New error message

        @type _type: type
        @param _type: Reraised exception type

        @raises: Exception
        """
        exc_type, exc_value, exc_traceback = sys.exc_info()
        msg = msg + \
            "\nOriginal message: {0} {1}".format(exc_type.__name__, exc_value)
        raise _type(msg) #, None, exc_traceback


class DictLoader(Loader):

    """
    DictLoader loads translations from a python dict.
    """

    def load(self, resource, locale, domain='messages'):
        resource = self.flatten(resource)

        catalogue = python_translate.translations.MessageCatalogue(locale)
        catalogue.add(resource, domain)

        return catalogue

    def flatten(self, messages, parent_key=''):
        """
        Flattens an nested array of translations.

        The scheme used is:
          'key' => array('key2' => array('key3' => 'value'))
        Becomes:
          'key.key2.key3' => 'value'

        This function takes an array by reference and will modify it

        @type messages: dict
        @param messages: The dict that will be flattened

        @type parent_key: str
        @param parent_key: Current path being parsed, used internally for recursive calls
        """
        items = []
        sep = '.'
        for k, v in list(messages.items()):
            new_key = "{0}{1}{2}".format(parent_key, sep, k) if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(list(self.flatten(v, new_key).items()))
            else:
                items.append((new_key, v))
        return dict(items)


class YamlFileLoader(DictLoader, FileMixin):

    def load(self, resource, locale, domain='messages'):
        messages = yaml.safe_load(self.read_file(resource))
        if messages is None:
            messages = {}
        

        if not isinstance(messages, dict):
            raise InvalidResourceException(
                'The file passed to YamlLoader must be a YAML array')

        catalogue = super(YamlFileLoader, self).load(messages, locale, domain)
        catalogue.add_resource(resource)

        return catalogue

class DummyLoader(DictLoader, FileMixin):
    
    def load(self, resource, locale, domain='messages'):
        catalogue = python_translate.translations.MessageCatalogue(locale)
        catalogue.add({}, domain)
        catalogue.add_resource(resource)

        return catalogue


class JSONFileLoader(DictLoader, FileMixin):

    def load(self, resource, locale, domain='messages'):
        contents = self.read_file(resource)
        if contents == "":
            messages = None
        else:
            try:
                messages = json.loads(contents)
            except ValueError:
                self.rethrow(
                    "Invalid resource {0}".format(resource),
                    InvalidResourceException)

        if messages is None:
            messages = {}

        if not isinstance(messages, dict):
            raise InvalidResourceException(
                'The file passed to JSONLoader must be a JSON object')

        catalogue = super(JSONFileLoader, self).load(messages, locale, domain)
        catalogue.add_resource(resource)

        return catalogue


class PoFileLoader(DictLoader, FileMixin):

    def load(self, resource, locale, domain='messages'):
        messages = self.parse(resource)

        catalogue = super(PoFileLoader, self).load(messages, locale, domain)
        catalogue.add_resource(resource)

        return catalogue

    def parse(self, resource):
        """
        Loads given resource into a dict using polib

        @type resource: str
        @param resource: resource

        @rtype: list
        """
        try:
            import polib
        except ImportError as e:
            self.rethrow(
                "You need to install polib to use PoFileLoader or MoFileLoader",
                ImportError)

        self.assert_valid_path(resource)

        messages = {}
        parsed = self._load_contents(polib, resource)

        for item in parsed:
            if item.msgid_plural:
                plurals = sorted(item.msgstr_plural.items())
                if item.msgid and len(plurals) > 1:
                    messages[item.msgid] = plurals[0][1]
                plurals = [msgstr for idx, msgstr in plurals]
                messages[item.msgid_plural] = "|".join(plurals)
            elif item.msgid:
                messages[item.msgid] = item.msgstr

        return messages

    def _load_contents(self, polib, resource):
        """
        Parses portable object (PO) format using polib

        @type resource: str
        @param resource: resource

        @rtype: list
        """
        try:
            return polib.pofile(resource)
        except (ValueError, AttributeError) as e:
            self.rethrow(
                "Invalid resource {0}".format(resource),
                InvalidResourceException)


class MoFileLoader(PoFileLoader):

    def _load_contents(self, polib, resource):
        """
        Parses machine object (MO) format using polib

        @type resource: str
        @param resource: resource

        @rtype: list
        """
        import struct
        try:
            return polib.mofile(resource)
        except (ValueError, AttributeError, struct.error) as e:
            self.rethrow(
                "Invalid resource {0}".format(resource),
                InvalidResourceException)
