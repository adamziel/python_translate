# -*- coding: utf-8 -*-
"""
This file is a part of python_translate package
(c) Adam Zieliński <adam@symfony2.guru>

For the full copyright and license information, please view the LICENSE and LICENSE_SYMFONY_TRANSLATION
files that were distributed with this source code.
"""

import ast
import codegen
from python_translate.extractors.base import Translation, TransVar, ExtensionBasedExtractor


class PythonExtractor(ExtensionBasedExtractor):

    def __init__(
            self,
            file_extensions=None,
            tranz_functions=None,
            tranzchoice_functions=None):
        file_extensions = file_extensions if file_extensions is not None else (
            "*.py",
        )

        self.tranz_functions = tranz_functions if tranz_functions is not None else (
            '_',
            'tranz')
        self.tranzchoice_functions = tranzchoice_functions if tranzchoice_functions is not None else (
            'tranzchoice',
        )
        super(PythonExtractor, self).__init__(file_extensions=file_extensions)

    def extract_translations(self, string):
        """Extract messages from Python string."""

        tree = ast.parse(string)
        # ast_visit(tree)
        visitor = TransVisitor(
            self.tranz_functions,
            self.tranzchoice_functions)
        visitor.visit(tree)

        return visitor.translations


class TransVisitor(ast.NodeVisitor):

    def __init__(self, tranz_functions, tranzchoice_functions):
        self.tranz_functions = tranz_functions
        self.tranzchoice_functions = tranzchoice_functions

        self.translations = []
        super(TransVisitor, self).__init__()

    def visit(self, node):
        if isinstance(node, ast.Call):
            self.process_node(node)
        return self.generic_visit(node)

    def process_node(self, node):
        func_name = self.get_func_name(node.func)

        if func_name not in self.tranz_functions + self.tranzchoice_functions:
            return

        kwargs = {}

        # Arguments
        kwargs['id'] = self.prepare_arg(
            node.args[0]) if len(
            node.args) > 0 else None
        idx = 1
        if func_name in self.tranzchoice_functions:
            kwargs['number'] = self.prepare_arg(
                node.args[1]) if len(
                node.args) > 1 else None
            idx += 1

        kwargs['parameters'] = self.parse_kwargs(
            node.args[idx]) if len(
            node.args) > idx else None
            
            
        kwargs['domain'] = self.prepare_arg(
            node.args[idx + 1]) if len(node.args) > idx + 1 else None
        kwargs['locale'] = self.prepare_arg(
            node.args[idx + 2]) if len(node.args) > idx + 2 else None

        # Keyword arguments
        if node.keywords:
            for keyword in node.keywords:
                if keyword.arg == "id" and not kwargs['id']:
                    kwargs['id'] = self.prepare_arg(keyword.value)

                if keyword.arg == "number" and not kwargs['number']:
                    kwargs['number'] = self.prepare_arg(keyword.value)

                if keyword.arg == "domain" and not kwargs['domain']:
                    kwargs['domain'] = self.prepare_arg(keyword.value)

                if keyword.arg == 'parameters':
                    kwargs['parameters'] = self.parse_kwargs(keyword.value)

                if keyword.arg == 'locale':
                    kwargs['locale'] = self.parse_kwargs(keyword.value)

        # Splats
        if node.starargs or node.kwargs:
            _id = "*" + node.starargs.id if node.starargs else "**" + \
                node.kwargs.id
            if not kwargs['number']:
                kwargs['number'] = TransVar(_id, TransVar.VARNAME)

            if not kwargs['id']:
                kwargs['id'] = TransVar(_id, TransVar.VARNAME)

            if not kwargs['domain']:
                kwargs['domain'] = TransVar(_id, TransVar.VARNAME)

            if not kwargs['locale']:
                kwargs['locale'] = TransVar(_id, TransVar.VARNAME)

            if not kwargs['parameters']:
                kwargs['parameters'] = self.parse_kwargs(kwargs['parameters'])

        fixed = ast.fix_missing_locations(node)
        kwargs.update({
            "is_transchoice": func_name in self.tranzchoice_functions,
            "lineno": fixed.lineno,
            "column": fixed.col_offset,
        })
        self.translations.append(Translation(**kwargs))

    def parse_kwargs(self, Dict):
        if not isinstance(Dict, ast.Dict):
            return self.expr_to_source(Dict)

        parameters = []
        for k in Dict.keys:
            if isinstance(k, ast.Str):
                parameters.append(k.s)
            else:
                return self.expr_to_source(Dict)

        return TransVar(parameters, TransVar.LITERAL)

    def expr_to_source(self, expr):
        try:
            src = codegen.to_source(expr)
        except Exception as e:
            src = "-unknown-"
        return TransVar(src, TransVar.UNKNOWN)

    def prepare_arg(self, value):
        if value is None:
            return None

        if isinstance(value, ast.Str):
            return TransVar(value.s, TransVar.LITERAL)

        if isinstance(value, ast.Num):
            return TransVar(value.n, TransVar.LITERAL)

        if isinstance(value, ast.Attribute):
            return TransVar(
                value.attr if isinstance(
                    value.attr,
                    str) else value.attr.id,
                TransVar.VARNAME)

        if isinstance(value, ast.Call):
            return TransVar(self.get_func_name(value), TransVar.VARNAME)

        return TransVar(None, TransVar.UNKNOWN)

    def get_func_name(self, func):
        if isinstance(func, ast.Attribute):
            return self.get_attr_name(func.attr)
        elif isinstance(func, ast.Name):
            return func.id
        else:
            return None
            # lambda or so
            raise ValueError('Unexpected type of Call node')

    def get_attr_name(self, attr):
        return attr if isinstance(attr, str) else attr.id
