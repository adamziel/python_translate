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

from python_translate.loaders import MoFileLoader, InvalidResourceException, NotFoundResourceException

__DIR__ = os.path.dirname(os.path.abspath(__file__))


class FileLoaderTest(unittest.TestCase):

    def testLoad(self):
        loader = MoFileLoader()
        resource = __DIR__ + '/../fixtures/resources.mo'
        catalogue = loader.load(resource, 'en', 'domain1')

        self.assertEquals({'foo': 'bar'}, catalogue.all('domain1'))
        self.assertEquals('en', catalogue.locale)
        self.assertEquals([resource], catalogue.get_resources())

    def testLoadPlurals(self):
        loader = MoFileLoader()
        resource = __DIR__ + '/../fixtures/plurals.mo'
        catalogue = loader.load(resource, 'en', 'domain1')

        self.assertEquals(
            {'foo': 'bar', 'foos': 'bar|bars'}, catalogue.all('domain1'))
        self.assertEquals('en', catalogue.locale)
        self.assertEquals([resource], catalogue.get_resources())

    def testLoadNonExistingResource(self):
        loader = MoFileLoader()
        resource = __DIR__ + '/../fixtures/non-existing.mo'
        self.assertRaises(
            NotFoundResourceException,
            lambda: loader.load(
                resource,
                'en',
                'domain1'))

    def testLoadInvalidResource(self):
        loader = MoFileLoader()
        resource = __DIR__ + '/../fixtures/empty.mo'
        self.assertRaises(
            InvalidResourceException,
            lambda: loader.load(
                resource,
                'en',
                'domain1'
            )
        )

    def testLoadEmptyTranslation(self):
        loader = MoFileLoader()
        resource = __DIR__ + '/../fixtures/empty-translation.mo'
        catalogue = loader.load(resource, 'en', 'domain1')

        self.assertEquals({'foo': ''}, catalogue.all('domain1'))
        self.assertEquals('en', catalogue.locale)
        self.assertEquals([resource], catalogue.get_resources())


if __name__ == '__main__':
    unittest.main()
