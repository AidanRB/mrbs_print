import requests
from bs4 import BeautifulSoup
from getpass import getpass

# Set default as localhost/MRBS
# Can be changed when imported to use external host
rootURL = "http://localhost/MRBS"
# Dictionary for logging in
logindata = {
    'returl': '',
    'target_url': '',
    'action': 'SetName',
    'username': '',
    'password': ''
}

# Dictionary to get CSV
reportdata = {
    'phase': '2',
    'roommatch': '',
    'namematch': '',
    'descrmatch': '',
    'creatormatch': '',
    'match_confirmed': '2',
    'output': '0',
    'output_format': '1',
    'sortby': 's',
    'sumby': 'd',
    'datatable': '1'
}

# Create requests session to manage cookies
s = requests.Session()


# Function to log in (and get csrf_token) for getting report
def login(username, password):
    logindata['username'] = username
    logindata['password'] = password
    # Get/parse login page to get csrf_token
    loginpage = s.get(rootURL + "/admin.php")
    loginsoup = BeautifulSoup(loginpage.text, 'html.parser')
    # Find csrf_token and add it to login/report dicts
    csrf_token = BeautifulSoup(loginpage.text, 'html.parser').find(
        'input', attrs={'name': 'csrf_token'})['value']
    logindata['csrf_token'] = csrf_token
    reportdata['csrf_token'] = csrf_token
    # Log in
    loggedin = s.post(rootURL + "/admin.php",
                      allow_redirects=True, data=logindata)
    # Check for redirect (successful login) or 200 (incorrect user/pass)
    if loggedin.status_code == 302:
        return True
    elif loggedin.status_code == 200:
        return False


# Get CSV report in specified times/areas
def getreport(from_date, to_date, areamatch):
    reportdata['from_date'] = from_date
    reportdata['to_date'] = to_date
    reportdata['areamatch'] = areamatch
    report = s.post(rootURL + "/report.php", data=reportdata)
    return report.text
