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
    for k, v in _update.items():
        if isinstance(v, collections.Mapping):
            r = recursive_update(_dict.get(k, {}), v)
            _dict[k] = r
        else:
            _dict[k] = _update[k]
    return _dict




# CaseInsensitiveDict is derived from code of the requests library (2015-04-20),
# which is subject to the Apache license.
#
# Copyright 2013 Kenneth Reitz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class CaseInsensitiveDict(collections.MutableMapping):
    """
    A case-insensitive ``dict``-like object.
    Implements all methods and operations of
    ``collections.MutableMapping`` as well as dict's ``copy``. Also
    provides ``lower_items``.
    All keys are expected to be strings. The structure remembers the
    case of the last key to be set, and ``iter(instance)``,
    ``keys()``, ``items()``, ``iterkeys()``, and ``iteritems()``
    will contain case-sensitive keys. However, querying and contains
    testing is case insensitive:
        cid = CaseInsensitiveDict()
        cid['Accept'] = 'application/json'
        cid['aCCEPT'] == 'application/json'  # True
        list(cid) == ['Accept']  # True
    For example, ``headers['content-encoding']`` will return the
    value of a ``'Content-Encoding'`` response header, regardless
    of how the header name was originally stored.
    If the constructor, ``.update``, or equality comparison
    operations are given keys that have equal ``.lower()``s, the
    behavior is undefined.
    """
    def __init__(self, data=None, **kwargs):
        self._store = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        # Use the lowercased key for lookups, but store the actual
        # key alongside the value.
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in list(self._store.values()))

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return (
            (lowerkey, keyval[1])
            for (lowerkey, keyval)
            in list(self._store.items())
        )

    def __eq__(self, other):
        if isinstance(other, collections.Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self):
         return CaseInsensitiveDict(list(self._store.values()))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, dict(list(self.items())))
