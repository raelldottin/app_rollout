import ast
from pprint import pprint

with open("output.json") as f:
    data = f.read()

print("Data type before reconstruction : ", type(data))

# reconstructing the data as a dictionary
d = ast.literal_eval(data)

print("Data type after reconstruction : ", type(d))
pprint(d["mobile_device_application"]["scope"])
