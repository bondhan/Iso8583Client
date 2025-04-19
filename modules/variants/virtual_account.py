from modules.variants.variant import Variant


class VirtualAccount(Variant):
    def __init__(self, mti, parsed_json):
        super().__init__(mti, parsed_json)
        self.variant = "virtual-account"

