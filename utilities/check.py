# This transaction checks the input

import re


# Check the username.
def check_username(username):
    if len(username) < 6 or len(username) > 12:
        return "Error: Username total characters should be between 6 and 12"
    elif not re.search("[A-Z]", username):
        return "Error: Username should contain one letter between [A-Z]"
    elif not re.search("[a-z]", username):
        return "Error: Username should contain one letter between [a-z]"
    elif not re.search("[0-9]", username):
        return "Error: Username should contain one letter between [1-9]"
    elif re.search("[\s]", username):
        return "Error: Username should not contain any space"
    else:
        return "Approved"


# check the name.
def check_name(name):
    if len(name) > 255:
        return "Error: Name should be less than 255 character"
    else:
        return "Approved"


user_type_list = ["Investor", "investor", "INVESTOR",
                  "Creator", "creator", "CREATOR",
                  "Institution", "institution", "INSTITUTION",
                  "Applicant", "applicant", "APPLICANT"]


# Check the User type.
def check_user(user_type):
    if user_type in user_type_list:
        return "Approved"
    else:
        return "Error: Check the spelling of User Type."


admin_list = ["admin", "ADMIN", "Admin"]


# check admin
def check_admin(user_type):
    if user_type in admin_list:
        return "Approved"
    else:
        return "Error: Check the spelling of User Type."


# Check the Input Email Address.
def check_email(email):
    pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
    if re.match(pat, email):
        return "Approved"
    else:
        return "Error: Email id is not valid."
