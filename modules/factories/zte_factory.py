from modules.factories.variant_factory import VariantFactory
from modules.variants.zte import Zte


class ZteFactory(VariantFactory):

        def create_iso_variant(self, mti, json_data):
            return Zte(mti, json_data)