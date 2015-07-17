# -*- coding: utf-8 -*-
"""
This file is a part of python_translate package
(c) Adam Zieliński <adam@symfony2.guru>

This file is derived from Symfony package.
(c) Fabien Potencier <fabien@symfony.com>

For the full copyright and license information, please view the LICENSE and LICENSE_SYMFONY_TRANSLATION
files that were distributed with this source code.
"""

import re
from decimal import Decimal
from collections import OrderedDict

INTERVAL_REGEX = re.compile("""
    ({\s*
        (\-?\d+(\.\d+)?[\s*,\s*\-?\d+(\.\d+)?]*)
    \s*})
        |
    (?P<left_delimiter>[\[\]])
        \s*
        (?P<left>-Inf|\-?\d+(\.\d+)?)
        \s*,\s*
        (?P<right>\+?Inf|\-?\d+(\.\d+)?)
        \s*
    (?P<right_delimiter>[\[\]])
""", re.X)

INTERVAL_MESSAGE_REGEX = re.compile("(?P<interval>{0})\s*(?P<message>.*?)$".format(INTERVAL_REGEX.pattern), re.X)
STANDARD_RULES_REGEX = re.compile("^\w+:\s*(.*?)$", re.X)

def test_interval(number, interval):
    """
     Tests if the given number is in the math interval.
     *
     @type number: int
        @param number: A number


     @type interval: str
        @param interval: An interval


     *
     @rtype: bool
     @raises: ValueError
    """
    interval = interval.strip()
    match = INTERVAL_REGEX.match(interval)
    if not match:
        raise ValueError('%s is not a valid interval', interval)
    if match.groups()[0]:
        for nb in match.groups()[1].split(","):
            if Decimal(nb.strip()) == Decimal(number):
                return True
    else:
        left_number = float(match.group('left'))
        right_number = float(match.group('right'))
        return (number >= left_number if '[' == match.group('left_delimiter') else number > left_number) \
           and (number <= right_number if ']' == match.group('right_delimiter') else number < right_number)

    return False


def select_message(message, number, locale):
    """
    Given a message with different plural translations separated by a
    pipe (|), this method returns the correct portion of the message based
    on the given number, locale and the pluralization rules in the message
    itself.

    The message supports two different types of pluralization rules:

    interval: {0} There are no apples|{1} There is one apple|]1,Inf] There are %count% apples
    indexed:  There is one apple|There are %count% apples

    The indexed solution can also contain labels (e.g. one: There is one apple).
    This is purely for making the translations more clear - it does not
    affect the functionality.

    The two methods can also be mixed:
        {0} There are no apples|one: There is one apple|more: There are %count% apples

    @type message: str
    @param message: The message being translated

    @type number: int
    @param number: The number of items represented for the message

    @type locale: st
    @param locale: The locale to use for choosing

    @rtype: str
    @raises: ValueError
    """
    parts = message.split("|")
    explicit_rules = OrderedDict()
    standard_rules = []
    for part in parts:
        part = part.strip()

        match_interval = INTERVAL_MESSAGE_REGEX.match(part)
        match_standard = STANDARD_RULES_REGEX.match(part)
        if match_interval:
            explicit_rules[match_interval.group('interval')] = match_interval.group('message')
        elif match_standard:
            standard_rules.append(match_standard.groups()[0])
        else:
            standard_rules.append(part)

    # try to match an explicit rule, then to the standard ones
    for interval, m in list(explicit_rules.items()):
        if test_interval(number, interval):
            return m

    position = PluralizationRules.get(number, locale)
    if len(standard_rules) <= position:
        # when there's exactly one rule given, and that rule is a standard
        # rule, use this rule
        if len(parts) == 1 and len(standard_rules) > 0:
            return standard_rules[0]
        raise ValueError('Unable to choose a translation for "%s" with locale "%s" for value "%s". '
                         'Double check that this translation has the correct plural options (e.g. '
                         '"There is one apple|There are {{count}} apples").' % (message, locale, number))

    return standard_rules[position]



