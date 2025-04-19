import copy
import datetime
import random
import string

from modules.factories.artajasa_factory import ArtajasaFactory
from modules.factories.virtual_account_factory import VirtualAccountFactory
from modules.factories.xlink_factory import XlinkFactory
from modules.factories.zte_factory import ZteFactory
from modules.variants.xlink import Xlink

def convert_to_strftime_format(custom_format):
    format_map = {
        "MM": "%m",
        "DD": "%d",
        "hh": "%H",
        "mm": "%M",
        "ss": "%S"
    }

    for key, value in format_map.items():
        custom_format = custom_format.replace(key, value)

    return custom_format

def generate_random_string(length=12):
    l = int(length / 3)
    k = length - l
    characters = ""
    numbers = ""
    for i in range(l):
        characters = characters + random.choice(string.ascii_letters.upper())

    for i in range(k):
        numbers = numbers + str(random.randint(0, 9))

    return characters + numbers


def generate_random_number(length, min):
    numbers = ""
    for i in range(length):
        numbers = numbers + str(random.randint(0, 9))

    return str(int(numbers) + min)


FUNCTIONS = {
    "randn": lambda args: generate_random_number(args[0], args[1]),
    "now": lambda args: datetime.datetime.now().strftime(convert_to_strftime_format(args[0])),
    "randa": lambda args: generate_random_string(args[0]),
}

def execute_dynamic_json(json_param):
    json_obj = copy.deepcopy(json_param)  # Make a full deep copy

    for key, value in json_obj.items():
        if isinstance(value, dict):
            func_name = value["func"]
            args = value["args"]
            if func_name in FUNCTIONS:
                json_obj[key] = FUNCTIONS[func_name](args)
    return json_obj


def convert_json_to_dict(json_data):
    dict_data = {}
    for key, value in json_data.items():
        dict_data[int(key)]=value

    return dict_data

def manufacture_iso_class(json_data):
    meta = json_data["meta"]
    variant_key = meta["variant"]
    mti = meta["mti"]

    data = json_data["data"]
    parsed_json = execute_dynamic_json(data)
    dict_data = convert_json_to_dict(parsed_json)

    match variant_key:
        case "artajasa":
            a = ArtajasaFactory()
            iso_obj = a.create_iso_variant(mti, dict_data)
        case "xlink":
            x = XlinkFactory()
            iso_obj = x.create_iso_variant(mti, dict_data)
        case "virtual-account":
            v = VirtualAccountFactory()
            iso_obj = v.create_iso_variant(mti, dict_data)
        case "zte":
            v = ZteFactory()
            iso_obj = v.create_iso_variant(mti, dict_data)
        case _:
            print("default")
            iso_obj = None

    return iso_obj
