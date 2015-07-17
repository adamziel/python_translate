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

from python_translate.selector import PluralizationRules


class PluralizationRulesTest(unittest.TestCase):

    def test_failed_langcodes(self):
        for nplural, lang_codes in self.failing_langcodes():
            matrix = self.generate_test_data(nplural, lang_codes)
            self.validate_matrix(nplural, matrix, False)

    def test_langcodes(self):
        for nplural, lang_codes in self.success_langcodes():
            matrix = self.generate_test_data(nplural, lang_codes)
            self.validate_matrix(nplural, matrix)

    def success_langcodes(self):
        return [
            [
                '1', [
                    'ay', 'bo', 'cgg', 'dz', 'id', 'ja', 'jbo', 'ka', 'kk', 'km', 'ko', 'ky']], [
                '2', [
                    'nl', 'fr', 'en', 'de', 'de_GE']], [
                        '3', [
                            'be', 'bs', 'cs', 'hr']], [
                                '4', [
                                    'cy', 'mt', 'sl']], [
                                        '5', []], [
                                            '6', ['ar']], ]

    def failing_langcodes(self):
        return [
            ['1', ['fa']],
            ['2', ['jbo']],
            ['3', ['cbs']],
            ['4', ['gd', 'kw']],
            ['5', ['ga']],
            ['6', []],
        ]

    def validate_matrix(self, nplural, matrix, expect_success=True):
        for lang_code, data in list(matrix.items()):
            indexes = set(data.values())
            if expect_success:
                self.assertEqual(
                    int(nplural),
                    len(indexes),
                    'Langcode "{0}" has "{1}" plural forms'.format(
                        lang_code,
                        nplural))
            else:
                self.assertNotEqual(
                    int(nplural),
                    len(indexes),
                    'Langcode "{0}" has "{1}" plural forms'.format(
                        lang_code,
                        nplural))

    def generate_test_data(self, plural, lang_codes):
        matrix = collections.defaultdict(lambda: {})
        for lang_code in lang_codes:
            for count in range(0, 201):
                plural = PluralizationRules.get(count, lang_code)
                matrix[lang_code][count] = plural

        return matrix

if __name__ == '__main__':
    unittest.main()
