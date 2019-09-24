"""
Fuzzer - auth.py
SWEN 331-01
09/21/15
"""

import requests

class Site(object):
    session = None
    current_page = None
    base_url = None

    def __init__(self, base_url):
        self.base_url = base_url

    def authenticate(self):
        pass

    def reset_db(self):
        pass

    def get_session(self):
        return self.session

    def get_page(self, url, payload=None):
        self.current_page = self.session.get(url, params=payload, data=payload)
        return self.current_page

    def post_page(self, url, payload):
        self.current_page = self.session.post(url, params=payload, data=payload)
        return self.current_page

class NonAuthSite(Site):
    name = 'noauth'

    def __init__(self, base_url):
        super(NonAuthSite, self).__init__(base_url)
        self.session = requests.Session()

class BodgeitSite(Site):
    name = 'bodgeit'

    def __init__(self, base_url):
        super(BodgeitSite, self).__init__(base_url)
        self.session = requests.Session()
        self.username = 'admin@bodgeit.com'
        self.password = 'password'
        self.registration_url = 'http://127.0.0.1:8080/bodgeit/register.jsp?'
        self.login_url = 'http://127.0.0.1:8080/bodgeit/login.jsp?'

        # Create the user. This will fail gracefully if already created.
        self.session.post("http://127.0.0.1:8080/bodgeit/register.jsp?",
                          {'username': self.username, 'password1': self.password, 'password2': self.password})

    def authenticate(self):
        self.session.post(self.login_url, {'username': self.username, 'password': self.password})

class DvwaSite(Site):
    name = 'dvwa'

    def __init__(self, base_url):
        super(DvwaSite, self).__init__(base_url)
        self.session = requests.Session()
        self.username = 'admin'
        self.password = 'password'
        self.login_url = 'http://127.0.0.1/dvwa/login.php'

    def authenticate(self):
        self.session.post(self.login_url, {'Login': 1, 'password': self.password, 'username': self.username})

        # Set low security
        cookies = self.session.cookies
        session_id = cookies["PHPSESSID"]
        self.session.cookies.clear()
        self.session.cookies["PHPSESSID"] = session_id
        self.session.cookies["security"] = "low"

    def reset_db(self):
        self.session.post('http://127.0.0.1/dvwa/setup.php', {'create_db':'Create / Reset Database'})
