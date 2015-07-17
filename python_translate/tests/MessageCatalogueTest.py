# -*- coding: utf-8 -*-
"""
This file is a part of python_translate package
(c) Adam Zieliński <adam@symfony2.guru>

This file is derived from Symfony package.
(c) Fabien Potencier <fabien@symfony.com>

For the full copyright and license information, please view the LICENSE and LICENSE_SYMFONY_TRANSLATION
files that were distributed with this source code.
"""

import collections
import unittest

from python_translate.translations import MessageCatalogue


class TranslatorTest(unittest.TestCase):

    def testGetLocale(self):
        catalogue = MessageCatalogue('en')

        self.assertEquals('en', catalogue.locale)

    def testGetDomains(self):
        catalogue = MessageCatalogue('en', {"domain1": {}, "domain2": {}})

        self.assertEquals(['domain1', 'domain2'], sorted(catalogue.get_domains()))

    def testAll(self):
        messages = dict(domain1=dict(foo='foo'), domain2=dict(bar='bar'))
        catalogue = MessageCatalogue('en', messages)

        self.assertEquals(dict(foo='foo'), catalogue.all('domain1'))
        self.assertEquals(dict(), catalogue.all('domain88'))
        self.assertEquals(messages, catalogue.all())

    def testHas(self):
        catalogue = MessageCatalogue(
            'en', dict(
                domain1=dict(
                    foo='foo'), domain2=dict(
                    bar='bar')))

        self.assertTrue(catalogue.has('foo', 'domain1'))
        self.assertFalse(catalogue.has('bar', 'domain1'))
        self.assertFalse(catalogue.has('foo', 'domain88'))

    def testGetSet(self):
        catalogue = MessageCatalogue(
            'en', dict(
                domain1=dict(
                    foo='foo'), domain2=dict(
                    bar='bar')))
        catalogue.set('foo1', 'foo1', 'domain1')

        self.assertEquals('foo', catalogue.get('foo', 'domain1'))
        self.assertEquals('foo1', catalogue.get('foo1', 'domain1'))

    def testAdd(self):
        catalogue = MessageCatalogue(
            'en', dict(
                domain1=dict(
                    foo='foo'), domain2=dict(
                    bar='bar')))
        catalogue.add(dict(foo1='foo1'), 'domain1')

        self.assertEquals('foo', catalogue.get('foo', 'domain1'))
        self.assertEquals('foo1', catalogue.get('foo1', 'domain1'))

        catalogue.add(dict(foo='bar'), 'domain1')
        self.assertEquals('bar', catalogue.get('foo', 'domain1'))
        self.assertEquals('foo1', catalogue.get('foo1', 'domain1'))

        catalogue.add(dict(foo='bar'), 'domain88')
        self.assertEquals('bar', catalogue.get('foo', 'domain88'))

    def testReplace(self):
        messages = dict(domain1=dict(foo='foo'), domain2=dict(bar='bar'))
        catalogue = MessageCatalogue('en', messages)

        messages = dict(foo1='foo1')
        catalogue.replace(messages, 'domain1')

        self.assertEquals(messages, catalogue.all('domain1'))

    def testAddCatalogue(self):
        catalogue = MessageCatalogue(
            'en', dict(
                domain1=dict(
                    foo='foo'), domain2=dict(
                    bar='bar')))
        catalogue.add_resource('r')

        catalogue1 = MessageCatalogue('en', dict(domain1=dict(foo1='foo1')))
        catalogue1.add_resource('r1')

        catalogue.add_catalogue(catalogue1)

        self.assertEquals('foo', catalogue.get('foo', 'domain1'))
        self.assertEquals('foo1', catalogue.get('foo1', 'domain1'))

        resources = catalogue.get_resources()
        resources.sort(key=len)
        self.assertEquals(['r', 'r1'], resources)

    def testadd_fallback_catalogue(self):
        catalogue = MessageCatalogue(
            'en_US', dict(
                domain1=dict(
                    foo='foo'), domain2=dict(
                    bar='bar')))
        catalogue.add_resource('r')

        catalogue1 = MessageCatalogue(
            'en',
            dict(
                domain1=dict(
                    foo='bar',
                    foo1='foo1')))
        catalogue1.add_resource('r1')

        catalogue.add_fallback_catalogue(catalogue1)

        self.assertEquals('foo', catalogue.get('foo', 'domain1'))
        self.assertEquals('foo1', catalogue.get('foo1', 'domain1'))

        resources = catalogue.get_resources()
        resources.sort(key=len)
        self.assertEquals(['r', 'r1'], resources)

    def testadd_fallback_catalogueWithCircularReference(self):
        main = MessageCatalogue('en_US')
        fallback = MessageCatalogue('fr_FR')

        fallback.add_fallback_catalogue(main)
        self.assertRaises(
            ValueError,
            lambda: main.add_fallback_catalogue(fallback))

    def testAddCatalogueWhenLocaleIsNotTheSameAsTheCurrentOne(self):
        catalogue = MessageCatalogue('en')
        self.assertRaises(
            ValueError,
            lambda: catalogue.add_catalogue(
                MessageCatalogue(
                    'fr',
                    dict())))

    def testGetadd_resource(self):
        catalogue = MessageCatalogue('en')
        catalogue.add_resource('r')
        catalogue.add_resource('r')
        catalogue.add_resource('r1')

        resources = catalogue.get_resources()
        resources.sort(key=len)
        self.assertEquals(['r', 'r1'], resources)

    """
    # @TODO
    def testMetadataDelete(self):
        catalogue = MessageCatalogue('en')
        self.assertEquals(dict(), catalogue.getMetadata('', ''), 'Metadata is empty')
        catalogue.deleteMetadata('key', 'messages')
        catalogue.deleteMetadata('', 'messages')
        catalogue.deleteMetadata()

    def testMetadataSetGetDelete(self):
        catalogue = MessageCatalogue('en')
        catalogue.setMetadata('key', 'value')
        self.assertEquals('value', catalogue.getMetadata('key', 'messages'), "Metadata 'key' = 'value'")

        catalogue.setMetadata('key2', dict())
        self.assertEquals(dict(), catalogue.getMetadata('key2', 'messages'), 'Metadata key2 is dict')

        catalogue.deleteMetadata('key2', 'messages')
        self.assertEquals(None, catalogue.getMetadata('key2', 'messages'), 'Metadata key2 should is deleted.')

        catalogue.deleteMetadata('key2', 'domain')
        self.assertEquals(None, catalogue.getMetadata('key2', 'domain'), 'Metadata key2 should is deleted.')

    def testMetadataMerge(self):
        cat1 = MessageCatalogue('en')
        cat1.setMetadata('a', 'b')
        self.assertEquals(dict(messages=dict(a='b')), cat1.getMetadata('', ''), 'Cat1 contains messages metadata.')

        cat2 = MessageCatalogue('en')
        cat2.setMetadata('b', 'c', 'domain')
        self.assertEquals(dict(domain=dict(b='c')), cat2.getMetadata('', ''), 'Cat2 contains domain metadata.')

        cat1.addCatalogue(cat2)
        self.assertEquals(dict(messages=dict(a='b'), domain=dict(b='c')), cat1.getMetadata('', ''), 'Cat1 contains merged metadata.')
    """

if __name__ == '__main__':
    unittest.main()
