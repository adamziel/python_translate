python_translate
=====================
[![Build Status](https://travis-ci.org/adamziel/python_translate.svg?branch=master)](https://travis-ci.org/adamziel/python_translate)


Documentation
=====================

Documentation is available in here:
https://python-translate.readthedocs.org/en/latest/


Overview
=====================

Most python translation tools are based on gettext. I don't like gettext so
I took an excellent Symfony Translation Component and I ported it to python:
https://github.com/symfony/Translation

Even though there is no dependency on gettext, you may actually use this
project to work with *.po and *.mo files! Never compile anything again!


Translation Component
=====================

Translation provides tools for loading translation files and generating
translated strings from these including support for pluralization.

```python
# -*- coding: utf-8 -*-

from python_translate.translations import Translator
from python_translate.loaders import DictLoader

translator = Translator('fr_FR');
translator.set_fallback_locales(['fr']);
translator.add_loader('dict', DictLoader());
translator.add_resource('dict', {
    'Hello World!': 'Bonjour',
}, 'fr')

print translator.trans('Hello World!');
```


Contributing
============

See [CONTRIBUTING.md](https://github.com/adamziel/python_translate/tree/master/CONTRIBUTING.md)


License
=======

The code is derived from the Symfony Translation component:
(c) Fabien Potencier <fabien@symfony.com>
https://github.com/symfony/symfony
For the full copyright and license information, please view the LICENSE and LICENSE_SYMFONY_TRANSLATION

The documentation and README are derived from the Symfony Documentation:
https://github.com/symfony/symfony-docs
http://symfony.com
The documentation and README are licensed under https://creativecommons.org/licenses/by-sa/3.0/



