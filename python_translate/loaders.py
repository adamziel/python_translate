# -*- coding: utf-8 -*-
"""
This file is a part of python_translate package
(c) Adam Zieliński <adam@symfony2.guru>

This file is derived from Symfony package.
(c) Fabien Potencier <fabien@symfony.com>

For the full copyright and license information, please view the LICENSE and LICENSE_SYMFONY_TRANSLATION
files that were distributed with this source code.
"""


import sys
import os.path
import yaml
import json
import collections
import python_translate.translations

class NotFoundResourceException(Exception):
    pass


class InvalidResourceException(Exception):
    pass


class Loader(object):

    """
    Loader is the abstract class that all translation loaders are supposed to extend
    """

    def load(self, resource, locale, domain='messages'):
        """
        Loads a locale.

        @type resource: mixed
        @param resource: A resource

        @type locale: str
        @param locale: A locale

        @type domain: str
        @param domain: The domain

        @rtype: MessageCatalogue
        @return: A MessageCatalogue instance

        @raises: NotFoundResourceException when the resource cannot be found
        @raises: InvalidResourceException  when the resource cannot be loaded
        """
        raise NotImplementedError()


class FileMixin(object):

    """
    FileMixin is a class that has some helper methods for file-based loaders
    """

    def assert_valid_path(self, path):
        """
        Ensures that the path represents an existing file

        @type path: str
        @param path: path to check

        """
        if not isinstance(path, str):
            raise NotFoundResourceException(
                "Resource passed to load() method must be a file path")

        if not os.path.isfile(path):
            raise NotFoundResourceException(
                'File "{0}" does not exist'.format(path))

    def read_file(self, path):
        """
        Reads a file into memory and returns it's contents

        @type path: str
        @param path: path to load
        """

        self.assert_valid_path(path)

        with open(path, 'rb') as file:
            contents = file.read().decode('UTF-8')

        return contents

    def rethrow(self, msg, _type=InvalidResourceException):
        """
        Raises an exception with custom type and modified error message.
        Raised exception is based on current exc_info() and carries it's traceback

        @type msg: str
        @param msg: New error message

        @type _type: type
        @param _type: Reraised exception type

        @raises: Exception
        """
        exc_type, exc_value, exc_traceback = sys.exc_info()
        msg = msg + \
            "\nOriginal message: {0} {1}".format(exc_type.__name__, exc_value)
        raise _type(msg) #, None, exc_traceback


class DictLoader(Loader):

    """
    DictLoader loads translations from a python dict.
    """

    def load(self, resource, locale, domain='messages'):
        resource = self.flatten(resource)

        catalogue = python_translate.translations.MessageCatalogue(locale)
        catalogue.add(resource, domain)

        return catalogue

    def flatten(self, messages, parent_key=''):
        """
        Flattens an nested array of translations.

        The scheme used is:
          'key' => array('key2' => array('key3' => 'value'))
        Becomes:
          'key.key2.key3' => 'value'

        This function takes an array by reference and will modify it

        @type messages: dict
        @param messages: The dict that will be flattened

        @type parent_key: str
        @param parent_key: Current path being parsed, used internally for recursive calls
        """
        items = []
        sep = '.'
        for k, v in list(messages.items()):
            new_key = "{0}{1}{2}".format(parent_key, sep, k) if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(list(self.flatten(v, new_key).items()))
            else:
                items.append((new_key, v))
        return dict(items)


class YamlFileLoader(DictLoader, FileMixin):

    def load(self, resource, locale, domain='messages'):
        messages = yaml.safe_load(self.read_file(resource))
        if messages is None:
            messages = {}


        if not isinstance(messages, dict):
            raise InvalidResourceException(
                'The file passed to YamlLoader must be a YAML array')

        catalogue = super(YamlFileLoader, self).load(messages, locale, domain)
        catalogue.add_resource(resource)

        return catalogue

class DummyLoader(DictLoader, FileMixin):

    def load(self, resource, locale, domain='messages'):
        catalogue = python_translate.translations.MessageCatalogue(locale)
        catalogue.add({}, domain)
        catalogue.add_resource(resource)

        return catalogue


