# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 22:49:07 2019

@author: NishantParmar
"""
from functools import reduce
import errno
import os
import PyPDF2
import re

source_dir = "file_path"
source_file = "filename.pdf"
src_file = os.path.join(source_dir, source_file)
#base_ptrn = "(.*)(\w+[\)][A-Z])+(.*)"
base_ptrn = "(.*)(\w+[\(\w+\)]*[\*A-Z0-9])+(.*)"
flags = {"upper": False, "digit": False}


def recursive_split(base_string, prev_suffix=""):
    match_ = re.match(base_ptrn, base_string)
    if match_:
        groups_ = list(match_.groups())
        group_ = groups_[1]
        char_split = re.split("\w+", group_)
        new_char = reduce(lambda x, y: x+y, char_split)
        write_output("new_char = [{}]".format(new_char))
        write_output("group = [{}]".format(group_))
        replacement_ = "{}" if str.isdigit(group_.strip()) else "{} "
        if (not str.isupper(group_) or new_char or (
                str.isupper(group_) and not flags["upper"])):
            group_ = group_.replace(new_char, replacement_.format(
                new_char)).strip()
            if str.isdigit(group_.strip()) and not flags["digit"]:
                group_ = " {}".format(group_)
        write_output("new_group = {}".format(group_))
        
        new_base = groups_[0]
        new_suffix = group_ + groups_[2] + prev_suffix
        write_output("[{},{}]\n".format(new_base, new_suffix))
        if new_base != "":
            flags["upper"] = True if str.isupper(group_) else False
            flags["digit"] = True if str.isdigit(group_.strip()[0]) else False
            recursive_split(new_base, new_suffix)
    else:
        write_output("Final string:\n{}".format(base_string + prev_suffix))


def parse_text(text, page_count):
    begin = "Town/CityCountyTier & RatingOrganisation NameSub Tier"
    end_p = "Page \d of {totalPages}".format(totalPages=page_count)
    ptrn_ = ".*{}(.*){}".format(begin, end_p)
    match_begin = re.match(ptrn_, text)
    if match_begin:
        match_groups = match_begin.groups()
        table_contents = match_groups[0]
        table_contents = re.subn("[\@\[\]\?\!]+", " * ", table_contents)
        return table_contents[0]
    return None


def write_output(page_body, index=None, page_count=None):
    logs_directory = os.path.join(os.getcwd(), "Output")
    if not os.path.exists(logs_directory):
        try:
            os.makedirs(logs_directory)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    logs_filename = "logs.txt"#.format(index=index)
    logs_file = os.path.join(logs_directory, logs_filename)
    write_mode = "w" if not os.path.exists(logs_file) else "a"
    with open(logs_file, write_mode, encoding="UTF-8") as log_file:
        log_file.write("\n{}".format(page_body))


def parse_file():
    with open(src_file, "rb") as pdf:
        file_obj = PyPDF2.PdfFileReader(pdf)
        print(file_obj.numPages)
        page_count = file_obj.numPages
        collection = list()
        for i in range(2):
            page_obj = file_obj.getPage(i)
            info_ = parse_text(page_obj.extractText(), page_count)
            collection.append(info_)
        return collection
