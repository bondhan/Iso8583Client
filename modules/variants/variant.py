from abc import ABC
from ISO8583.ISO8583 import ISO8583

class Variant(ABC):
    def __init__(self, mti,parsed_data_json):
        self.mti = mti
        self.parsed_data_json = parsed_data_json

    def get_iso(self):
        iso = ISO8583()
        iso.setMTI(self.mti)
        for key, value in self.parsed_data_json.items():
            iso.setBit(key, value)

        return iso