class JSONFileLoader(DictLoader, FileMixin):

    def load(self, resource, locale, domain='messages'):
        contents = self.read_file(resource)
        if contents == "":
            messages = None
        else:
            try:
                messages = json.loads(contents)
            except ValueError:
                self.rethrow(
                    "Invalid resource {0}".format(resource),
                    InvalidResourceException)

        if messages is None:
            messages = {}

        if not isinstance(messages, dict):
            raise InvalidResourceException(
                'The file passed to JSONLoader must be a JSON object')

        catalogue = super(JSONFileLoader, self).load(messages, locale, domain)
        catalogue.add_resource(resource)

        return catalogue


class PoFileLoader(DictLoader, FileMixin):

    def load(self, resource, locale, domain='messages'):
        messages = self.parse(resource)

        catalogue = super(PoFileLoader, self).load(messages, locale, domain)
        catalogue.add_resource(resource)

        return catalogue

    def parse(self, resource):
        """
        Loads given resource into a dict using polib

        @type resource: str
        @param resource: resource

        @rtype: list
        """
        try:
            import polib
        except ImportError as e:
            self.rethrow(
                "You need to install polib to use PoFileLoader or MoFileLoader",
                ImportError)

        self.assert_valid_path(resource)

        messages = {}
        parsed = self._load_contents(polib, resource)

        for item in parsed:
            if item.msgid_plural:
                plurals = sorted(item.msgstr_plural.items())
                if item.msgid and len(plurals) > 1:
                    messages[item.msgid] = plurals[0][1]
                plurals = [msgstr for idx, msgstr in plurals]
                messages[item.msgid_plural] = "|".join(plurals)
            elif item.msgid:
                messages[item.msgid] = item.msgstr

        return messages

    def _load_contents(self, polib, resource):
        """
        Parses portable object (PO) format using polib

        @type resource: str
        @param resource: resource

        @rtype: list
        """
        try:
            return polib.pofile(resource)
        except (ValueError, AttributeError) as e:
            self.rethrow(
                "Invalid resource {0}".format(resource),
                InvalidResourceException)


class MoFileLoader(PoFileLoader):

    def _load_contents(self, polib, resource):
        """
        Parses machine object (MO) format using polib

        @type resource: str
        @param resource: resource

        @rtype: list
        """
        import struct
        try:
            return polib.mofile(resource)
        except (ValueError, AttributeError, struct.error) as e:
            self.rethrow(
                "Invalid resource {0}".format(resource),
                InvalidResourceException)




















def getLevelName(level):
    """
    Return the textual representation of logging level 'level'.
    If the level is one of the predefined levels (CRITICAL, ERROR, WARNING,
    INFO, DEBUG) then you get the corresponding string. If you have
    associated levels with names using addLevelName then the name you have
    associated with 'level' is returned.
    If a numeric value corresponding to one of the defined levels is passed
    in, the corresponding string representation is returned.
    Otherwise, the string "Level %s" % level is returned.
    """
    # See Issues #22386, #27937 and #29220 for why it's this way
    result = _levelToName.get(level)
    if result is not None:
        return result
    result = _nameToLevel.get(level)
    if result is not None:
        return result
    return "Level %s" % level

def addLevelName(level, levelName):
    """
    Associate 'levelName' with 'level'.
    This is used when converting levels to text during message formatting.
    """
    _acquireLock()
    try:    #unlikely to cause an exception, but you never know...
        _levelToName[level] = levelName
        _nameToLevel[levelName] = level
    finally:
        _releaseLock()

#
# _srcfile is used when walking the stack to check when we've got the first
# caller stack frame, by skipping frames whose filename is that of this
# module's source. It therefore should contain the filename of this module's
# source file.
#
# Ordinarily we would use __file__ for this, but frozen modules don't always
# have __file__ set, for some reason (see Issue #21736). Thus, we get the
# filename from a handy code object from a function defined in this module.
# (There's no particular reason for picking addLevelName.)
#

# _srcfile is only used in conjunction with sys._getframe().
# To provide compatibility with older versions of Python, set _srcfile
# to None if _getframe() is not available; this value will prevent
# findCaller() from being called. You can also do this if you want to avoid
# the overhead of fetching caller information, even when _getframe() is
# available.
#if not hasattr(sys, '_getframe'):
#    _srcfile = None


def _checkLevel(level):
    if isinstance(level, int):
        rv = level
    elif str(level) == level:
        if level not in _nameToLevel:
            raise ValueError("Unknown level: %r" % level)
        rv = _nameToLevel[level]
    else:
        raise TypeError("Level not an integer or a valid string: %r" % level)
    return rv