class PluralizationRules(object):
    """
    Returns the plural rules for a given locale.

    Attributes:
        rules  list
    """

    # The plural rules are derived from code of the Zend Framework (2010-09-25),
    # which is subject to the new BSD license (http://framework.zend.com/license/new-bsd).
    # Copyright (c) 2005-2010 Zend Technologies USA Inc. (http://www.zend.com)
    _rules = {
        'bo': lambda number: 0,
        'dz': lambda number: 0,
        'id': lambda number: 0,
        'ja': lambda number: 0,
        'jv': lambda number: 0,
        'ka': lambda number: 0,
        'km': lambda number: 0,
        'kn': lambda number: 0,
        'ko': lambda number: 0,
        'ms': lambda number: 0,
        'th': lambda number: 0,
        'tr': lambda number: 0,
        'vi': lambda number: 0,
        'zh': lambda number: 0,
        'af': lambda number: 0 if number == 1 else 1,
        'az': lambda number: 0 if number == 1 else 1,
        'bn': lambda number: 0 if number == 1 else 1,
        'bg': lambda number: 0 if number == 1 else 1,
        'ca': lambda number: 0 if number == 1 else 1,
        'da': lambda number: 0 if number == 1 else 1,
        'de': lambda number: 0 if number == 1 else 1,
        'el': lambda number: 0 if number == 1 else 1,
        'en': lambda number: 0 if number == 1 else 1,
        'eo': lambda number: 0 if number == 1 else 1,
        'es': lambda number: 0 if number == 1 else 1,
        'et': lambda number: 0 if number == 1 else 1,
        'eu': lambda number: 0 if number == 1 else 1,
        'fa': lambda number: 0 if number == 1 else 1,
        'fi': lambda number: 0 if number == 1 else 1,
        'fo': lambda number: 0 if number == 1 else 1,
        'fur': lambda number: 0 if number == 1 else 1,
        'fy': lambda number: 0 if number == 1 else 1,
        'gl': lambda number: 0 if number == 1 else 1,
        'gu': lambda number: 0 if number == 1 else 1,
        'ha': lambda number: 0 if number == 1 else 1,
        'he': lambda number: 0 if number == 1 else 1,
        'hu': lambda number: 0 if number == 1 else 1,
        'is': lambda number: 0 if number == 1 else 1,
        'it': lambda number: 0 if number == 1 else 1,
        'ku': lambda number: 0 if number == 1 else 1,
        'lb': lambda number: 0 if number == 1 else 1,
        'ml': lambda number: 0 if number == 1 else 1,
        'mn': lambda number: 0 if number == 1 else 1,
        'mr': lambda number: 0 if number == 1 else 1,
        'nah': lambda number: 0 if number == 1 else 1,
        'nb': lambda number: 0 if number == 1 else 1,
        'ne': lambda number: 0 if number == 1 else 1,
        'nl': lambda number: 0 if number == 1 else 1,
        'nn': lambda number: 0 if number == 1 else 1,
        'no': lambda number: 0 if number == 1 else 1,
        'om': lambda number: 0 if number == 1 else 1,
        'or': lambda number: 0 if number == 1 else 1,
        'pa': lambda number: 0 if number == 1 else 1,
        'pap': lambda number: 0 if number == 1 else 1,
        'ps': lambda number: 0 if number == 1 else 1,
        'pt': lambda number: 0 if number == 1 else 1,
        'so': lambda number: 0 if number == 1 else 1,
        'sq': lambda number: 0 if number == 1 else 1,
        'sv': lambda number: 0 if number == 1 else 1,
        'sw': lambda number: 0 if number == 1 else 1,
        'ta': lambda number: 0 if number == 1 else 1,
        'te': lambda number: 0 if number == 1 else 1,
        'tk': lambda number: 0 if number == 1 else 1,
        'ur': lambda number: 0 if number == 1 else 1,
        'zu': lambda number: 0 if number == 1 else 1,
        'am': lambda number: 0 if number in (0, 1) else 1,
        'bh': lambda number: 0 if number in (0, 1) else 1,
        'fil': lambda number: 0 if number in (0, 1) else 1,
        'fr': lambda number: 0 if number in (0, 1) else 1,
        'gun': lambda number: 0 if number in (0, 1) else 1,
        'hi': lambda number: 0 if number in (0, 1) else 1,
        'ln': lambda number: 0 if number in (0, 1) else 1,
        'mg': lambda number: 0 if number in (0, 1) else 1,
        'nso': lambda number: 0 if number in (0, 1) else 1,
        'xbr': lambda number: 0 if number in (0, 1) else 1,
        'ti': lambda number: 0 if number in (0, 1) else 1,
        'wa': lambda number: 0 if number in (0, 1) else 1,
        'be': lambda number: 0 if number % 10 == 1 and number % 100 != 11 else (1 if ((number % 10 >= 2) and (number % 10 <= 4)) and ((number % 100 < 10) or (number % 100 >= 20)) else 2),
        'bs': lambda number: 0 if number % 10 == 1 and number % 100 != 11 else (1 if ((number % 10 >= 2) and (number % 10 <= 4)) and ((number % 100 < 10) or (number % 100 >= 20)) else 2),
        'hr': lambda number: 0 if number % 10 == 1 and number % 100 != 11 else (1 if ((number % 10 >= 2) and (number % 10 <= 4)) and ((number % 100 < 10) or (number % 100 >= 20)) else 2),
        'ru': lambda number: 0 if number % 10 == 1 and number % 100 != 11 else (1 if ((number % 10 >= 2) and (number % 10 <= 4)) and ((number % 100 < 10) or (number % 100 >= 20)) else 2),
        'sr': lambda number: 0 if number % 10 == 1 and number % 100 != 11 else (1 if ((number % 10 >= 2) and (number % 10 <= 4)) and ((number % 100 < 10) or (number % 100 >= 20)) else 2),
        'uk': lambda number: 0 if number % 10 == 1 and number % 100 != 11 else (1 if ((number % 10 >= 2) and (number % 10 <= 4)) and ((number % 100 < 10) or (number % 100 >= 20)) else 2),
        'cs': lambda number: 0 if number == 1 else (1 if 2 <= number <= 4 else 2),
        'sk': lambda number: 0 if number == 1 else (1 if 2 <= number <= 4 else 2),
        'ga': lambda number: 0 if number == 1 else (1 if number == 2 else 2),
        'lt': lambda number: 0 if (number % 10 == 1 and number % 100 != 11) else (1 if ((number % 10 >= 2 and number % 100 < 10) or number % 100 >= 20) else 2),
        'sl': lambda number: 0 if number % 100 == 1 else (1 if number % 100 == 2 else (2 if number % 100 in (3, 4) else 3)),
        'mk': lambda number: 0 if number % 10 == 1 else 1,
        'mt': lambda number: 0 if number == 1 else (1 if number == 0 or 1 < number % 100 < 11 else (2 if 10 < number % 100 < 20 else 3)),
        'lv': lambda number: 0 if number == 0 else (1 if number % 10 != 1 and number % 100 != 11 else 2),
        'pl': lambda number: 0 if number == 1 else (1 if (2 <= number % 10 <= 4) and (number % 100 < 12 or number % 100 > 14) else 2),
        'cy': lambda number: 0 if number == 1 else (1 if number == 2 else (2 if number in (8, 11) else 3)),
        'ro': lambda number: 0 if number == 1 else (1 if number == 0 or 0 < number % 100 < 20 else 2),
        'ar': lambda number: 0 if number == 0 else (1 if number == 1 else (2 if number == 2 else (3 if 3 <= number % 100 <= 10 else (4 if 11 <= number % 100 <= 99 else 5))))
    }

    @staticmethod
    def get(number, locale):
        """
        Returns the plural position to use for the given locale and number.

        @type number: int
        @param number: The number

        @type locale: str
        @param locale: The locale

        @rtype: int
        @return: The plural position
        """
        if locale == 'pt_BR':
            # temporary set a locale for brazilian
            locale = 'xbr'

        if len(locale) > 3:
            locale = locale.split("_")[0]

        rule = PluralizationRules._rules.get(locale, lambda _: 0)
        _return = rule(number)
        if not isinstance(_return, int) or _return < 0:
            return 0
        return _return

    @staticmethod
    def set(rule, locale):
        """
        Overrides the default plural rule for a given locale.

        @type rule: str
        @param rule: Callable

        @type locale: str
        @param locale: The locale

        @raises: ValueError
        """

        if locale == 'pt_BR':
            # temporary set a locale for brazilian
            locale = 'xbr'

        if len(locale) > 3:
            locale = locale.split("_")[0]

        if not hasattr(rule, '__call__'):
            raise ValueError('The given rule can not be called')

        PluralizationRules._rules[locale] = rule
