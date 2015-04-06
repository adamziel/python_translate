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
import fnmatch
import collections


def find_files(path, patterns):
    """
    Returns all files from a given path that matches the pattern or list
    of patterns

    @type path: str
    @param path: A path to traverse

    @typ patterns: str|list
    @param patterns: A pattern or a list of patterns to match

    @rtype: list[str]:
    @return: A list of matched files
    """
    if not isinstance(patterns, (list, tuple)):
        patterns = [patterns]

    matches = []
    for root, dirnames, filenames in os.walk(path):
        for pattern in patterns:
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))
    return matches


def recursive_update(_dict, _update):
    """
    Same as dict.update, but updates also nested dicts instead of
    overriding then

    @type _dict: A
    @param _dict: dict to apply update to

    @type _update: A
    @param _update: dict to pick update data from

    @return:
    """
    for k, v in _update.iteritems():
        if isinstance(v, collections.Mapping):
            r = recursive_update(_dict.get(k, {}), v)
            _dict[k] = r
        else:
            _dict[k] = _update[k]
    return _dict
