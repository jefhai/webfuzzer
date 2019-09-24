"""
Fuzzer - plan.py
SWEN 331-01
09/21/15
"""

import copy
import re
import validators
import itertools
from bs4 import BeautifulSoup
from sect import *
from elem import *
from random import shuffle
from urlparse import urlparse, urljoin
from util import *

# The plan class defines the default behavior of an plan object, generally not modified, you should subclass!
class Plan(object):
    def __init__(self):
        self.report = None
        self.site = None

    def execute(self):
        raise NotImplementedError("Subclasses of Plan should implement their own execute().")

    def get_report(self):
        return self.report

class Discovery(Plan):
    def __init__(self, site, common_words, extensions, malformed_ignored):
        super(Discovery, self).__init__()
        self.site = site

        # Optional file data
        self.common_words = common_words
        self.extensions = extensions
        self.malformed_ignored = malformed_ignored

        # Section
        self.site_description = ModeDescriptionSection(self.site.base_url, 'discovery')
        self.discovered_links = DiscoveredLinksSection()
        self.cookies = CookiesSection()
        self.form_inputs = FormInputsSection()
        self.url_inputs = UrlInputsSection()

        # Report
        self.report = [self.site_description, self.discovered_links,
                       self.form_inputs, self.url_inputs, self.cookies]

    def __get_cookies(self, session):
        # Get the session cookies
        cookies = session.cookies.items()

        # Check for any cookie changes, add new cookies
        for cookie in cookies:
            cookie_element = CookieElement(cookie)
            if not self.cookies.__contains__(cookie_element):
                self.cookies.add_element(cookie_element)

    def __get_page_form_input(self, page, page_url):
        # Find all the form inputs
        html = BeautifulSoup(page.text, 'html5lib')
        inputs_list = html.find_all('input')

        if inputs_list:
            # Add the form input element, there's no chance for a duplicate
            form_input_element = FormInputElement(inputs_list, page_url)
            self.form_inputs.add_element(form_input_element)

    def __get_potential_page_links(self, page):
        # Find all the pages href links
        html = BeautifulSoup(page.text, 'html5lib')
        for tag in html.find_all('a'):
            link = tag.get('href').__str__()

            element = None

            # If link appears to be a valid url
            if validators.url(link):
                # Categorize local and external links
                if link.startswith(self.site.base_url):
                    element = PotentialUrlLinkElement(link)
                else:
                    element = ExternalUrlLinkElement(link)

            # Find email address
            elif "mailto:" in link:
                potential_email = re.sub('mailto:', '', link)
                if validators.email(potential_email):
                    element = EmailAddressElement(potential_email)
            elif validators.email(link):
                element = EmailAddressElement(link)

            # Link didn't match anything valid
            else:
                element = MalformedLinkElement(link)

            # Add new link element to list if it does not already exist
            if not self.discovered_links.contains(element) and element is not None:
                self.discovered_links.add_element(element)

            # Will attempt to create valid links with invalid fragments
            self.__build_in_malformed()

    def __get_unreviewed(self, malformed_element_cls):
        return next((element for element in self.discovered_links.get_all_elements_of_type(malformed_element_cls)
                     if not element.reviewed), None)

    def __build_in_malformed(self):
        # Get an unreviewed malformed link element
        malformed_element = self.__get_unreviewed(MalformedLinkElement)
        while malformed_element:

            # If malformed element is blacklisted then don't review it
            if malformed_element.data in self.malformed_ignored:
                malformed_element.reviewed = True

            # If malformed element hasn't been reviewed, review it
            if not malformed_element.reviewed:

                potential_url = urljoin(self.site.base_url, malformed_element.data)
                # If the potential url looks valid
                if validators.url(potential_url):
                    # Check if its a known potential element
                    new_element = PotentialUrlLinkElement(potential_url)
                    if not self.discovered_links.contains(new_element):
                        self.discovered_links.add_element(new_element)

                    # Hide from report, it's a known potential element
                    malformed_element.hide = True

                malformed_element.reviewed = True

            malformed_element = self.__get_unreviewed(MalformedLinkElement)

    def __guess_potential_page_links(self):
        guessed_urls = []

        # Create url guesses
        base_url = self.site.base_url
        for common in self.common_words:
            for ext in self.extensions:
                potential_url = urljoin(base_url, common + ext)
                if validators.url(potential_url):
                    guessed_urls.append(potential_url)

        # Create potential link elements and add to discovered link list
        for guessed_url in guessed_urls:
            potential_link_element = PotentialUrlLinkElement(guessed_url)
            if not self.discovered_links.contains(potential_link_element):
                self.discovered_links.add_element(potential_link_element)

    def __get_url_inputs(self):
        # Get all the confirmed url link elements
        confirmed_link_elements = self.discovered_links.get_all_elements_of_type(ConfirmedUrlLinkElement)

        # Capture the confirmed url link inputs
        for confirmed_link_element in confirmed_link_elements:
            confirmed_url_link = confirmed_link_element.data
            parsed_link = urlparse(confirmed_url_link)

            # If there is something in the query or params stores, add element to url_inputs
            if not parsed_link.query == '':
                self.url_inputs.add_element(UrlInputElement(parsed_link))

    def __get_unvisited(self, link_element_cls):
        return next((element for element in self.discovered_links.get_all_elements_of_type(link_element_cls)
                     if not element.visited), None)

    def execute(self):

        sys.stdout.write("Getting things ready for discovery...\n")
        sys.stdout.flush()

        # Add base url
        self.discovered_links.add_element(PotentialUrlLinkElement(self.site.base_url))

        self.site.authenticate()

        self.__guess_potential_page_links()

        # Start the crawl
        urls_visited = 0
        potential_link_element = self.__get_unvisited(PotentialUrlLinkElement)
        while potential_link_element:
            potential_url = potential_link_element.data

            page = self.site.get_page(potential_url)

            # Reauthenticate if needed
            if page.status_code == 401 or page.status_code == 302:
                self.site.authenticate()
                page = self.site.get_page(potential_url)

            # Record successful page information
            if page.status_code == 200:
                self.__get_potential_page_links(page)
                self.__get_page_form_input(page, potential_url)
                self.__get_cookies(self.site.session)

                # Potential link becomes confirmed link
                confirmed_link_element = ConfirmedUrlLinkElement(potential_link_element.data)
                self.discovered_links.add_element(confirmed_link_element)
                self.discovered_links.remove_element(potential_link_element)

            potential_link_element.visited = True
            urls_visited += 1

            # Write percentage progress to console
            number_of_links_discovered = len(self.discovered_links.get_all_elements_of_type(ConfirmedUrlLinkElement)) + \
                                         len(self.discovered_links.get_all_elements_of_type(PotentialUrlLinkElement))
            percent_complete = FuzzUtil.percent(urls_visited, number_of_links_discovered)
            sys.stdout.write("\rDiscovering " + self.site.base_url + " " + percent_complete.__str__() + "% complete")
            sys.stdout.flush()

            # Next potential link
            potential_link_element = self.__get_unvisited(PotentialUrlLinkElement)

        sys.stdout.write("\n")
        sys.stdout.flush()

        sys.stdout.write("Finishing up...\n")
        self.__get_url_inputs()

