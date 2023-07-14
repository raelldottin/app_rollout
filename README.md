# Automate iOS App Deployment via Jamf

Python script to deploy and monitor the deployment of an iOS app via Jamf.

Note: I recommend using Autopkg project for similar tasks: https://github.com/autopkg/autopkg

## Design

iOS app deployment steps:

Create smart groupss if not already created

Examples of smart groups:
"Assocaite App Deployment Group x.x.x"
"Assocaite App Deployment Group x.x.x without minimum iOS version"
"II. Associate app v.x.x.x"

There are two types of deployements: pilot stores and all stores

Steps for app deployment to pilot stores:
Add "Associate App Deployment Group x.x.x" to the "NewStore Associate App (Pilot QA)" exclusion scope in Jamf for pilot store deployments
Wait 15 minutes
Remove the exclude

Steps for app deployment to all stores:
Add "Associate App Deployment Group x.x.x" to the "NewStore Associate App" exclusion scope in Jamf for pilot store deployments
Wait 15 minutes
Remove the exclude

At 9 am EST, update a Google spreadsheet with devices pending update and devices without the minimum iOS version. This data is derived from smart groups. 

## Installation
```console
git clone https://github.com/raelldottin/app_rollout.git
cd app_rollout
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app_rollout.py --appname "NewStore Associate App"

usage: app_rollout.py [-h] [--jamfserver JAMFSERVER] [--jamfuser JAMFUSER] [--jamfpass JAMFPASS]
                      --appname APPNAME [--appversion APPVERSION]
                      [--mininumiosversion MINIMUMIOSVERSION] [--bundleidentifier BUNDLEIDENTIFIER]

```
