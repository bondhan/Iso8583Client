from modules.variants.variant import Variant

class Xlink(Variant):
    def __init__(self, mti, parsed_json):
        super().__init__(mti, parsed_json)
        self.variant = "xlink"
