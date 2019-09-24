"""
Fuzzer - elem.py
SWEN 331-01
09/21/15
"""

from urlparse import parse_qsl, urlunsplit, urljoin
import textwrap

# The section class defines the default behavior of an element object, generally not modified, you should subclass!
class Element(object):
    def __init__(self):
        self.data = None
        self.hide = False  # TODO: Use for future verbose reporting command

    def __str__(self):
        return self.data.__str__()

class CookieElement(Element):
    def __init__(self, cookie):
        super(CookieElement, self).__init__()
        self.data = cookie

    def __str__(self):
        return self.data[0].__str__() + ": " + self.data[1].__str__()

class EmailAddressElement(Element):
    def __init__(self, email_address):
        super(EmailAddressElement, self).__init__()
        self.data = email_address

class ExternalUrlLinkElement(Element):
    def __init__(self, url_link):
        super(ExternalUrlLinkElement, self).__init__()
        self.data = url_link

# Input Elements
class InputElement(Element):
    def __init__(self):
        super(InputElement, self).__init__()
        self.tested = False

class FormInputElement(InputElement):
    def __init__(self, input_dictionary, discovered_url):
        super(FormInputElement, self).__init__()
        self.data = (discovered_url, input_dictionary)

    def __str__(self):

        input_name_list = []

        for input in self.data[1]:
            if input.has_attr('name'):
                input_name_list.append(input["name"])

        string = "Inputs on " + self.data[0] + "\n"
        if input_name_list:
            string += "\t\t\t" + input_name_list.__str__()
        else:
            string += "\t\t\tNothing interesting found..."
        return string

class UrlInputElement(InputElement):
    def __init__(self, parsed_url):
        super(UrlInputElement, self).__init__()

        query_strings = []
        query_strings.append(parsed_url.query)

        query_list = parse_qsl(parsed_url.query, keep_blank_values=False)
        parameters = []
        for query in query_list:
            parameters.append(query[0])

        url = urlunsplit([parsed_url.scheme, parsed_url.netloc, parsed_url.path, None, None])
        self.data = [url, parameters]

    def __add__(self, other):
        for parameter in other.data[1]:
            if not self.data[1].__contains__(parameter):
                self.data[1].append(parameter)
        return self

    def __eq__(self, other):
        return self.data[0] == other.data[0]

# Malformed Elements
class MalformedElement(Element):
    def __init__(self):
        super(MalformedElement, self).__init__()
        self.reviewed = False

class MalformedLinkElement(MalformedElement):
    def __init__(self, malformed_link):
        super(MalformedLinkElement, self).__init__()
        self.data = malformed_link

# Url Link Elements
class UrlLinkElement(Element):
    def __init__(self):
        super(UrlLinkElement, self).__init__()
        self.visited = False
        self.status_code = None

class ConfirmedUrlLinkElement(UrlLinkElement):
    def __init__(self, confirmed_url_link):
        super(ConfirmedUrlLinkElement, self).__init__()
        self.data = confirmed_url_link

class PotentialUrlLinkElement(UrlLinkElement):
    def __init__(self, potential_url_link):
        super(PotentialUrlLinkElement, self).__init__()
        self.data = potential_url_link

# Test Report Elements
class TestReportElement(Element):
    def __init__(self, report_header, report_message):
        super(TestReportElement, self).__init__()
        self.data = (report_header, report_message)

    def __str__(self):
        """
        Example output:

            For the 'name' form input in was found that
                The following vector '<% jd #@!#! %>' caused sensitive information to be
                displayed: 123414124 username password
        """
        report_header, report_messages = self.data
        string = report_header + "\n"

        #Wrapper declaration
        wrapper = textwrap.TextWrapper()
        wrapper.initial_indent = "\t\t\t"
        wrapper.subsequent_indent = "\t\t\t\t"
        wrapper.width = 80

        for report_message in report_messages:
            for line in wrapper.wrap(report_message):
                string += line + "\n"
            
        return string

class UrlInputTestReportElement(TestReportElement):
    def __init__(self, report_header, report_message):
        super(UrlInputTestReportElement, self).__init__(report_header, report_message)

class FormInputTestReportElement(TestReportElement):
    def __init__(self, report_header, report_message):
        super(FormInputTestReportElement, self).__init__(report_header, report_message)
