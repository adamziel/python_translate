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

from python_translate.selector import select_message


class PluralizationRulesTest(unittest.TestCase):

    def testChoose(self):
        for expected, id, number in self.getChooseTests():
            self.assertEquals(expected, select_message(id, number, 'en'))

    def testReturnMessageIfExactlyOneStandardRuleIsGiven(self):
        self.assertEquals(
            'There are two apples',
            select_message(
                'There are two apples',
                2,
                'en'))

    def testThrowExceptionIfMatchingMessageCannotBeFound(self):
        for id, number in self.getNonMatchingMessages():
            self.assertRaises(
                ValueError,
                lambda: select_message(
                    id,
                    number,
                    'en'))

    def getNonMatchingMessages(self):
        return [
            ['{0} There are no apples|{1} There is one apple', 2],
            ['{1} There is one apple|]1,Inf] There are {count} apples', 0],
            ['{1} There is one apple|]2,Inf] There are {count} apples', 2],
            ['{0} There are no apples|There is one apple', 2],
        ]

    def getChooseTests(self):
        return [
            ['There are no apples',
             '{0} There are no apples|{1} There is one apple|]1,Inf] There are {count} apples',
             0],
            ['There are no apples',
             '{0}     There are no apples|{1} There is one apple|]1,Inf] There are {count} apples',
             0],
            ['There are no apples',
             '{0}There are no apples|{1} There is one apple|]1,Inf] There are {count} apples',
             0],

            ['There is one apple',
             '{0} There are no apples|{1} There is one apple|]1,Inf] There are {count} apples',
             1],

            [
                'There are {count} apples',
                '{0} There are no apples|{1} There is one apple|]1,Inf] There are {count} apples',
                10],
            [
                'There are {count} apples',
                '{0} There are no apples|{1} There is one apple|]1,Inf]There are {count} apples',
                10],
            [
                'There are {count} apples',
                '{0} There are no apples|{1} There is one apple|]1,Inf]     There are {count} apples',
                10],

            ['There are {count} apples',
             'There is one apple|There are {count} apples',
             0],
            ['There is one apple',
             'There is one apple|There are {count} apples',
             1],
            ['There are {count} apples',
             'There is one apple|There are {count} apples',
             10],

            ['There are {count} apples',
             'one: There is one apple|more: There are {count} apples',
             0],
            ['There is one apple',
             'one: There is one apple|more: There are {count} apples',
             1],
            ['There are {count} apples',
             'one: There is one apple|more: There are {count} apples',
             10],

            ['There are no apples',
             '{0} There are no apples|one: There is one apple|more: There are {count} apples',
             0],
            ['There is one apple',
             '{0} There are no apples|one: There is one apple|more: There are {count} apples',
             1],
            [
                'There are {count} apples',
                '{0} There are no apples|one: There is one apple|more: There are {count} apples',
                10],

            ['',
             '{0}|{1} There is one apple|]1,Inf] There are {count} apples',
             0],
            ['',
             '{0} There are no apples|{1}|]1,Inf] There are {count} apples',
             1],

            # Indexed only tests which are Gettext PoFile* compatible strings.
            ['There are {count} apples',
             'There is one apple|There are {count} apples',
             0],
            ['There is one apple',
             'There is one apple|There are {count} apples',
             1],
            ['There are {count} apples',
             'There is one apple|There are {count} apples',
             2],

            # Tests for float numbers
            ['There is almost one apple',
             '{0} There are no apples|]0,1[ There is almost one apple|{1} There is one apple|[1,Inf] There is more than one apple',
             0.7],
            ['There is one apple',
             '{0} There are no apples|]0,1[There are {count} apples|{1} There is one apple|[1,Inf] There is more than one apple',
             1],
            ['There is more than one apple',
             '{0} There are no apples|]0,1[There are {count} apples|{1} There is one apple|[1,Inf] There is more than one apple',
             1.7],
            ['There are no apples',
             '{0} There are no apples|]0,1[There are {count} apples|{1} There is one apple|[1,Inf] There is more than one apple',
             0],
            ['There are no apples',
             '{0.0} There are no apples|]0,1[There are {count} apples|{1} There is one apple|[1,Inf] There is more than one apple',
             0],
        ]


if __name__ == '__main__':
    unittest.main()
