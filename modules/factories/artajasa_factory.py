from modules.factories.variant_factory import VariantFactory
from modules.variants.artajasa import Artajasa


class ArtajasaFactory(VariantFactory):

        def create_iso_variant(self, mti, json_data):
            return Artajasa(mti, json_data)