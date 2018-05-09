#!/usr/bin/env python3

import re
import magic
from os import listdir
from os.path import isfile
from subprocess import call, PIPE, check_output
from sys import argv
from collections import defaultdict
from itertools import chain
import textblob

class Verifier(object):

    def __init__(self, dir_path, expression):
        self.dir_path = dir_path
        self.dir_files = [i for i in listdir(dir_path)
                          if isfile(dir_path + i)]
        self.expression = expression.lower()

    def get_content(self, file_path):
        file_type = magic.from_file(file_path, mime=True).split('/')[1]
        if file_type == 'pdf':
            return self.open_pdf(file_path)
        elif file_type == 'html':
            return self.open_html(file_path)
        elif file_type == 'plain':
            with open(file_path) as f:
                return f.read().lower()
        else:
            raise AttributeError('%s file type not supported' % file_path)

    def open_pdf(self, file_path):
        output = check_output(['pdftotext', file_path, '-'], PIPE)
        return output.decode('utf8').lower()

    def open_html(self, file_path):
        output = check_output(['html2text', '-utf8', file_path], PIPE)
        return output.decode('utf8').lower()

    def gen_items(self):
        for i in self.dir_files:
            try:
                yield (i, self.get_content(self.dir_path + i))
            except AttributeError as e:
                print(e)
                continue

    def check_expression(self, input_string):
        variants = list()
        expression_list = self.expression.lower().split(' ')
        if re.match('dos?|das?', expression_list[-2]):
            first_names = ' '.join(expression_list[:-2])
            last_name = ' '.join(expression_list[-2:])
        else:
            first_names = ' '.join(expression_list[:-1])
            last_name = expression_list[-1]
        abrv_first_names = '. '.join([i[0] for i in first_names.split(' ')]) + '.'
        expr1 = "%s, %s" % (last_name, first_names)
        expr2 = "%s, %s" % (last_name, abrv_first_names)
        reexpr1 = re.compile(expr1)
        reexpr2 = re.compile(expr2)
        reexpr3 = re.compile(self.expression)
        occurences1 = reexpr1.finditer(input_string)
        occurences2 = reexpr2.finditer(input_string)
        occurences3 = reexpr3.finditer(input_string)
        return chain(occurences1, occurences2, occurences3)

    def get_occurences_qt(self):
        occurence_list = list()
        for file_name, content in self.gen_items():
            item_occurences = [i.group()
                               for i in self.check_expression(content)]
            yield (file_name, len(item_occurences))

    def get_context(self, context_limits=200):
        occurence_list = list()
        for file_name, content in self.gen_items():
            item_context = list()
            for i in self.check_expression(content):
                a, b = i.span()
                context = content[a - context_limits: b + context_limits]
                item_context.append(context)
            yield (file_name, item_context)

if __name__ == '__main__':
    ver = Verifier(argv[1], argv[2])
    for file_name, occurences in ver.get_occurences_qt():
        if occurences:
            print('file %s had %d of the name %s in the document' % (file_name, occurences, argv[2]))
