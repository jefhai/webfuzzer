"""
Fuzzer - fuzz.py
SWEN 331-01
09/21/15
"""

from src.f.argp import *
from src.f.plan import *
from src.f.util import *

def main():
    # Optional file data
    common_words = FuzzUtil.get_lines_from_file(args.common_words)
    extensions = FuzzUtil.get_lines_from_file(args.extensions)
    malformed_ignored = FuzzUtil.get_lines_from_file(args.malformed_ignored)

    # Report paths
    disc_report_path = args.disc_report_path

    discovery = Discovery(site, common_words, extensions, malformed_ignored)
    discovery.execute()
    FuzzUtil.write_report(discovery.get_report(), disc_report_path)

    if args.mode == 'test':
        # Optional data
        sensitive = FuzzUtil.get_lines_from_file(args.sensitive)
        vectors = FuzzUtil.get_lines_from_file(args.vectors)
        random = args.random
        slow_ms = args.slow_ms

        # Report paths
        test_report_path = args.test_report_path

        test = Test(site, discovery.form_inputs.elements, discovery.url_inputs.elements, 
                    discovery.cookies.elements, vectors, sensitive, random, slow_ms)
        test.execute()
        FuzzUtil.write_report(test.get_report(), test_report_path)

    return 0

if __name__ == '__main__':
    rc = main()
    sys.exit(rc)
