"""
iOS App Deployment Reporting
"""

from __future__ import annotations

__author__ = "Raell Dottin"
__email__ = "raell.dottin@untuckit.com"
__copyright__ = "Copyright (c) 2023 UNTUCKit"
__license__ = "MIT"
__version__ = "0.0.1"

import logging
import sys
import argparse
import jamf
import csv

logfilepath = "app_rollout_report.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(funcName)s() - %(message)s",
    handlers=[
        logging.FileHandler(logfilepath),
        logging.StreamHandler(sys.stdout),
    ],
)


def get_mobile_device_group(groupname: str) -> tuple[str, str] | tuple[None, None]:
    """Get a list of smart device groups, find a specific smart group based on the g
    roup name and return the group id and group name.

        :param groupname: the name of samrt device group
    """
    api = jamf.API()
    mobiledevicegroups = api.get("mobiledevicegroups")

    try:
        for group in mobiledevicegroups["mobile_device_groups"]["mobile_device_group"]:
            if groupname == group["name"]:
                logging.debug(f"Found smart group: {group['name']}")
                return group["id"], group["name"]
    except:
        logging.exception("Unable to get list of mobile device groups.", exc_info=True)

    logging.info(f"Unable to find mobile device group: {groupname}")
    return None, None


def get_mobile_app(
    appname: str,
) -> tuple[str, str, str] | tuple[None, None, None]:
    """Get a list of mobile apps, find a specific app from the list and return id, n
    ame, version, and bundle id.

        :param appname: the name of mobile application
    """
    api = jamf.API()
    mobiledeviceapps = api.get("mobiledeviceapplications")

    try:
        for app in mobiledeviceapps["mobile_device_applications"][
            "mobile_device_application"
        ]:
            if appname == app["name"]:
                logging.info(f"Found Mobile Device App entry for {app['name']}.")
                return app["name"], app["version"], app["bundle_id"]
    except:
        logging.exception("Unable to get list of mobile device apps", exc_info=True)

    logging.info(f"Unable to find a mobile app named {appname}")

    return None, None, None


def getDeployReport(
    appname,
    smartdevicegroup,
    appversion=None,
    mininumiosversion=None,
    bundleidentifier=None,
):
    if any(
        arg is None
        for arg in (
            appname,
            appversion,
            mininumiosversion,
            bundleidentifier,
            smartdevicegroup,
        )
    ):
        appname, appversion, bundleidentifier = get_mobile_app(appname)


def main():
    """
    Get smart group details.
    Check each mobile device record of every member of this smart.
    Check app name, app version, bundle id, ios version.
    Create a spreadsheet with the results.
    """
    parser = argparse.ArgumentParser(
        description="Produce iOS app deployment reporting using Jamf Pro"
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
        "--smartdevicegroup",
        action="store",
        dest="smartdevicegroup",
        default=None,
        help="Smart Device Group",
        required=True,
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
        logging.debug("Debug logging enabled.")

    getDeployReport(
        args.appname,
        args.appversion,
        args.mininumiosversion,
        args.bundleidentifier,
        args.smartdevicegroup,
    )


if __name__ == "__main__":
    # Get the app name
    # Get the smart group name
    # Get app version
    # Check each member of the smart group's version of the app
    # Save the data into a gsheet
    # Run from github
    main()
