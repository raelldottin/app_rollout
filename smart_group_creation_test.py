import jamf
import json
from pprint import pprint

api = jamf.API()

# Create a new smart group
# print(api.get("mobiledevicegroups/id/0"))
# data = api.get("mobiledevicegroups/id/56")

# pprint(data["mobile_device_group"]["mobile_devices"])


# smart_group = f'{{"mobile_device_group": {{"name": "test group", "is_smart": "true", "site": {{"id": "-1", "name": "None"}}, "criteria": {{"size": "0"}}, "mobile_devices": {json.dumps(data["mobile_device_group"], sort_keys=True, indent=4, separators=(",", ": "))}}}}}'
smart_group = f'{{"mobile_device_group": {{"name": "test group", "is_smart": "true", "site": {{"id": "-1", "name": "None"}}, "criteria": {{"size": "0"}}}}}}'
print(
    api.post(
        "mobiledevicegroups/id/0",
        json.loads(smart_group),
    )
)
