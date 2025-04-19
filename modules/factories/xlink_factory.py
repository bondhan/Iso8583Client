from modules.factories.variant_factory import VariantFactory
from modules.variants.xlink import Xlink


class XlinkFactory(VariantFactory):

        def create_iso_variant(self, mti, json_data):
            return Xlink(mti, json_data)