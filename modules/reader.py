import json

def read_input_file(file):


    # Read and parse JSON file
    with open(file, "r") as file:
        data = json.load(file)

        if data["meta"] is None or data["data"] is None:
            raise Exception("Wrong JSON format")

    return data