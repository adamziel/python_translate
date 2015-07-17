# -*- coding: utf-8 -*-
"""
This file is a part of python_translate package
(c) Adam Zieliński <adam@symfony2.guru>

This file is derived from Symfony package.
(c) Fabien Potencier <fabien@symfony.com>

For the full copyright and license information, please view the LICENSE and LICENSE_SYMFONY_TRANSLATION
files that were distributed with this source code.
"""

import re
import collections
import string
from datetime import datetime, timedelta
from python_translate.utils import recursive_update, CaseInsensitiveDict
import python_translate.selector as selector

LOCALE_REGEX = re.compile('^[a-z0-9@_\\.\\-]*$', re.I)

# For python 2 compatibility
try:
    unicode
except NameError:
    unicode = str
    
class MessageCatalogue(object):

    def __init__(self, locale, messages=None):
        self.locale = locale
        self.messages = messages or {}
        self.messages = {k: CaseInsensitiveDict(v) for k,v in list(self.messages.items())}
        self.resources = {}
        self.metadata = None
        self.parent = None
        self.fallback_catalogue = None
        super(MessageCatalogue, self).__init__()

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_domains(self):
        """
        Gets the domains.

        @rtype: list
        @return: A list of domains
        """
        return list(self.messages.keys())

    def all(self, domain=None):
        """
        Gets the messages within a given domain.

        If domain is None, it returns all messages.

        @type id: The
        @param id: message id

        @rtype: dict
        @return: A dict of messages
        """
        if domain is None:
            return {k: dict(v) for k, v in list(self.messages.items())}

        return dict(self.messages.get(domain, {}))

    def set(self, id, translation, domain='messages'):
        """
        Sets a message translation.
        """
        assert isinstance(id, (str, unicode))
        assert isinstance(translation, (str, unicode))
        assert isinstance(domain, (str, unicode))

        self.add({id: translation}, domain)

    def has(self, id, domain):
        """
        Checks if a message has a translation.

        @rtype: bool
        @return: true if the message has a translation, false otherwise
        """
        assert isinstance(id, (str, unicode))
        assert isinstance(domain, (str, unicode))

        if self.defines(id, domain):
            return True

        if self.fallback_catalogue is not None:
            return self.fallback_catalogue.has(id, domain)

        return False

    def defines(self, id, domain='messages'):
        """
        Checks if a message has a translation (it does not take into account
        the fallback mechanism).

        @rtype: bool
        @return: true if the message has a translation, false otherwise
        """
        assert isinstance(id, (str, unicode))
        assert isinstance(domain, (str, unicode))

        return id in self.messages.get(domain, {})

    def get(self, id, domain='messages'):
        """
        Gets a message translation.

        @rtype: str
        @return: The message translation
        """
        assert isinstance(id, (str, unicode))
        assert isinstance(domain, (str, unicode))

        if self.defines(id, domain):
            return self.messages[domain][id]

        if self.fallback_catalogue is not None:
            return self.fallback_catalogue.get(id, domain)

        return id

    def replace(self, messages, domain='messages'):
        """
        Sets translations for a given domain.
        """
        assert isinstance(messages, (dict, CaseInsensitiveDict))
        assert isinstance(domain, (str, unicode))

        self.messages[domain] = CaseInsensitiveDict({})
        self.add(messages, domain)

    def add(self, messages, domain='messages'):
        """
        Adds translations for a given domain.
        """
        assert isinstance(messages, (dict, CaseInsensitiveDict))
        assert isinstance(domain, (str, unicode))

        if domain not in self.messages:
            self.messages[domain] = CaseInsensitiveDict(messages)
        else:
            self.messages[domain].update(messages)

    def add_catalogue(self, catalogue):
        """
        Merges translations from the given Catalogue into the current one.
        The two catalogues must have the same locale.

        @type id: The
        @param id: message id

        """
        assert isinstance(catalogue, MessageCatalogue)

        if catalogue.locale != self.locale:
            raise ValueError(
                'Cannot add a catalogue for locale "%s" as the '
                'current locale for this catalogue is "%s"' %
                (catalogue.locale, self.locale))

        for domain, messages in list(catalogue.all().items()):
            self.add(messages, domain)

        for resource in catalogue.resources:
            self.add_resource(resource)

    def add_fallback_catalogue(self, catalogue):
        """
        Merges translations from the given Catalogue into the current one
        only when the translation does not exist.

        This is used to provide default translations when they do not exist
        for the current locale.

        @type id: The
        @param id: message id

        """
        assert isinstance(catalogue, MessageCatalogue)

        # detect circular references
        c = self
        while True:
            if c.locale == catalogue.locale:
                raise ValueError(
                    'Circular reference detected when adding a '
                    'fallback catalogue for locale "%s".' %
                    catalogue.locale)
            c = c.parent
            if c is None:
                break

        catalogue.parent = self
        self.fallback_catalogue = catalogue

        for resource in catalogue.resources:
            self.add_resource(resource)

    def get_resources(self):
        """
        Returns an array of resources loaded to build this collection.
        @rtype: list
        @return:s: An array of resources
        """
        return list(self.resources.values())

    def add_resource(self, resource):
        """
        Adds a resource for this collection.
        :param: resource A resource instance
        """
        self.resources[unicode(resource)] = resource


