from modules.evaluator import manufacture_iso_class
from modules.reader import read_input_file

def get_echo_message(file):
    json_data = read_input_file(file)

    iso_class = manufacture_iso_class(json_data)
    iso_msg = iso_class.get_iso()
    print("iso_class:", iso_class.variant, "mti", iso_class.mti, "message:", iso_msg.getNetworkISO())
    return iso_msg.getNetworkISO()