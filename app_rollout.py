"""
iOS App Deployment
"""

from __future__ import annotations

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
                "Unable to email log file because email authentication is not properly setup.",
                exc_info=True,
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


def get_mobile_app(
    appname: str,
) -> tuple[str, str, str, str] | tuple[None, None, None, None]:
    """Get a list of mobile apps, find a specific app from the list and return id, name, version, and bundle id.

    :param appname: the name of mobile application
    """
    api = jamf.API()
    mobiledeviceapps = api.get("mobiledeviceapplications")

    try:
        if mobiledeviceapps:
            for app in mobiledeviceapps["mobile_device_applications"][
                "mobile_device_application"
            ]:
                if appname == app["name"]:
                    logging.info(f"Found Mobile Device App entry for {app['name']}.")
                    return app["id"], app["name"], app["version"], app["bundle_id"]
    except:
        logging.exception("Unable to get list of mobile device apps", exc_info=True)

    logging.info(f"Unable to find a mobile app named {appname}")

    return None, None, None, None


def get_mobile_device_group(groupname: str) -> tuple[str, str] | int:
    """Get a list of smart device groups, find a specific smart group based on the group name and return the group id and group name.

    :param groupname: the name of samrt device group
    """
    api = jamf.API()
    mobiledevicegroups = api.get("mobiledevicegroups")
    availableId = 0

    try:
        for group in mobiledevicegroups["mobile_device_groups"]["mobile_device_group"]:
            logging.debug(f"{group['id']=} {availableId=}")
            if (not availableId) or (availableId < int(group["id"])):
                availableId = int(group["id"])
            if groupname == group["name"]:
                return group["id"], group["name"]

    except:
        logging.exception("Unable to get list of mobile device groups.", exc_info=True)

    return availableId + 1


# implement a function to create smart group
def set_mobile_device_group(id) -> bool:
    """Creates a mobile smart group.
    :param id: id of the mobile group to create
    """
    return None


def get_mobile_app_details(id):
    """Get the entry details for a specific mobile app id
    :param id: id of the mobile app
    """
    api = jamf.API()
    return api.get(f"mobiledeviceapplications/id/{id}")


def set_mobile_app_details(id):
    """Set the mobile app details for a specific mobile app id
    :param id: id of the mobile app

    do we have to convert dictionary to xml?
    can the library perform a put with a dictionary?
    {'mobile_device_application': {'general': {'id': '92', 'name': 'NewStore Associate App', 'display_name': 'NewStore Associate App', 'description': 'The NewStore Associate App is for a retail store associate to perform various tasks in-store. Some of the key transactions performed by the store associate using the app are mentioned below.', 'bundle_id': 'com.newstore.associate-one', 'version': '1.36.0', 'internal_app': 'true', 'category': {'id': '2', 'name': 'iOS Applications'}, 'ipa': {'name': None, 'uri': None, 'data': None}, 'icon': {'id': '10837', 'name': '1024x1024bb.png', 'uri': 'https://ics.services.jamfcloud.com/icon/hash_becc2d03a7df883dd90054391441b13907a5385ae3f0ffa425b1f84007dfe1c4'}, 'mobile_device_provisioning_profile': None, 'url': 'https://apps.apple.com/us/app/newstore-associate-app/id1545162024', 'itunes_store_url': 'https://apps.apple.com/us/app/newstore-associate-app/id1545162024', 'make_available_after_install': 'true', 'itunes_country_region': 'US', 'itunes_sync_time': '25200', 'deployment_type': 'Install Automatically/Prompt Users to Install', 'deploy_automatically': 'true', 'deploy_as_managed_app': 'true', 'remove_app_when_mdm_profile_is_removed': 'true', 'prevent_backup_of_app_data': 'false', 'allow_user_to_delete': 'true', 'require_network_tethered': 'false', 'keep_description_and_icon_up_to_date': 'true', 'keep_app_updated_on_devices': 'false', 'free': 'true', 'take_over_management': 'true', 'host_externally': 'true', 'external_url': 'https://apps.apple.com/us/app/newstore-associate-app/id1545162024', 'site': {'id': '-1', 'name': 'None'}}, 'scope': {'all_mobile_devices': 'true', 'all_jss_users': 'true', 'mobile_devices': None, 'buildings': None, 'departments': None, 'mobile_device_groups': None, 'jss_users': None, 'jss_user_groups': None, 'limitations': {'users': None, 'user_groups': None, 'network_segments': None}, 'exclusions': {'mobile_devices': {'mobile_device': {'id': '412', 'name': 'Joe Kabashi (Quality Assurance) iPad', 'udid': '00008030-001C18A60E88C02E', 'wifi_mac_address': '9C:3E:53:C3:CC:CD'}}, 'buildings': {'building': [{'id': '1', 'name': 'HQ'}, {'id': '77', 'name': 'Satellite Office  - Chicago'}, {'id': '93', 'name': 'UNTUCKit  Westfield'}, {'id': '14', 'name': 'UNTUCKit Boston'}, {'id': '3', 'name': 'UNTUCKit Brookfield'}, {'id': '87', 'name': 'UNTUCKit Yorkdale'}]}, 'departments': None, 'mobile_device_groups': None, 'users': None, 'user_groups': None, 'network_segments': None, 'jss_users': None, 'jss_user_groups': None}}, 'self_service': {'self_service_install_button_text': 'Install', 'self_service_after_install_button_text': 'Reinstall', 'self_service_description': 'The NewStore Associate App is for a retail store associate to perform various tasks in-store. Some of the key transactions performed by the store associate using the app are mentioned below.', 'self_service_icon': {'id': '10837', 'filename': '1024x1024bb.png', 'uri': 'https://ics.services.jamfcloud.com/icon/hash_becc2d03a7df883dd90054391441b13907a5385ae3f0ffa425b1f84007dfe1c4'}, 'feature_on_main_page': 'false', 'self_service_categories': {'category': {'id': '2', 'name': 'iOS Applications', 'display_in': 'true'}}, 'notification': 'false', 'notification_subject': None, 'notification_message': None}, 'vpp_codes': None, 'vpp': {'assign_vpp_device_based_licenses': 'true', 'vpp_admin_account_id': '1', 'total_vpp_licenses': '1000', 'remaining_vpp_licenses': '606', 'used_vpp_licenses': '394'}, 'app_configuration': {'preferences': '<dict>\r\n    <key>live</key>\r\n    <string>untuckit</string>\r\n    <key>test</key>\r\n    <string>untuckit-staging</string>\r\n</dict>'}}}
    """

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
    parser.add_argument(
        "--debug",
        action=argparse.BooleanOptionalAction,
        dest="debug",
        default=None,
        help="Debugging output",
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    id, appname, appversion, bundleidentifier = get_mobile_app(args.appname)
    print(f"{id=}, {appname=}, {appversion=}, {bundleidentifier=}")

    if id:
        print(get_mobile_app_details(id))
    if appname and appversion:
        print(get_mobile_device_group(f"{appname} Deployment Group {appversion}"))

    """
    Deployment process add deployment group as an exclusion to the mobile app entry
    Wait 5 minutes
    Remove the deployment group from the mobile app exception

    we need 
    set_mobile_app_details(id)
    sleep(300)
    set_mobile_app_details(id)
    """


if __name__ == "__main__":
    main()