class Translator(object):

    """
    Translator

    Attributes:
        catalogues         list   A list of handled MessageCatalogue
        locale             str    Locale of this Translator
        resources          list[str]
        loaders            list[Loader]
        fallback_locales   list[str]
    """

    def __init__(self, locale):
        self.catalogues = {}
        self.resources = collections.defaultdict(lambda: [])
        self.loaders = {}
        self.fallback_locales = []
        self.locale = locale
        super(Translator, self).__init__()

    @property
    def locale(self):
        """
        Returns the current locale.
        @rtype: str:
        @return: locale:
        """
        return self.__locale

    @locale.setter
    def locale(self, value):
        """
        Sets the current locale.

        @type value: str
        @raises: ValueError If the locale contains invalid characters
        """
        self._assert_valid_locale(value)
        self.__locale = value

    def trans(self, id, parameters=None, domain=None, locale=None):
        """
        Translates the given message.

        @type id: str
        @param id: The message id

        @type parameters: dict
        @param parameters: A dict of parameters for the message

        @type domain: str
        @param domain: The domain for the message or null to use the default

        @type locale: str
        @param locale: The locale or null to use the default

        @rtype: str
        @return: Translated message
        """
        if parameters is None:
            parameters = {}
        assert isinstance(parameters, dict)

        if locale is None:
            locale = self.locale
        else:
            self._assert_valid_locale(locale)

        if domain is None:
            domain = 'messages'

        msg = self.get_catalogue(locale).get(id, domain)
        return self.format(msg, parameters)

    def transchoice(self, id, number, parameters=None, domain=None, locale=None):
        """
        Translates the given choice message by choosing a translation according
        to a number.

        @type id: The
        @param id: message id

        @type number: The
        @param number: number to use to find the indice of the message

        @type parameters: An
        @param parameters: array of parameters for the message

        @type domain: The
        @param domain: domain for the message or null to use the default

        @type locale: The
        @param locale: locale or null to use the default

        @raises: ValueError

        @rtype: str
        @return: Translated message
        """
        if parameters is None:
            parameters = {}
        assert isinstance(parameters, dict)

        if locale is None:
            locale = self.locale
        else:
            self._assert_valid_locale(locale)

        if domain is None:
            domain = 'messages'

        catalogue = self.get_catalogue(locale)
        while not catalogue.defines(id, domain):
            cat = catalogue.fallback_catalogue
            if cat:
                catalogue = cat
                locale = catalogue.locale
            else:
                break

        parameters['count'] = number
        msg = selector.select_message(
            catalogue.get(
                id,
                domain
            ),
            number,
            locale)
        return self.format(msg, parameters)

    def format(self, msg, parameters):
        return string.Formatter().vformat(
            msg,
            (),
            collections.defaultdict(
                str,
                **parameters
            )
        )

    def set_fallback_locales(self, locales):
        """
        Sets the fallback locales.

        @type locales: list[str]
        @param locales: The falback locales

        @raises: ValueError: If a locale contains invalid characters
        """
        # needed as the fallback locales are linked to the already loaded
        # catalogues
        self.catalogues = {}

        for locale in locales:
            self._assert_valid_locale(locale)

        self.fallback_locales = locales

    def add_loader(self, format, loader):
        self.loaders[format] = loader

    def add_resource(self, format, resource, locale, domain=None):
        """
        Adds a resource
        @type format: str
        @param format: Name of the loader (@see add_loader)

        @type resource: str
        @param resource: The resource name

        @type locale: str
        @type domain: str

        @raises: ValueError If the locale contains invalid characters
        @return:
        """
        if domain is None:
            domain = 'messages'

        self._assert_valid_locale(locale)
        self.resources[locale].append([format, resource, domain])
        if locale in self.fallback_locales:
            self.catalogues = {}
        else:
            self.catalogues.pop(locale, None)

    def get_catalogue(self, locale=None):
        """
        @type locale: str
        @rtype: MessageCatalogue
        """
        if locale is None:
            locale = self.locale

        if locale not in self.catalogues:
            self._load_catalogue(locale)

        return self.catalogues[locale]

    def get_messages(self, locale=None):
        """
        Collects all messages for the given locale.

        @type locale:  str|one
        @param locale: Locale of translations, by default is current locale

        @rtype: dict:
        @return: dict indexed by catalog name
        """
        if locale is None:
            locale = self.locale

        if locale not in self.catalogues:
            self._load_catalogue(locale)

        catalogues = [self.catalogues[locale]]
        catalogue = catalogues[0]
        while True:
            catalogue = catalogue.fallback_catalogue
            if catalogue is None:
                break
            catalogues.append(catalogue)

        messages = {}
        for catalogue in catalogues[::-1]:
            recursive_update(messages, catalogue.all())

        return messages

    def _load_catalogue(self, locale):
        # @TODO: Caching
        self._initialize_catalogue(locale)

    def _initialize_catalogue(self, locale):
        from python_translate.loaders import NotFoundResourceException

        self._assert_valid_locale(locale)

        try:
            self._do_load_catalogue(locale)
        except NotFoundResourceException as e:
            if not self._compute_fallback_locales(locale):
                raise e
        self._load_fallback_catalogues(locale)

    def _do_load_catalogue(self, locale):
        self.catalogues[locale] = MessageCatalogue(locale)
        if locale in self.resources:
            for resource in self.resources[locale]:
                if resource[0] not in self.loaders:
                    raise RuntimeError(
                        'The "{0}" translation loader is not '
                        'registered'.format(resource[0])
                    )
                self.catalogues[locale].add_catalogue(
                    self.loaders[resource[0]].load(
                        resource[1],
                        locale,
                        resource[2]
                    )
                )

    def _load_fallback_catalogues(self, locale):
        current = self.catalogues[locale]
        for fallback in self._compute_fallback_locales(locale):
            if fallback not in self.catalogues:
                self._do_load_catalogue(fallback)

            current.add_fallback_catalogue(self.catalogues[fallback])
            current = self.catalogues[fallback]

    def _compute_fallback_locales(self, locale):
        locales = [loc for loc in self.fallback_locales if loc != locale]
        if "_" in locale:
            locales.insert(0, locale.split("_")[0])
        seen = set()

        # dedupe
        return [
            loc for loc in locales if loc not in seen and not seen.add(loc)]

    def _assert_valid_locale(self, locale):
        """
            Asserts that the locale is valid, throws a ValueError if not.
        """
        if locale is not None and not LOCALE_REGEX.match(locale):
            raise ValueError("Invalid locale '%s'" % locale)