#---------------------------------------------------------------------------
#   Thread-related stuff
#---------------------------------------------------------------------------

#
#_lock is used to serialize access to shared data structures in this module.
#This needs to be an RLock because fileConfig() creates and configures
#Handlers, and so might arbitrary user threads. Since Handler code updates the
#shared dictionary _handlers, it needs to acquire the lock. But if configuring,
#the lock would already have been acquired - so we need an RLock.
#The same argument applies to Loggers and Manager.loggerDict.
#

def _acquireLock():
    """
    Acquire the module-level lock for serializing access to shared data.
    This should be released with _releaseLock().
    """
    if _lock:
        _lock.acquire()

def _releaseLock():
    """
    Release the module-level lock acquired by calling _acquireLock().
    """
    if _lock:
        _lock.release()

#---------------------------------------------------------------------------
#   The logging record
#---------------------------------------------------------------------------

class LogRecord(object):
    """
    A LogRecord instance represents an event being logged.
    LogRecord instances are created every time something is logged. They
    contain all the information pertinent to the event being logged. The
    main information passed in is in msg and args, which are combined
    using str(msg) % args to create the message field of the record. The
    record also includes information such as when the record was created,
    the source line where the logging call was made, and any exception
    information to be logged.
    """
    def __init__(self, name, level, pathname, lineno,
                 msg, args, exc_info, func=None, sinfo=None, **kwargs):
        """
        Initialize a logging record with interesting information.
        """
        ct = time.time()
        self.name = name
        self.msg = msg
        #
        # The following statement allows passing of a dictionary as a sole
        # argument, so that you can do something like
        #  logging.debug("a %(a)d b %(b)s", {'a':1, 'b':2})
        # Suggested by Stefan Behnel.
        # Note that without the test for args[0], we get a problem because
        # during formatting, we test to see if the arg is present using
        # 'if self.args:'. If the event being logged is e.g. 'Value is %d'
        # and if the passed arg fails 'if self.args:' then no formatting
        # is done. For example, logger.warning('Value is %d', 0) would log
        # 'Value is %d' instead of 'Value is 0'.
        # For the use case of passing a dictionary, this should not be a
        # problem.
        # Issue #21172: a request was made to relax the isinstance check
        # to hasattr(args[0], '__getitem__'). However, the docs on string
        # formatting still seem to suggest a mapping object is required.
        # Thus, while not removing the isinstance check, it does now look
        # for collections.abc.Mapping rather than, as before, dict.
        if (args and len(args) == 1 and isinstance(args[0], collections.abc.Mapping)
            and args[0]):
            args = args[0]
        self.args = args
        self.levelname = getLevelName(level)
        self.levelno = level
        self.pathname = pathname
        try:
            self.filename = os.path.basename(pathname)
            self.module = os.path.splitext(self.filename)[0]
        except (TypeError, ValueError, AttributeError):
            self.filename = pathname
            self.module = "Unknown module"
        self.exc_info = exc_info
        self.exc_text = None      # used to cache the traceback text
        self.stack_info = sinfo
        self.lineno = lineno
        self.funcName = func
        self.created = ct
        self.msecs = (ct - int(ct)) * 1000
        self.relativeCreated = (self.created - _startTime) * 1000
        if logThreads:
            self.thread = threading.get_ident()
            self.threadName = threading.current_thread().name
        else: # pragma: no cover
            self.thread = None
            self.threadName = None
        if not logMultiprocessing: # pragma: no cover
            self.processName = None
        else:
            self.processName = 'MainProcess'
            mp = sys.modules.get('multiprocessing')
            if mp is not None:
                # Errors may occur if multiprocessing has not finished loading
                # yet - e.g. if a custom import hook causes third-party code
                # to run when multiprocessing calls import. See issue 8200
                # for an example
                try:
                    self.processName = mp.current_process().name
                except Exception: #pragma: no cover
                    pass
        if logProcesses and hasattr(os, 'getpid'):
            self.process = os.getpid()
        else:
            self.process = None

    def __str__(self):
        return '<LogRecord: %s, %s, %s, %s, "%s">'%(self.name, self.levelno,
            self.pathname, self.lineno, self.msg)

    __repr__ = __str__

    def getMessage(self):
        """
        Return the message for this LogRecord.
        Return the message for this LogRecord after merging any user-supplied
        arguments with the message.
        """
        msg = str(self.msg)
        if self.args:
            msg = msg % self.args
        return msg
