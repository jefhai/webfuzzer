"""
Fuzzer - sect.py
SWEN 331-01
09/21/15
"""

from elem import *

# The section class defines the default behavior of a section object, generally not modified, you should subclass!
class Section(object):
    def __init__(self):
        self.elements = None

        # Extra information
        # DEFINE HERE

        # Notes
        #  always end a section description with \n
        self.section_description = "THIS IS A SECTION HEADER\n"

    def add_element(self, element):
        self.elements.append(element)

    def remove_element(self, element):
        self.elements.remove(element)

    def get_elements(self):
        return self.elements

    def get_all_elements_of_type(self, cls):
        found = []
        for element in self.elements:
            if isinstance(element, cls):
                found.append(element)
        return found

    def __contains__(self, item):
        return item in self.elements

    def __str__(self):
        """ Example style:
            string = self.section_description

            if not self.elements:
                string += "\t No Elements\n"
            else:
                for element in self.elements:
                    string += element.__str__()
        """
        raise NotImplementedError("Subclasses of Section should implement their own __str__().")

class ModeDescriptionSection(Section):
    def __init__(self, base_url, mode):
        super(ModeDescriptionSection, self).__init__()

        # Extra information
        self.base_url = base_url
        self.mode = mode

        self.section_description = "The following is a " + self.mode + " report for " + self.base_url + "\n"

    def add_element(self, element):
        raise NotImplementedError("add_element() not implemented for the ModeDescriptionSection class.")

    def get_elements(self):
        raise NotImplementedError("get_elements() not implemented for the ModeDescriptionSection class.")

    def contains(self, element):
        raise NotImplementedError("contains() not implemented for the ModeDescriptionSection class.")

    def __str__(self):
        return self.section_description

class DiscoveredLinksSection(Section):
    def __init__(self):
        super(DiscoveredLinksSection, self).__init__()
        self.elements = []

        self.section_description = "Link Discovery:\n"

    def contains(self, element):
        return any(element.data == e.data for e in self.elements)

    def __str__(self):

        string = self.section_description

        if not self.elements:
            string += "\tNo Links Discovered\n"
        else:
            if any(isinstance(e, ConfirmedUrlLinkElement) for e in self.elements):
                string += "\tLocal Links:\n"
                for element in self.elements:
                    if isinstance(element, ConfirmedUrlLinkElement):
                        string += "\t\t" + element.__str__() + "\n"

            if any(isinstance(e, ExternalUrlLinkElement) for e in self.elements):
                string += "\tExternal Links:\n"
                for element in self.elements:
                    if isinstance(element, ExternalUrlLinkElement):
                        string += "\t\t" + element.__str__() + "\n"

            if any(isinstance(e, MalformedLinkElement) for e in self.elements):
                if any(isinstance(element, MalformedLinkElement) and element.hide is False for element in
                       self.elements):
                    string += "\tMalformed Links:\n"
                for element in self.elements:
                    if isinstance(element, MalformedLinkElement):
                        if not element.hide:
                            string += "\t\t" + element.__str__() + "\n"

            if any(isinstance(e, EmailAddressElement) for e in self.elements):
                string += "\tEmail Addresses:\n"
                for element in self.elements:
                    if isinstance(element, EmailAddressElement):
                        string += "\t\t" + element.__str__() + "\n"

        return string

class FormInputsSection(Section):
    def __init__(self):
        super(FormInputsSection, self).__init__()
        self.elements = []

        self.section_description = "Form Discovery:\n"

    def __str__(self):
        string = self.section_description

        if not self.elements:
            string += "\tNo Forms Discovered\n"
        else:
            if any(isinstance(e, FormInputElement) for e in self.elements):
                    string += "\tForm Inputs:\n"
                    for element in self.elements:
                        if isinstance(element, FormInputElement):
                            string += "\t\t" + element.__str__() + "\n"

        return string

class UrlInputsSection(Section):
    def __init__(self):
        super(UrlInputsSection, self).__init__()
        self.elements = []

        self.section_description = "URL Input Discovery:\n"

    def add_element(self, element):
        found_element = None
        for existing_element in self.elements:
            if element == existing_element:
                found_element = existing_element
                break
        if not found_element:
            self.elements.append(element)
        else:
            found_element + element

    def __str__(self):
        string = self.section_description

        if not self.elements:
            string += "\tNo URL Inputs Discovered\n"
        else:
            if any(isinstance(e, UrlInputElement) for e in self.elements):
                string += "\tURL Inputs:\n"
                for element in self.elements:
                    if isinstance(element, UrlInputElement):
                        string += "\t\t" + element.__str__() + "\n"

        return string

class CookiesSection(Section):
    def __init__(self):
        super(CookiesSection, self).__init__()
        self.elements = []

        self.section_description = "Cookie Discovery:\n"

    def __contains__(self, item):
        for element in self.elements:
            if item.data[0] == element.data[0] and item.data[1] == element.data[1]:
                return True
        return False

    def __str__(self):
        string = self.section_description

        if not self.elements:
            string += "\tNo Cookies Discovered\n"
        else:
            if any(isinstance(e, CookieElement) for e in self.elements):
                string += "\tCookies:\n"
                for element in self.elements:
                    if isinstance(element, CookieElement):
                        string += "\t\t" + element.__str__() + "\n"

        return string

class TestReportSection(Section):
    def __init__(self):
        super(TestReportSection, self).__init__()
        self.elements = []

        self.section_description = "Test Reports:\n"

    def __str__(self):
        string = self.section_description

        if not self.elements:
            string += "\tNo Test Reports\n"
        else:
            if any(isinstance(e, FormInputTestReportElement) for e in self.elements):
                string += "\tForm Input Reports:\n"
                for element in self.elements:
                    if isinstance(element, FormInputTestReportElement):
                        string += "\t\t" + element.__str__() + "\n"
            if any(isinstance(e, UrlInputTestReportElement) for e in self.elements):
                string += "\tUrl Input Reports:\n"
                for element in self.elements:
                    if isinstance(element, UrlInputTestReportElement):
                        string += "\t\t" + element.__str__() + "\n"

        return string
