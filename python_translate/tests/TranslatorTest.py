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

from python_translate.selector import select_message
from python_translate import loaders
from python_translate import dumpers
from python_translate.translations import Translator, MessageCatalogue

__DIR__ = os.path.dirname(os.path.abspath(__file__))


class TranslatorTest(unittest.TestCase):

    def testConstructorInvalidLocale(self):
        for locale, in self.getInvalidLocalesTests():
            self.assertRaises(ValueError, lambda: Translator(locale))

    def testConstructorValidLocale(self):
        for locale, in self.getValidLocalesTests():
            translator = Translator(locale)
            self.assertEquals(locale, translator.locale)

    def testConstructorWithoutLocale(self):
        translator = Translator(None)

        self.assertIsNone(translator.locale)

    def testSetGetLocale(self):
        translator = Translator('en')

        self.assertEquals('en', translator.locale)

        translator.locale = 'fr'
        self.assertEquals('fr', translator.locale)

    def testSetInvalidLocale(self):
        for locale, in self.getInvalidLocalesTests():
            translator = Translator('fr')

            def set():
                translator.locale = locale
            self.assertRaises(ValueError, set)

    def testSetValidLocale(self):
        for locale, in self.getValidLocalesTests():
            translator = Translator(locale)
            translator.locale = locale

            self.assertEquals(locale, translator.locale)

    def testget_catalogue(self):
        translator = Translator('en')

        self.assertEquals(MessageCatalogue('en'), translator.get_catalogue())

        translator.locale = 'fr'
        self.assertEquals(
            MessageCatalogue('fr'),
            translator.get_catalogue('fr'))

    def testset_fallback_locales(self):
        translator = Translator('en')
        translator.add_loader('dict', loaders.DictLoader())
        translator.add_resource('dict', {'foo': 'foofoo'}, 'en')
        translator.add_resource('dict', {'bar': 'foobar'}, 'fr')

        # force catalogue loading
        translator.trans('bar')

        translator.set_fallback_locales(['fr'])
        self.assertEquals('foobar', translator.trans('bar'))

    def testset_fallback_localesMultiple(self):
        translator = Translator('en')
        translator.add_loader('dict', loaders.DictLoader())
        translator.add_resource('dict', {'foo': 'foo (en)'}, 'en')
        translator.add_resource('dict', {'bar': 'bar (fr)'}, 'fr')

        # force catalogue loading
        translator.trans('bar')

        translator.set_fallback_locales(['fr_FR', 'fr'])
        self.assertEquals('bar (fr)', translator.trans('bar'))

    def testSetFallbackInvalidLocales(self):
        for locale, in self.getInvalidLocalesTests():
            translator = Translator('fr')
            self.assertRaises(
                ValueError, lambda: translator.set_fallback_locales(['fr', locale]))

    def testSetFallbackValidLocales(self):
        for locale, in self.getValidLocalesTests():
            translator = Translator(locale)
            translator.set_fallback_locales(['fr', locale])
            # no assertion. self method just asserts that no exception is
            # thrown

    def testTransWithFallbackLocale(self):
        translator = Translator('fr_FR')
        translator.add_loader('dict', loaders.DictLoader())
        translator.add_resource('dict', {'foo': 'foofoo'}, 'en_US')
        translator.add_resource('dict', {'bar': 'foobar'}, 'en')

        translator.set_fallback_locales(['en'])

        self.assertEquals('foobar', translator.trans('bar'))

    def testadd_resourceInvalidLocales(self):
        for locale, in self.getInvalidLocalesTests():
            translator = Translator('fr')
            self.assertRaises(
                ValueError, lambda: translator.add_resource(
                    'dict', {
                        'foo': 'foofoo'}, locale))

    def testadd_resourceValidLocales(self):
        for locale, in self.getValidLocalesTests():
            translator = Translator('fr')
            translator.add_resource('dict', {'foo': 'foofoo'}, locale)
            # no assertion. self method just asserts that no exception is
            # thrown

    def testadd_resourceAfterTrans(self):
        translator = Translator('fr')
        translator.add_loader('dict', loaders.DictLoader())

        translator.set_fallback_locales(['en'])

        translator.add_resource('dict', {'foo': 'foofoo'}, 'en')
        self.assertEquals('foofoo', translator.trans('foo'))

        translator.add_resource('dict', {'bar': 'foobar'}, 'en')
        self.assertEquals('foobar', translator.trans('bar'))

    def testTransWithoutFallbackLocaleFile(self):
        for format, loader in self.getTransFileTests():
            loader_class = getattr(loaders, loader)
            translator = Translator('en')
            translator.add_loader(format, loader_class())
            translator.add_resource(
                format,
                __DIR__ +
                '/fixtures/non-existing',
                'en')
            translator.add_resource(
                format,
                __DIR__ +
                '/fixtures/resources.' +
                format,
                'en')

            # force catalogue loading
            self.assertRaises(
                loaders.NotFoundResourceException,
                lambda: translator.trans('foo'))

    def testTransWithFallbackLocaleFile(self):
        for format, loader in self.getTransFileTests():
            loader_class = getattr(loaders, loader)
            translator = Translator('en_GB')
            translator.add_loader(format, loader_class())
            translator.add_resource(
                format,
                __DIR__ +
                '/fixtures/non-existing',
                'en_GB')
            translator.add_resource(
                format,
                __DIR__ +
                '/fixtures/resources.' +
                format,
                'en',
                'resources')

            self.assertRaises(
                loaders.NotFoundResourceException,
                self.assertEquals(
                    'bar',
                    translator.trans(
                        'foo',
                        {},
                        'resources')))

    def testTransWithFallbackLocaleBis(self):
        translator = Translator('en_US')
        translator.add_loader('dict', loaders.DictLoader())
        translator.add_resource('dict', {'foo': 'foofoo'}, 'en_US')
        translator.add_resource('dict', {'bar': 'foobar'}, 'en')
        self.assertEquals('foobar', translator.trans('bar'))

    def testTransWithFallbackLocaleTer(self):
        translator = Translator('fr_FR')
        translator.add_loader('dict', loaders.DictLoader())
        translator.add_resource('dict', {'foo': 'foo (en_US)'}, 'en_US')
        translator.add_resource('dict', {'bar': 'bar (en)'}, 'en')

        translator.set_fallback_locales(['en_US', 'en'])

        self.assertEquals('foo (en_US)', translator.trans('foo'))
        self.assertEquals('bar (en)', translator.trans('bar'))

    def testTransNonExistentWithFallback(self):
        translator = Translator('fr')
        translator.set_fallback_locales(['en'])
        translator.add_loader('dict', loaders.DictLoader())
        self.assertEquals('non-existent', translator.trans('non-existent'))

    def testWhenAResourceHasNoRegisteredLoader(self):
        translator = Translator('en')
        translator.add_resource('dict', {'foo': 'foofoo'}, 'en')

        self.assertRaises(RuntimeError, lambda: translator.trans('foo'))

    def testTrans(self):
        for expected, id, translation, parameters, locale, domain in self.getTransTests(
        ):
            translator = Translator('en')
            translator.add_loader('dict', loaders.DictLoader())
            translator.add_resource(
                'dict', {
                    str(id): translation}, locale, domain)

            self.assertEquals(
                expected,
                translator.trans(
                    id,
                    parameters,
                    domain,
                    locale))

    def testTransInvalidLocale(self):
        for locale, in self.getInvalidLocalesTests():
            translator = Translator('en')
            translator.add_loader('dict', loaders.DictLoader())
            translator.add_resource('dict', {'foo': 'foofoo'}, 'en')

            self.assertRaises(
                ValueError,
                lambda: translator.trans(
                    'foo',
                    {},
                    '',
                    locale))

    def testTransValidLocale(self):
        for locale, in self.getValidLocalesTests():
            translator = Translator('en')
            translator.add_loader('dict', loaders.DictLoader())
            translator.add_resource('dict', {'foo': 'foofoo'}, 'en')

            translator.trans('foo', {}, '', locale)
            # no assertion. self method just asserts that no exception is
            # thrown

    def testFlattenedTrans(self):
        for expected, messages, id in self. getFlattenedTransTests():
            translator = Translator('en')
            translator.add_loader('dict', loaders.DictLoader())
            translator.add_resource('dict', messages, 'fr', '')

            self.assertEquals(expected, translator.trans(id, {}, '', 'fr'))

    def testtranschoice(self):
        for expected, id, translation, number, parameters, locale, domain in self.gettranschoiceTests(
        ):
            translator = Translator('en')
            translator.add_loader('dict', loaders.DictLoader())
            translator.add_resource(
                'dict', {
                    str(id): translation}, locale, domain)

            self.assertEquals(
                expected,
                translator.transchoice(
                    id,
                    number,
                    parameters,
                    domain,
                    locale))

    def testtranschoiceInvalidLocale(self):
        for locale, in self.getInvalidLocalesTests():
            translator = Translator('en')
            translator.add_loader('dict', loaders.DictLoader())
            translator.add_resource('dict', {'foo': 'foofoo'}, 'en')

            self.assertRaises(
                ValueError,
                lambda: translator.transchoice(
                    'foo',
                    1,
                    {},
                    '',
                    locale))

    def testtranschoiceValidLocale(self):
        for locale, in self.getValidLocalesTests():
            translator = Translator('en')
            translator.add_loader('dict', loaders.DictLoader())
            translator.add_resource('dict', {'foo': 'foofoo'}, 'en')

            translator.transchoice('foo', 1, {}, '', locale)
            # no assertion. self method just asserts that no exception is
            # thrown

    def getTransFileTests(self):
        return [
            # ['csv', 'CsvFileLoader'],
            # ['ini', 'IniFileLoader'],
            ['mo', 'MoFileLoader'],
            ['po', 'PoFileLoader'],
            # ['php', 'PhpFileLoader'],
            # ['ts', 'QtFileLoader'],
            # ['xlf', 'XliffFileLoader'],
            ['yml', 'YamlFileLoader'],
            ['json', 'JSONFileLoader'],
        ]

    def getTransTests(self):
        return [['Symfony est super !',
                 'Symfony is great!',
                 'Symfony est super !',
                 {},
                 'fr',
                 ''],
                ['Symfony est awesome !',
                 'Symfony is {what}!',
                 'Symfony est {what} !',
                 {'what': 'awesome'},
                 'fr',
                 ''],
                ]

    def getFlattenedTransTests(self):
        messages = {
            'symfony': {
                'is': {
                    'great': 'Symfony est super!',
                },
            },
            'foo': {
                'bar': {
                    'baz': 'Foo Bar Baz',
                },
                'baz': 'Foo Baz',
            },
        }

        return [
            ['Symfony est super!', messages, 'symfony.is.great'],
            ['Foo Bar Baz', messages, 'foo.bar.baz'],
            ['Foo Baz', messages, 'foo.baz'],
        ]

    def gettranschoiceTests(self):
        return [['Il y a 0 pomme',
                 '{0}There are no appless|{1}There is one apple|]1,Inf] There is {count} apples',
                 '[0,1] Il y a {count} pomme|]1,Inf] Il y a {count} pommes',
                 0,
                 {'count': 0},
                 'fr',
                 ''],
                ['Il y a 1 pomme',
                 '{0}There are no appless|{1}There is one apple|]1,Inf] There is {count} apples',
                 '[0,1] Il y a {count} pomme|]1,Inf] Il y a {count} pommes',
                 1,
                 {'count': 1},
                 'fr',
                 ''],
                ['Il y a 10 pommes',
                 '{0}There are no appless|{1}There is one apple|]1,Inf] There is {count} apples',
                 '[0,1] Il y a {count} pomme|]1,Inf] Il y a {count} pommes',
                 10,
                 {'count': 10},
                 'fr',
                 ''],
                ['Il y a 0 pomme',
                 'There is one apple|There is {count} apples',
                 'Il y a {count} pomme|Il y a {count} pommes',
                 0,
                 {'count': 0},
                 'fr',
                 ''],
                ['Il y a 1 pomme',
                 'There is one apple|There is {count} apples',
                 'Il y a {count} pomme|Il y a {count} pommes',
                 1,
                 {'count': 1},
                 'fr',
                 ''],
                ['Il y a 10 pommes',
                 'There is one apple|There is {count} apples',
                 'Il y a {count} pomme|Il y a {count} pommes',
                 10,
                 {'count': 10},
                 'fr',
                 ''],
                ['Il y a 0 pomme',
                 'one: There is one apple|more: There is {count} apples',
                 'one: Il y a {count} pomme|more: Il y a {count} pommes',
                 0,
                 {'count': 0},
                 'fr',
                 ''],
                ['Il y a 1 pomme',
                 'one: There is one apple|more: There is {count} apples',
                 'one: Il y a {count} pomme|more: Il y a {count} pommes',
                 1,
                 {'count': 1},
                 'fr',
                 ''],
                ['Il y a 10 pommes',
                 'one: There is one apple|more: There is {count} apples',
                 'one: Il y a {count} pomme|more: Il y a {count} pommes',
                 10,
                 {'count': 10},
                 'fr',
                 ''],
                ['Il n\'y a aucune pomme',
                 '{0}There are no apples|one: There is one apple|more: There is {count} apples',
                 '{0}Il n\'y a aucune pomme|one: Il y a {count} pomme|more: Il y a {count} pommes',
                 0,
                 {'count': 0},
                 'fr',
                 ''],
                ['Il y a 1 pomme',
                 '{0}There are no apples|one: There is one apple|more: There is {count} apples',
                 '{0}Il n\'y a aucune pomme|one: Il y a {count} pomme|more: Il y a {count} pommes',
                 1,
                 {'count': 1},
                 'fr',
                 ''],
                ['Il y a 10 pommes',
                 '{0}There are no apples|one: There is one apple|more: There is {count} apples',
                 '{0}Il n\'y a aucune pomme|one: Il y a {count} pomme|more: Il y a {count} pommes',
                 10,
                 {'count': 10},
                 'fr',
                 ''],
                ]

    def getInvalidLocalesTests(self):
        return [
            ['fr FR'],
            ['français'],
            ['fr+en'],
            ['utf#8'],
            ['fr&en'],
            ['fr~FR'],
            [' fr'],
            ['fr '],
            ['fr*'],
            ['fr/FR'],
            ['fr\\FR'],
        ]

    def getValidLocalesTests(self):
        return [
            [''],
            [None],
            ['fr'],
            ['francais'],
            ['FR'],
            ['frFR'],
            ['fr-FR'],
            ['fr_FR'],
            ['fr.FR'],
            ['fr-FR.UTF8'],
            ['sr@latin'],
        ]

    def testtranschoiceFallback(self):
        translator = Translator('ru')
        translator.set_fallback_locales(['en'])
        translator.add_loader('dict', loaders.DictLoader())
        translator.add_resource(
            'dict', {
                'some_message2': 'one thing|{count} things'}, 'en')

        self.assertEquals(
            '10 things', translator.transchoice(
                'some_message2', 10, {
                    'count': 10}))

    def testtranschoiceFallbackBis(self):
        translator = Translator('ru')
        translator.set_fallback_locales(['en_US', 'en'])
        translator.add_loader('dict', loaders.DictLoader())
        translator.add_resource(
            'dict', {
                'some_message2': 'one thing|{count} things'}, 'en_US')

        self.assertEquals(
            '10 things', translator.transchoice(
                'some_message2', 10, {
                    'count': 10}))

    def testtranschoiceFallbackWithNoTranslation(self):
        translator = Translator('ru')
        translator.set_fallback_locales(['en'])
        translator.add_loader('dict', loaders.DictLoader())

        # consistent behavior with Translator::trans(), which returns the string
        # unchanged if it can't be found
        self.assertEquals(
            'some_message2', translator.transchoice(
                'some_message2', 10, {
                    'count': 10}))

    def testGetMessages(self):
        for resources, locale, expected in self.dataProviderGetMessages():
            locales = list(resources.keys())
            _locale = locale if locale is not None else locales[0]
            locales = locales[0:locales.index(_locale,)]

            translator = Translator(_locale)
            translator.set_fallback_locales(locales[::-1])
            translator.add_loader('dict', loaders.DictLoader())
            for _locale, domainMessages in list(resources.items()):
                for domain, messages in list(domainMessages.items()):
                    translator.add_resource('dict', messages, _locale, domain)

            result = translator.get_messages(locale)

            self.assertEquals(expected, result)

    def dataProviderGetMessages(self):
        resources = collections.OrderedDict((
            ('en', {
                'jsmessages': {
                    'foo': 'foo (EN)',
                    'bar': 'bar (EN)',
                },
                'messages': {
                    'foo': 'foo messages (EN)',
                },
                'validators': {
                    'int': 'integer (EN)',
                },
            }),
            ('pt-PT', {
                'messages': {
                    'foo': 'foo messages (PT)',
                },
                'validators': {
                    'str': 'integer (PT)',
                },
            }),
            ('pt_BR', {
                'validators': {
                    'int': 'integer (BR)',
                },
            }),
        ))

        return [
            [resources, None,
                {
                    'jsmessages': {
                        'foo': 'foo (EN)',
                        'bar': 'bar (EN)',
                    },
                    'messages': {
                        'foo': 'foo messages (EN)',
                    },
                    'validators': {
                        'int': 'integer (EN)',
                    },
                },
             ],
            [resources, 'en',
                {
                    'jsmessages': {
                        'foo': 'foo (EN)',
                        'bar': 'bar (EN)',
                    },
                    'messages': {
                        'foo': 'foo messages (EN)',
                    },
                    'validators': {
                        'int': 'integer (EN)',
                    },
                },
             ],
            [resources, 'pt-PT',
                {
                    'jsmessages': {
                        'foo': 'foo (EN)',
                        'bar': 'bar (EN)',
                    },
                    'messages': {
                        'foo': 'foo messages (PT)',
                    },
                    'validators': {
                        'int': 'integer (EN)',
                        'str': 'integer (PT)',
                    },
                }
             ],
            [resources, 'pt_BR',
                {
                    'jsmessages': {
                        'foo': 'foo (EN)',
                        'bar': 'bar (EN)',
                    },
                    'messages': {
                        'foo': 'foo messages (PT)',
                    },
                    'validators': {
                        'int': 'integer (BR)',
                        'str': 'integer (PT)',
                    },
                },
             ],
        ]

if __name__ == '__main__':
    unittest.main()
