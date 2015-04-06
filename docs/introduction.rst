.. index::
    single: Translation
    single: Components; Translation

Introduction
=========================

    python_translate provides tools to internationalize your
    application.

Installation
------------

You can install the component in 2 different ways:

* Install it via pip (``pip install python_translate``)
* Use the official Git repository (https://github.com/adamziel/python_translate).

Constructing the Translator
---------------------------

The main access point of the Translation component is
`python_translate.translations.Translator`. Before you can use it,
you need to configure it and load the messages to translate (called *message
catalogs*).

Configuration
~~~~~~~~~~~~~

The constructor of the ``Translator`` class needs one argument: The locale.

.. code-block:: python

    from python_translate.translations import Translator

    translator = Translator('fr_FR')

.. note::

    The locale set here is the default locale to use. You can override this
    locale when translating strings.

.. note::

    The term *locale* refers roughly to the user's language and country. It
    can be any string that your application uses to manage translations and
    other format differences (e.g. currency format). The `ISO 639-1`_
    *language* code, an underscore (``_``), then the `ISO 3166-1 alpha-2`_
    *country* code (e.g. ``fr_FR`` for French/France) is recommended.

.. _component-translator-message-catalogs:

Loading Message Catalogs
~~~~~~~~~~~~~~~~~~~~~~~~

The messages are stored in message catalogs inside the ``Translator``
class. A message catalog is like a dictionary of translations for a specific
locale.

python_translate uses Loader classes to load catalogs. You can load
multiple resources for the same locale, which will then be combined into one
catalog.

The component comes with some default Loaders and you can create your own
Loader too. The default loaders are:

* `python_translate.loaders.DictLoader` - to load
  catalogs from Python dictionaries.
* `python_translate.loaders.JsonFileLoader` - to load
  catalogs from JSON files.
* `python_translate.loaders.YamlFileLoader` - to load
  catalogs from Yaml files (requires ``pyyaml``).
* `python_translate.loaders.MoFileLoader` - to load
  catalogs from gettext files (requires ``polib``).
* `python_translate.loaders.PoFileLoader` - to load
  catalogs from gettext files (requires ``polib``).

You can also :doc:`create your own Loader </components/translation/custom_formats>`,
in case the format is not already supported by one of the default loaders.

At first, you should add one or more loaders to the ``Translator``::

    # ...
    translator.add_loader('dict', DictLoader())

The first argument is the name to which you can refer the loader in the
translator and the second argument is an instance of the loader itself. After
this, you can add your resources using the correct loader.

Loading Messages with the ``ArrayLoader``
.........................................

Loading messages can be done by calling
`python_translate.translation.Translator::add_resource`. The first
argument is the loader name (this was the first argument of the ``add_loader``
method), the second is the resource and the third argument is the locale::

    # ...
    translator.add_resource('dict', {
        'Hello World!': 'Bonjour',
    }, 'fr_FR')

Loading Messages with the File Loaders
......................................

If you use one of the file loaders, you should also use the ``add_resource``
method. The only difference is that you should put the file name to the resource
file as the second argument, instead of an array::

    # ...
    translator.add_loader('yaml', YamlFileLoader())
    translator.add_resource('yaml', 'path/to/messages.fr.yml', 'fr_FR')

The Translation Process
-----------------------

To actually translate the message, the Translator uses a simple process:

* A catalog of translated messages is loaded from translation resources defined
  for the ``locale`` (e.g. ``fr_FR``). Messages from the
  :ref:`components-fallback-locales` are also loaded and added to the
  catalog, if they don't already exist. The end result is a large "dictionary"
  of translations

* If the message is located in the catalog, the translation is returned. If
  not, the translator returns the original message.

You start this process by calling
`python_translate.translation.Translator::trans` or
`python_translate.translation.Translator::transchoice`. Then, the
Translator looks for the exact string inside the appropriate message catalog
and returns it (if it exists).

.. _components-fallback-locales:

Fallback Locales
~~~~~~~~~~~~~~~~

If the message is not located in the catalog of the specific locale, the
translator will look into the catalog of one or more fallback locales. For
example, assume you're trying to translate into the ``fr_FR`` locale:

#. First, the translator looks for the translation in the ``fr_FR`` locale;

#. If it wasn't found, the translator looks for the translation in the ``fr``
   locale;

#. If the translation still isn't found, the translator uses the one or more
   fallback locales set explicitly on the translator.

For (3), the fallback locales can be set by calling
`python_translate.translation.Translator::set_fallback_locales`::

    # ...
    translator.set_fallback_locales(['en'])

.. _using-message-domains:

Using Message Domains
---------------------

As you've seen, message files are organized into the different locales that
they translate. The message files can also be organized further into "domains".

The domain is specified in the fourth argument of the ``add_resource()``
method. The default domain is ``messages``. For example, suppose that, for
organization, translations were split into three different domains:
``messages``, ``admin`` and ``navigation``. The French translation would be
loaded like this::

    // ...
    translator.add_loader('yml', YamlLoader())

    translator.add_resource('yml', 'messages.fr.yml', 'fr_FR')
    translator.add_resource('yml', 'admin.fr.yml', 'fr_FR', 'admin')
    translator.add_resource('yml', 'navigation.fr.yml', 'fr_FR', 'navigation')

When translating strings that are not in the default domain (``messages``),
you must specify the domain as the third argument of ``trans()``::

    translator.trans('Symfony is great', {}, 'admin')

Symfony will now look for the message in the ``admin`` domain of the
specified locale.

Usage
-----

Read how to use the Translation component in :doc:`usage`.

.. _`ISO 3166-1 alpha-2`: http://en.wikipedia.org/wiki/ISO_3166-1#Current_codes
.. _`ISO 639-1`: http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes