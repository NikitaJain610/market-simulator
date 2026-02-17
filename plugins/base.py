# plugins/base.py
# Niki

from abc import ABC, abstractmethod


class ProtocolPlugin(ABC):

    @abstractmethod
    def create_session_logic(self):
        pass

    @abstractmethod
    def decode(self, raw_bytes: bytes):
        pass

    @abstractmethod
    def map_to_canonical(self, protocol_message):
        pass

    @abstractmethod
    def encode_execution(self, canonical_execution):
        pass
