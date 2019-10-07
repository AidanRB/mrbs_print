import getreport
from parse import parse
from getpass import getpass

# Set variable variables
from_date = '2019-07-07'
to_date = '2019-07-13'
areamatch = 'Education Building'

# Set root of MRBS and log in
getreport.rootURL = "http://192.168.0.2/MRBS"
getreport.login(input("username: "), getpass("password: "))

# Get and parse csv into data
csvtext = getreport.getreport(from_date, to_date, areamatch)
events = parse(csvtext)
events
