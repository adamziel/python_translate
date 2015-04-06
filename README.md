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


