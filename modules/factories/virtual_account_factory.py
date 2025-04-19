from modules.factories.variant_factory import VariantFactory
from modules.variants.virtual_account import VirtualAccount


class VirtualAccountFactory(VariantFactory):

        def create_iso_variant(selfmti, mti, json_data):
            return VirtualAccount(mti, json_data)