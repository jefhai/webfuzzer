"""
Fuzzer - argp.py
SWEN 331-01
09/21/15
"""

import argparse
import os
import validators
from site import *

class FindDiscoveryReportPath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if os.path.isfile(values):
            if os.access(values, os.R_OK):
                setattr(namespace, self.dest, values)
        else:
            raise ValueError("--disc-report is not an accessible file path")

class FindTestReportPath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if os.path.isfile(values):
            if os.access(values, os.R_OK):
                setattr(namespace, self.dest, values)
        else:
            raise ValueError("--test-report is not an accessible file path")

class FindCommonWords(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if os.path.isfile(values):
            if os.access(values, os.R_OK):
                setattr(namespace, self.dest, values)
        else:
            raise ValueError("--common-words is not an acceptable value")

class FindExtensions(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if os.path.isfile(values):
            if os.access(values, os.R_OK):
                setattr(namespace, self.dest, values)
        else:
            raise ValueError("--extensions is not an accessible file path")

class FindMalformedIgnore(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if os.path.isfile(values):
            if os.access(values, os.R_OK):
                setattr(namespace, self.dest, values)
        else:
            raise ValueError("--malformed-ignore is not an accessible file path")

fuzz_parser = argparse.ArgumentParser(usage="%(prog)s [discover | test] url OPTIONS")
fuzz_mode_subparsers = fuzz_parser.add_subparsers(dest='mode')

# Common parser arguments
fuzz_parent_parser = argparse.ArgumentParser(add_help=False)
fuzz_parent_parser.add_argument('url', help="Site url to fuzz.",
                                type=str)

fuzz_parent_parser.add_argument('--common-words', dest='common_words', help="Newline-delimited file \
    of common words to be used in page guessing and input guessing. Required.",
                                type=str, required=True, action=FindCommonWords, default="./resources/common_words.txt")

fuzz_parent_parser.add_argument('--custom-auth', dest='custom_auth', help="Signal that the fuzzer\
    should use hard-coded authentication for a specific application (e.g. dvwa). Optional.",
                                type=str, required=False, default='noauth')

fuzz_parent_parser.add_argument('--disc-report', dest='disc_report_path', help="The location for the discovery report \
    output file. Optional.", type=str, required=False, action=FindDiscoveryReportPath,
                                default="./reports/discovery.txt")

fuzz_parent_parser.add_argument('--extensions', dest='extensions', help="A list of common extensions. Optional",
                                type=str, required=False, action=FindExtensions, default="./resources/extensions.txt")

fuzz_parent_parser.add_argument('--malformed-ignored', dest='malformed_ignored', help="A list of malformed strings that\
    should be ignored during the discovery process. Optional", type=str, required=False,
                                action=FindMalformedIgnore, default="./resources/malformed_ignored.txt")

fuzz_parent_parser.add_argument('--test-report', dest='test_report_path', help="The location for the test report \
    output file. Optional.", type=str, required=False, action=FindTestReportPath, default="./reports/test.txt")

# Discovery parser
disc_parser = fuzz_mode_subparsers.add_parser('discover', parents=[fuzz_parent_parser])

# Test parser
test_parser = fuzz_mode_subparsers.add_parser('test', parents=[fuzz_parent_parser])
test_parser.add_argument('--vectors', dest='vectors', help="Newline-delimited file of common \
    exploits to vulnerabilities. Required.",
                         type=str, required=True, default="./resources/vectors.txt")

test_parser.add_argument('--sensitive', dest='sensitive', help="Newline-delimited file data \
    that should never be leaked. It's assumed that this data is in the application's database \
    (e.g. test data), but is not reported in any response. Required.",
                         type=str, required=True, default="./resources/sensitive.txt")

test_parser.add_argument('--random', dest='random', help="When off, try each input to each \
    page systematically.  When on, choose a random page, then a random input field and test \
    all vectors. Default: false.",
                         type=bool, required=False, default=False)

test_parser.add_argument('--slow', dest='slow_ms', help="Number of milliseconds considered \
    when a response is considered \"slow\". Default is 500 milliseconds",
                         type=int, required=False, default=500)

# Get parser arguments
args = fuzz_parser.parse_args()

# Validate custom authentication application profile exists
found = False
for s in Site.__subclasses__():
    if args.custom_auth == s.name:
        site = s.__new__(s)
        site.__init__(args.url)
        found = True
if not found:
    raise ValueError("--custom-auth is not a known authentication application")

# Validate provided url
if not validators.url(args.url):
    raise ValueError("provided url is not valid")
