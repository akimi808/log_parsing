#!/usr/bin/env python
import os
import re
from datetime import datetime, timedelta
import argparse

DELTA_RE = re.compile('^(?:(?P<days>\d*)d)?(?:(?P<hours>\d*)h)?(?:(?P<minutes>\d*)m)?(?:(?P<seconds>\d*)s)?$')


def logtail(log_file, seek_date, regexp, date_format):
    log_file.seek(0, os.SEEK_END)
    last_byte = log_file.tell() - 1
    if last_byte == 0:
        return ""
    first_byte = 0
    sample_date = turn_to_date(seek_date, date_format)
    compiled_re = re.compile(regexp)
    while last_byte >= first_byte:
        middle_byte = (last_byte + first_byte) // 2
        str_start = search_eol_left(log_file, middle_byte)
        str_end = search_eol_right(log_file, last_byte, middle_byte)
        log_file.seek(str_start)
        string = log_file.read(str_end - str_start)
        if compare_to_sample_date(string, sample_date, compiled_re, date_format) == 1:
            first_byte = str_end + 1
        else:
            last_byte = str_start - 1
    log_file.seek(last_byte + 1)
    bytes = log_file.read(4096)
    yield bytes
    while bytes:
        bytes = log_file.read(4096)
        yield bytes


def search_eol_left(log_file, middle_byte):
    start = middle_byte
    log_file.seek(start)
    char = log_file.read(1)
    if char == "\n":
        start = start - 1
        log_file.seek(start)
        char = log_file.read(1)
    while char != "\n" and start != 0:
        start = start - 1
        log_file.seek(start)
        char = log_file.read(1)
    return start if start == 0 else start + 1


def search_eol_right(log_file, last_byte, middle_byte):
    end = middle_byte
    log_file.seek(end)
    char = log_file.read(1)
    while char != "\n" and end != last_byte:
        end = end + 1
        log_file.seek(end)
        char = log_file.read(1)
    return end


def parse_str(str, regexp):
    if not str:
        return ""
    #m = re.match(r'^[^\[]*\[([^\]]*)', str)
    m = regexp.match(str)
    str = m.group(1)
    return str.strip()


def turn_to_date(seek_date, date_format):
    m = DELTA_RE.match(seek_date)
    if m:
        parts = m.groupdict()
        delta = timedelta(days=int(parts.get('days') or 0),
                          hours=int(parts.get('hours') or 0),
                          minutes=int(parts.get('minutes') or 0),
                          seconds=int(parts.get('seconds') or 0))
        return datetime.now() - delta
    try:
        n = datetime.strptime(seek_date, date_format)
        return n
    except TypeError:
        print("Not a date")
        exit(1)


def compare_to_sample_date(log_line, sample_date, regexp, date_format):
    date_str = parse_str(log_line, regexp)
    date = datetime.strptime(date_str, date_format)
    if date.year == 1900:
        date.replace(year=datetime.now().year)
    return 1 if date < sample_date else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse date and print lines with this date and later from the log file')
    parser.add_argument('filename', metavar='FILE', type=str,
                        help='write a file name')
    parser.add_argument('-d', dest="date", metavar='DATE', type=str,
                        help='a date to compare', default="5m")
    parser.add_argument('-r', dest="regexp", metavar='REGEXP', type=str, help='regular expression for describing log line',
                        default="^[^\[]*\[([^\]]*)")
    parser.add_argument('-f', dest="format", metavar="DATE_FORMAT", type=str, help='date format in strptime syntax',
                        default="%d/%b/%Y:%H:%M:%S")
    args = parser.parse_args()

    with open(args.filename) as f:
        for b in logtail(f, args.date, args.regexp, args.format):
            print(b, end='')