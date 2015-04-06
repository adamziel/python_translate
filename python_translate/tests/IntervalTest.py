# -*- coding: utf-8 -*-
"""
This file is a part of python_translate package
(c) Adam Zieliński <adam@symfony2.guru>

This file is derived from Symfony package.
(c) Fabien Potencier <fabien@symfony.com>

For the full copyright and license information, please view the LICENSE and LICENSE_SYMFONY_TRANSLATION
files that were distributed with this source code.
"""

import unittest

from python_translate.selector import test_interval


class IntervalTest(unittest.TestCase):

    def test_test(self):
        self.assertTrue(test_interval(3, '{1,2, 3 ,4}'))
        self.assertFalse(test_interval(10, '{1,2, 3 ,4}'))
        self.assertFalse(test_interval(3, '[1,2]'))
        self.assertTrue(test_interval(1, '[1,2]'))
        self.assertTrue(test_interval(2, '[1,2]'))
        self.assertFalse(test_interval(1, ']1,2['))
        self.assertFalse(test_interval(2, ']1,2['))
        self.assertTrue(test_interval(float('-Inf'), '[-Inf,2['))
        self.assertTrue(test_interval(float('+Inf'), '[-1,+Inf]'))

    def test_exception(self):
        self.assertRaises(ValueError, lambda: test_interval(1, 'foobar'))

if __name__ == '__main__':
    unittest.main()
