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
import tempfile

from python_translate.dumpers import YamlFileDumper
from python_translate.translations import MessageCatalogue

__DIR__ = os.path.dirname(os.path.abspath(__file__))


class FileDumperTest(unittest.TestCase):

    def testDump(self):
        catalogue = MessageCatalogue('en')
        catalogue.add({"foo": "bar"})

        tmp_dir = tempfile.gettempdir()
        dumper = YamlFileDumper()
        dumper.dump(catalogue, {"path": tmp_dir})

        with open(__DIR__ + '/../fixtures/resources.yml') as f1:
            with open(tmp_dir + '/messages.en.yml') as f2:
                a = f2.read()
                self.assertEqual(f1.read(), a)

        os.unlink(tmp_dir + '/messages.en.yml')

if __name__ == '__main__':
    unittest.main()
