#!/usr/bin/env python3
# coding: utf-8
from __future__ import print_function, absolute_import
import os.path as path
from collections import defaultdict
from logging import getLogger as get_logger
from dotapatch.model import Html
from dotapatch.data import HeropediaData


class Dotapatch (object):

    ERROR = -1
    SUCCESS = 0
    WARNING = 1

    def __init__(self, filename, template='default'):
        self.logger = get_logger('dotapatch.patch')
        self._file_path = path.abspath(filename)
        self._template = template

        if not path.isfile(self._file_path):
            error_title = '{} not found'.format(self._file_path)
            error_body = '''
In case {name} is in a directory other than
{path} try:

 1) 'cd' over to the correct directory
 2) run dotapatch again
 e.g.
     $ cd /whole/path/to/file/
     $ dotapatch {name}

 or

 1) run dotapatch specifying the /whole/path/to/file/{name}
 e.g.
     $ dotapatch /whole/path/to/file/{name}

Contact me at @arthurazs if the error persists.
            '''.format(
                path=path.dirname(self._file_path),
                name=path.basename(self._file_path))
            self.logger.error(error_title)
            self.logger.warning(error_body)

    def parse(self):
        status = Dotapatch.ERROR
        if path.isfile(self._file_path):
            with open(self._file_path, 'r') as changelog:
                # read changelog
                lines = []
                for line in changelog:
                    line = line.replace('* ', '').rstrip()
                    if line:
                        lines.append(line)

                patch_version = lines[0][:-1]
                patch_name = patch_version.replace('.', '')
                lines = lines[2:]
                initialLineCount = len(lines)

            data = HeropediaData()

            # Organize changelog
            item = defaultdict(list)
            hero = defaultdict(list)

            for line in lines[:]:
                found_hero = data.get_hero_name(line)

                # Remove hero/item name, capitalize the line
                formatted_line = ' '.join(line.split(': ')[1:])
                formatted_line = formatted_line.capitalize()

                if found_hero:
                    hero[found_hero].append(formatted_line)
                    lines.remove(line)
                else:
                    found_item = data.get_item_name(line)
                    if found_item:
                        item[found_item].append(formatted_line)
                        lines.remove(line)

            # Generate .html
            # TODO use path.join here?
            with open(patch_name + '.html', 'w') as text:
                model = Html(patch_version, self._template)
                model.add_general(lines)
                model.add_items(item)
                model.add_heroes(hero)
                model.close()
                print(model.get_content(), file=text)
                self.logger.info(
                    'HTML saved at {}.html'
                    .format(path.abspath(patch_name)))

            # Feedback
            currentLineCount = sum(len(changes) for changes in hero.values()) \
                + sum(len(changes) for changes in item.values())
            status = initialLineCount - currentLineCount
            if (status == 0):
                self.logger.info('Conversion went smoothly.')
            elif (status < 0):
                self.logger.critical('Contact me at @arthurazs')
            else:
                if (status == 1):
                    message = '''1 line under GENERAL updates:
* {}

This line might be a hero/item update and you should manually place it
at the proper location.'''.format(''.join(lines))
                    self.logger.warning(message)
                else:
                    message = '{} lines under GENERAL updates:' \
                        .format(str(status))
                    for line in lines:
                        message = ('{}\n* {}'.format(message, line))
                    message = '''{}

Some of these lines might be hero/item updates and you should manually
place them at the proper location.'''.format(message)
                    self.logger.warning(message)
        return status
