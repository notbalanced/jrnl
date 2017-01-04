#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, unicode_literals
from . import Entry
from . import Journal
import codecs
import os
import fnmatch


class Folder(Journal.Journal):
    """A Journal handling multiple files in a folder"""

    def __init__(self, **kwargs):
        self.entries = []
        self._deleted_entries = []
        super(Folder, self).__init__(**kwargs)

    def open(self):
        filenames = []
        self.entries = []
        for root, dirnames, f in os.walk(self.config['journal']):
            for filename in fnmatch.filter(f, '*.txt'):
                filenames.append(os.path.join(root, filename))
        for filename in filenames:
            with codecs.open(filename, "r", "utf-8") as f:
                journal = f.read()
                self.entries.extend(self._parse(journal))
        self.sort()
        return self

    def write(self):
        """Writes only the entries that have been modified into proper files."""
        
        #Create a list of dates of modified entries
        modified_dates = []
        seen_dates = set()
        for e in self.entries:
            if e.modified:
                if e.date not in seen_dates:
                    modified_dates.append(e.date)
                    seen_dates.add(e.date)

        #For every date that had a modified entry, write to a file
        for d in modified_dates:
            write_entries=[]
            filename = os.path.join(self.config['journal'], d.strftime("%Y"), d.strftime("%m"), d.strftime("%d")+".txt")
            dirname = os.path.dirname(filename)
            #create directory if it doesn't exist
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            for e in self.entries:
                if e.date.year == d.year and e.date.month == d.month and e.date.day == d.day:
                    write_entries.append(e)
            journal = "\n".join([e.__unicode__() for e in write_entries])
            with codecs.open(filename, 'w', "utf-8") as journal_file:
                journal_file.write(journal)

    def parse_editable_str(self, edited):
        """Parses the output of self.editable_str and updates it's entries."""
        deleted_entry = False
        mod_entries = self._parse(edited)
        if len(mod_entries) != len(self.entries):
            deleted_entry = True
        print("mod {} total {}".format(len(mod_entries),len(self.entries)))
        # Match those entries that can be found in self.entries and set
        # these to modified, so we can get a count of how many entries got
        # modified and how many got deleted later.
        for entry in mod_entries:
            entry.modified = (not any(entry == old_entry for old_entry in self.entries)) or deleted_entry
        self.entries = mod_entries
