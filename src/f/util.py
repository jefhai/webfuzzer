"""
Fuzzer - util.py
SWEN 331-01
09/21/15
"""

import os
import sys
from sect import Section

class FuzzUtil(object):
    @staticmethod
    def get_lines_from_file(file_path):
        try:
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            if not os.path.isfile(file_path):
                os.write(file_path, "")
            with open(file_path, 'r') as fuzz_file:
                lines_list = fuzz_file.read().splitlines()
        except IOError as e:
            raise IOError(e.args)

        return lines_list

    @staticmethod
    def write_report(report, report_path):
        try:
            if not os.path.exists(os.path.dirname(report_path)):
                os.makedirs(os.path.dirname(report_path))
            with open(report_path, 'a+') as f:
                for section in report:
                    if isinstance(section, Section):
                        f.write(section.__str__() + "\n")
        except IOError as e:
            raise IOError(e.args)

        sys.stdout.write("Report written to: " + report_path + "\n")

    @staticmethod
    def percent(currval, maxval):
        return int(round(float(currval) / maxval * 100))

    @staticmethod
    def clean_url_spaces(url):
        return url.replace(' ', '%20')

    @staticmethod
    def status_code_to_string(status_code):
        if status_code == 200:
            return "200 (Ok)"
        if status_code == 303:
            return "303 (See Other)"
        elif status_code == 400:
            return "400 (Bad Request)"
        elif status_code == 401:
            return "401 (Unauthorized)"
        elif status_code == 403:
            return "403 (Forbidden)"
        elif status_code == 404:
            return "404 (Not Found)"
        elif status_code == 500:
            return "500 (Internal Server Error)"
        else:
            return status_code.__str__() + " (NO DEFINITION)"
