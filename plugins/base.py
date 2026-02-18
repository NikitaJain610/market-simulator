# plugins/base.py

from abc import ABC, abstractmethod


class ProtocolPlugin(ABC):

    @abstractmethod
    def create_session_logic(self):
        pass

    @abstractmethod
    def decode(self, raw_bytes):
        pass

    @abstractmethod
    def map_to_canonical(self, msg):
        pass

    @abstractmethod
    def encode_event(self, event):
        pass

    @abstractmethod
    def encode_logon_ack(self):
        pass
