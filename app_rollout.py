"""
iOS App Deployment
"""

__author__ = "Raell Dottin"
__email__ = "raell.dottin@untuckit.com"
__copyright__ = "Copyright (c) 2023 UNTUCKit"
__license__ = "MIT"
__version__ = "0.0.1"

import argparse
import logging
import io
import sys
from configparser import ConfigParser
from email.message import EmailMessage
import smtplib
import jamf

logfilepath = "app_rollout.log"
log_capture_string = io.StringIO()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(logfilepath),
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(log_capture_string),
    ],
)


def email_logfile(
    filename, argparse, email=None, password=None, recipient=None
) -> bool:
    """Emails all standard output to the receipient address.

    :param filename: the name of the log file
    :param argparse: argparse class with command line arguments
    :param email: sender email address
    :param password: the password for the sender email
    :param recipient: the recipient email address
    """

    if email and password and recipient:
        pass
    else:
        try:
            config = ConfigParser()
            config.read("./config.secrets")
            email = config.get("MAIL_CONFIG", "SENDER_EMAIL")
            password = config.get("MAIL_CONFIG", "SENDER_PASSWD")
            recipient = config.get("MAIL_CONFIG", "RECIPIENT_EMAIL")
        except:
            logging.exception(
                "Unable to email log file because email authentication is not properly setup.", exc_info=True
            )
            return False

    try:
        with open(filename, "rb") as f:
            logs = f.read()
    except:
        with open(logfilepath, "rb") as f:
            logs = f.read()

    if not logs:
        return False

    logs = log_capture_string.getvalue()
    subject = f"App Deployment: {argparse.appname if hasattr(argparse, 'appname') else ''} {argparse.appversion if hasattr(argparse, 'appversion') else ''}"
    message = EmailMessage()
    message["from"] = email
    message["to"] = recipient
    message["subject"] = subject
    message.set_content(logs)

    try:
        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.ehlo()
        session.starttls()
        session.login(email, password)
        session.send_message(message)
        session.quit()
    except:
        logging.exception("Unable to send log file via email", exc_info=True)
    log_capture_string.close()
    return True


def get_mobile_app(appname: str) -> tuple[str, str, str, str] | None:
    """Get a list of mobile apps, find a specific app from the list and return id, name, version, and bundle id.

    :param appname: the name of mobile application
    """
    api = jamf.API()
    mobiledeviceapps = api.get("mobiledeviceapplications")

    try:
        for app in mobiledeviceapps["mobile_device_applications"][
            "mobile_device_application"
        ]:
            if appname == app["name"]:
                logging.info(
                    f"Found Mobile Device App entry for {app['name']}.")
                return app["id"], app["name"], app["version"], app["bundle_id"]
    except:
        logging.exception(
            "Unable to get list of mobile device apps", exc_info=True)

    logging.info(f"Unable to find a mobile app named {appname}")

    return None


def get_mobile_device_group(groupname: str) -> tuple[str, str] | None:
    """Get a list of smart device groups, find a specific smart group based on the group name and return the group id and group name.

    :param groupname: the name of samrt device group
    """
    api = jamf.API()
    mobiledevicegroups = api.get("mobiledevicegroups")

    try:
        for group in mobiledevicegroups["mobile_device_groups"]["mobile_device_group"]:
            if groupname == group["name"]:
                return group["id"], group["name"]

    except:
        logging.exception(
            "Unable to get list of mobile device groups.", exc_info=True)

    return availabeid


# implement a function to create smart group
def set_mobile_device_group(id):
    """Creates a mobile smart group.
    :param 
    return None


def get_mobile_app_details(id):
    api = jamf.API()
    api.get(f"mobiledeviceapplications/id/{id}")


def set_mobile_app_details(appname):
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Automate iOS app deployment using Jamf Pro"
    )
    parser.add_argument(
        "--jamfserver",
        action="store",
        dest="jamfserver",
        default=None,
        help="Jamf Server URL",
    )
    parser.add_argument(
        "--jamfuser",
        action="store",
        dest="jamfuser",
        default=None,
        help="Jamf Server Username",
    )
    parser.add_argument(
        "--jamfpass",
        action="store",
        dest="jamfpass",
        default=None,
        help="Jamf Server Password",
    )
    parser.add_argument(
        "--appname",
        action="store",
        dest="appname",
        default=None,
        help="iOS App Name",
        required=True,
    )
    parser.add_argument(
        "--appversion",
        action="store",
        dest="appversion",
        default=None,
        help="iOS App Version",
    )
    parser.add_argument(
        "--mininumiosversion",
        action="store",
        dest="minimumiosversion",
        default=None,
        help="Minimum Required iOS Version",
    )
    parser.add_argument(
        "--bundleidentifier",
        action="store",
        dest="bundleidentifier",
        default=None,
        help="App Bundle Identifier",
    )

    args = parser.parse_args()

    id, appname, appversion, bundleidentifier = get_mobile_app(args.appname)
    print(get_mobile_app_details(id))
    print(get_mobile_device_group(f"{appname} Deployment Group {appversion}"))


#    get_smart_device_groups()
if __name__ == "__main__":
    main()