class Test(Plan):
    def __init__(self, site, disc_form_input_elements, disc_url_input_elements, disc_cookie_elements, vectors,
                 sensitive, random, slow_ms):
        super(Test, self).__init__()
        self.site = site

        self.random = random
        self.slow_ms = slow_ms

        # From discovery
        self.disc_form_input_elements = copy.deepcopy(disc_form_input_elements)
        if random:
            shuffle(self.disc_form_input_elements)
        self.disc_url_input_elements = copy.deepcopy(disc_url_input_elements)
        self.disc_cookie_elements = copy.deepcopy(disc_cookie_elements)

        # Optional file data
        self.vectors = vectors
        self.sensitive = sensitive

        # Section
        self.site_description = ModeDescriptionSection(self.site.base_url, 'test')
        self.test_reports = TestReportSection()

        # Report
        self.report = [self.site_description, self.test_reports]

    def __get_url_input_permutations(self, url, url_input_parameters, vector):

        test_url_permutations = []

        parameter_combinations = []
        for num_queries in xrange(1, len(url_input_parameters) + 1):
            length_combinations = list(itertools.combinations(url_input_parameters, num_queries))
            for combination in length_combinations:
                parameter_combinations.append(combination)

        for parameter_combination in parameter_combinations:
            test_url_permutation = url + "?"
            first = True
            for parameter in parameter_combination:
                if not first:
                    test_url_permutation += "&"
                else:
                    first = False
                test_url_permutation += parameter.__str__() + "=" + vector.__str__()

            test_url_permutations.append(FuzzUtil.clean_url_spaces(test_url_permutation))

        return test_url_permutations

    def __get_form_payload(self, form_inputs, vector):

        attack_possibilities = {}
        type_whitelist = ["text", "password", "hidden", "email", "number", "search", "url"]

        # Remove the input fields that cannot be modified (e.g. the Submit button)
        for form_input in form_inputs:
            field = BeautifulSoup(form_input.__str__(), "html5lib")
            if "name" in field.input.__str__() and "type" in field.input.__str__():
                if field.input["type"] in type_whitelist:
                    attack_possibilities[field.input["name"]] = vector
                elif field.input["type"] == "submit" and "value" in field.input.__str__():
                    attack_possibilities[field.input["name"]] = field.input["value"]

        return attack_possibilities

    def __get_untested_form_input_element(self):
        return next((element for element in self.disc_form_input_elements if not element.tested), None)

    def __get_untested_url_input_element(self):
        return next((element for element in self.disc_url_input_elements if not element.tested), None)

    def __analyze_response_time(self, page):
        report_string = ""
        time_to_load = int(page.elapsed.total_seconds() * 1000)  # Convert timedelta to milliseconds
        if time_to_load > self.slow_ms:
            report_string += "Request response took " + time_to_load.__str__() + "ms. "
        return report_string

    def __analyze_status_code(self, page):
        report_string = ""
        if not page.status_code == 200:
            report_string += "Status code " + FuzzUtil.status_code_to_string(page.status_code) + ". "
        return report_string

    def __analyze_sensitive(self, page):
        sensitive_string = ""

        found_sensitive = False
        for sensitive_fragment in self.sensitive:
            if sensitive_fragment in page.text:
                found_sensitive = True
                if sensitive_string == "":
                    sensitive_string += "Response contained sensitive phrase(s): " + sensitive_fragment
                else:
                    sensitive_string += ", " + sensitive_fragment

        if found_sensitive:
            sensitive_string += ". "
            if "SQL" in sensitive_string:
                sensitive_string += "Page may be vulnerable to SQL injection. "

        return sensitive_string

    def __analyze_sanitize(self, page, vector):
        sanitize_string = ""

        if '<' in vector and '>' in vector:
            if vector in page.text:
                sanitize_string += vector + " was not sanitized. Page may be vulnerable to XSS. "

        return sanitize_string

    def __update_progress(self, num_tested_elements, total_test_elements):
        # Write percentage progress to console
        percent_complete = FuzzUtil.percent(num_tested_elements, total_test_elements)
        sys.stdout.write("\rTesting " + self.site.base_url + " " + percent_complete.__str__() + "% complete")
        sys.stdout.flush()

    def execute(self):
        sys.stdout.write("Getting things ready for testing...\n")
        sys.stdout.flush()

        num_tested_elements = 0
        total_test_elements = len(self.disc_form_input_elements) + \
                              len(self.disc_url_input_elements)

        self.site.authenticate()

        # Form input testing
        form_input_element = self.__get_untested_form_input_element()
        while form_input_element:
            url, form_inputs = form_input_element.data

            report_messages = []

            for vector in self.vectors:
                form_payload = self.__get_form_payload(form_inputs, vector)

                # Request page
                page = self.site.post_page(url, form_payload)

                # Analyze page
                response_string = self.__analyze_response_time(page)
                status_string = self.__analyze_status_code(page)
                sensitive_string = self.__analyze_sensitive(page)
                sanitize_string = self.__analyze_sanitize(page, vector)

                if response_string or status_string or sensitive_string or sanitize_string:
                    report_messages.append("Vector: " + vector.__str__() + " Produced: " + response_string + \
                                            status_string + sensitive_string + sanitize_string)

            # If there is something to report, report it.
            if report_messages:
                report_header = "Problem(s) found on: " + url.__str__()
                self.test_reports.add_element(FormInputTestReportElement(report_header, report_messages))

            form_input_element.tested = True

            num_tested_elements += 1
            self.__update_progress(num_tested_elements, total_test_elements)
            form_input_element = self.__get_untested_form_input_element()

        # Url input testing
        url_input_element = self.__get_untested_url_input_element()
        while url_input_element:
            url, url_input_parameters = url_input_element.data

            report_messages = []

            for vector in self.vectors:
                test_url_permutations = self.__get_url_input_permutations(url, url_input_parameters, vector)
                for test_url_permutation in test_url_permutations:
                    # Request page
                    page = self.site.get_page(test_url_permutation)

                    # Analyze page
                    response_string = self.__analyze_response_time(page)
                    status_string = self.__analyze_status_code(page)
                    sensitive_string = self.__analyze_sensitive(page)
                    sanitize_string = self.__analyze_sanitize(page, vector)

                    if response_string or status_string or sensitive_string or sanitize_string:
                        report_messages.append("Vector: " + vector.__str__() + " Produced: " + response_string + \
                                          status_string + sensitive_string + sanitize_string)

            # If there is something to report, report it.
            if report_messages:
                report_header = "Problem(s) found on: " + url.__str__()
                self.test_reports.add_element(UrlInputTestReportElement(report_header, report_messages))

            url_input_element.tested = True

            num_tested_elements += 1
            self.__update_progress(num_tested_elements, total_test_elements)
            url_input_element = self.__get_untested_url_input_element()

        sys.stdout.write("\n")
        sys.stdout.flush()

        sys.stdout.write("Finishing up...\n")

        self.site.reset_db()
