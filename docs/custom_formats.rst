.. index::
    single: Translation; Adding Custom Format Support

Adding Custom Format Support
============================

Sometimes, you need to deal with custom formats for translation files. The
Translation component is flexible enough to support this. Just create a
loader (to load translations) and, optionally, a dumper (to dump translations).

Imagine that you have a custom format where translation messages are defined
using one line for each translation and parentheses to wrap the key and the
message. A translation file would look like this:

.. code-block:: text

    (welcome)(accueil)
    (goodbye)(au revoir)
    (hello)(bonjour)

.. _components-translation-custom-loader:

Creating a Custom Loader
------------------------

To define a custom loader that is able to read these kinds of files, you must create a
new class that extends the
:class:`python_translate.loaders.Loader`. The
:method:`python_translate.loaders.Loader::load`
method will get a filename and parse it into an dict. Then, it will
create the catalog that will be returned::

    import re
    from python_translate.translations import MessageCatalogue
    from python_translate.loaders import Loader

    FORMAT_REGEX = re.compile("\(([^\)]+)\)\(([^\)]+)\)")
    
    class MyFormatLoader(Loader):

        def load(self, resource, locale, domain = 'messages'):
            messages = {}
            with open(resource, 'r') as f:
                lines = f.readlines()

            for line in lines:
                match = FORMAT_REGEX.match(line)
                if match:
                    messages[match.group(1)] = match.group(2)

            catalogue = MessageCatalogue(locale)
            catalogue.add(messages, domain)

            return catalogue

Once created, it can be used as any other loader::

    from python_translate.translations import Translator

    translator = Translator('fr_FR')
    translator.add_loader('my_format', MyFormatLoader())

    translator.add_resource('my_format', './translations/messages.txt', 'fr_FR')

    print translator.trans('welcome')

It will print *"accueil"*.

.. _components-translation-custom-dumper:

Creating a Custom Dumper
------------------------

It is also possible to create a custom dumper for your format, which is
useful when using the extraction commands. To do so, a new class
implementing the
:class:`python_translate.dumpers.Dumper`. The
must be created. To write the dump contents into a file, extending the
:class:`python_translate.dumpers.FileDumper` class
will save a few lines::

:method:`python_translate.dumpers.Dumper::load`

    from python_translate.translations import MessageCatalogue
    from python_translate.dumpers import FileDumper

    class MyFormatDumper(FileDumper):

        def format(self, messages, domain = 'messages'):
            output = ''

            for source, target in messages.all(domain).items():
                output += "({0})({1})\n".format(source, target)
                
            return output

        def get_extension(self):
            return 'txt'
    

The :method:`python_translate.dumpers.FileDumper::format`
method creates the output string, that will be used by the
:method:`python_translate.dumpers.Dumper::dump` method
of the FileDumper class to create the file. The dumper can be used like any other
built-in dumper. In the following example, the translation messages defined in the
YAML file are dumped into a text file with the custom format::

    from python_translate.loaders import YamlFileLoader

    loader = YamlFileLoader();
    catalogue = loader.load('./translations/messages.fr_FR.yml' , 'fr_FR')

    dumper = MyFormatDumper()
    dumper.dump(catalogue, {'path': './dumps'})