class DebugTranslator(Translator):

    """
    Translator class to be used in development. Features:

    * Reloads translations on the fly - never restart dev server again
    * Raises a RuntimeError if a translation could not be loaded
    """

    def __init__(self, locale):
        self.last_reload = datetime.now()
        super(DebugTranslator, self).__init__(locale)

    def trans(self, id, parameters=None, domain=None, locale=None):
        """
        Throws RuntimeError whenever a message is missing
        """
        if parameters is None:
            parameters = {}

        if locale is None:
            locale = self.locale
        else:
            self._assert_valid_locale(locale)

        if domain is None:
            domain = 'messages'

        catalogue = self.get_catalogue(locale)
        if not catalogue.has(id, domain):
            raise RuntimeError(
                "There is no translation for {0} in domain {1}".format(
                    id,
                    domain
                )
            )

        msg = self.get_catalogue(locale).get(id, domain)
        return self.format(msg, parameters)

    def transchoice(self, id, number, parameters=None, domain=None, locale=None):
        """
        Raises a RuntimeError whenever a message is missing
        @raises: RuntimeError
        """
        if parameters is None:
            parameters = {}

        if locale is None:
            locale = self.locale
        else:
            self._assert_valid_locale(locale)

        if domain is None:
            domain = 'messages'

        catalogue = self.get_catalogue(locale)
        while not catalogue.defines(id, domain):
            cat = catalogue.fallback_catalogue
            if cat:
                catalogue = cat
                locale = catalogue.locale
            else:
                break

        if not catalogue.has(id, domain):
            raise RuntimeError(
                "There is no translation for {0} in domain {1}".format(
                    id,
                    domain
                )
            )

        parameters['count'] = number
        msg = selector.select_message(
            catalogue.get(
                id,
                domain
            ),
            number,
            locale
        )
        return self.format(msg, parameters)

    def get_catalogue(self, locale):
        """
        Reloads messages catalogue if requested after more than one second
        since last reload
        """
        if locale is None:
            locale = self.locale

        if locale not in self.catalogues or datetime.now() - self.last_reload > timedelta(seconds=1):
            self._load_catalogue(locale)
            self.last_reload = datetime.now()

        return self.catalogues[locale]
