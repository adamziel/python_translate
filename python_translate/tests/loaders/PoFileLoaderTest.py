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
import collections
import unittest

from python_translate.loaders import PoFileLoader, InvalidResourceException, NotFoundResourceException

__DIR__ = os.path.dirname(os.path.abspath(__file__))


class FileLoaderTest(unittest.TestCase):

    def testLoad(self):
        loader = PoFileLoader()
        resource = __DIR__ + '/../fixtures/resources.po'
        catalogue = loader.load(resource, 'en', 'domain1')

        self.assertEquals({'foo': 'bar'}, catalogue.all('domain1'))
        self.assertEquals('en', catalogue.locale)
        self.assertEquals([resource], catalogue.get_resources())

    def testLoadPlurals(self):
        loader = PoFileLoader()
        resource = __DIR__ + '/../fixtures/plurals.po'
        catalogue = loader.load(resource, 'en', 'domain1')

        self.assertEquals(
            {'foo': 'bar', 'foos': 'bar|bars'}, catalogue.all('domain1'))
        self.assertEquals('en', catalogue.locale)
        self.assertEquals([resource], catalogue.get_resources())

    def testLoadDoesNothingIfEmpty(self):
        loader = PoFileLoader()
        resource = __DIR__ + '/../fixtures/empty.po'
        catalogue = loader.load(resource, 'en', 'domain1')

        self.assertEquals({}, catalogue.all('domain1'))
        self.assertEquals('en', catalogue.locale)
        self.assertEquals([resource], catalogue.get_resources())

    def testLoadEmptyTranslation(self):
        loader = PoFileLoader()
        resource = __DIR__ + '/../fixtures/empty-translation.po'
        catalogue = loader.load(resource, 'en', 'domain1')

        self.assertEquals({'foo': ''}, catalogue.all('domain1'))
        self.assertEquals('en', catalogue.locale)
        self.assertEquals([resource], catalogue.get_resources())

    def testEscapedId(self):
        loader = PoFileLoader()
        resource = __DIR__ + '/../fixtures/escaped-id.po'
        catalogue = loader.load(resource, 'en', 'domain1')

        messages = catalogue.all('domain1')
        self.assertIn('escaped "foo"', messages)
        self.assertEquals('escaped "bar"', messages['escaped "foo"'])

    def testEscapedIdPlurals(self):
        loader = PoFileLoader()
        resource = __DIR__ + '/../fixtures/escaped-id-plurals.po'
        catalogue = loader.load(resource, 'en', 'domain1')

        messages = catalogue.all('domain1')
        self.assertIn('escaped "foo"', messages)
        self.assertIn('escaped "foos"', messages)
        self.assertEquals('escaped "bar"', messages['escaped "foo"'])
        self.assertEquals(
            'escaped "bar"|escaped "bars"',
            messages['escaped "foos"'])


if __name__ == '__main__':
    unittest.main()
