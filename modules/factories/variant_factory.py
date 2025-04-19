from abc import abstractmethod, ABC

class VariantFactory(ABC):
    @abstractmethod
    def create_iso_variant(self, mti, json_data):
        pass