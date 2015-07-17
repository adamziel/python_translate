# -*- coding: utf-8 -*-
"""
This file is a part of python_translate package
(c) Adam Zieliński <adam@symfony2.guru>

This file is derived from Symfony package.
(c) Fabien Potencier <fabien@symfony.com>

For the full copyright and license information, please view the LICENSE and LICENSE_SYMFONY_TRANSLATION
files that were distributed with this source code.
"""

from python_translate.translations import MessageCatalogue

class AbstractOperation(object):

    """
    Base catalogues binary operation class.
    @author Jean-François Simon <contact@jfsimon.fr>
    @author Adam Zielinski <adam@symfony2.guru>

    Attributes:
        source   MessageCatalogue
        target   MessageCatalogue
        result   MessageCatalogue
        domains  None|list
        messages dict
    """

    def __init__(self, source, target):
        """
        @type source: MessageCatalogue
        @type target: MessageCatalogue
        @raises ValueError
        """
        if source.locale != target.locale:
            raise ValueError(
                'Operated catalogues must belong to the same locale.')
        self.source = source
        self.target = target
        self.result = MessageCatalogue(source.locale)
        self.domains = None
        self.messages = {}
        super(AbstractOperation, self).__init__()

    def get_domains(self):
        """
        Returns domains affected by operation.
        @rtype: list
        """
        if self.domains is None:
            self.domains = list(
                set(self.source.get_domains() + self.target.get_domains()))
        return self.domains

    def get_messages(self, domain):
        """
        Returns all valid messages after operation.
        @type domain: str
        @rtype: dict
        """
        if domain not in self.domains:
            raise ValueError('Invalid domain: {0}'.format(domain))

        if domain not in self.messages or 'all' not in self.messages[domain]:
            self._process_domain(domain)

        return self.messages[domain]['all']

    def get_new_messages(self, domain):
        """
        Returns new valid messages after operation.
        @type domain: str
        @rtype: dict
        """
        if domain not in self.domains:
            raise ValueError('Invalid domain: {0}'.format(domain))

        if domain not in self.messages or 'new' not in self.messages[domain]:
            self._process_domain(domain)

        return self.messages[domain]['new']

    def get_obsolete_messages(self, domain):
        """
        Returns obsolete valid messages after operation.
        @type domain: str
        @rtype: dict
        """
        if domain not in self.domains:
            raise ValueError('Invalid domain: {0}'.format(domain))

        if domain not in self.messages or \
            'obsolete' not in self.messages[domain]:
            self._process_domain(domain)

        return self.messages[domain]['obsolete']

    def get_result(self):
        """
        Returns resulting catalogue
        @rtype: MessageCatalogue
        """
        for domain in self.domains:
            if domain not in self.messages:
                self._process_domain(domain)

        return self.result

    def _process_domain(self, domain):
        raise NotImplementedError()


class DiffOperation(AbstractOperation):

    """
    Diff operation between two catalogues.
    """

    def _process_domain(self, domain):
        self.messages[domain] = {
            'all': {},
            'new': {},
            'obsolete': {},
        }

        for id, message in list(self.source.all(domain).items()):
            if self.target.has(id, domain):
                self.messages[domain]['all'][id] = message
                self.result.add({id: message}, domain)
            else:
                self.messages[domain]['obsolete'][id] = message

        for id, message in list(self.target.all(domain).items()):
            if not self.source.has(id, domain):
                self.messages[domain]['all'][id] = message
                self.messages[domain]['new'][id] = message
                self.result.add({id: message}, domain)


class MergeOperation(AbstractOperation):

    """
    Merge operation between two catalogues.
    """

    def _process_domain(self, domain):
        self.messages[domain] = {
            'all': {},
            'new': {},
            'obsolete': {},
        }

        for id, message in list(self.source.all(domain).items()):
            self.messages[domain]['all'][id] = message
            self.result.add({id: message}, domain)

        for id, message in list(self.target.all(domain).items()):
            if not self.source.has(id, domain):
                self.messages[domain]['all'][id] = message
                self.messages[domain]['new'][id] = message
                self.result.add({id: message}, domain)
