"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from abc import ABC, abstractmethod


# Description: Abstract base class for all coding schemes. Defines interface and
#             common functionality for encoding/decoding binary sequences.
#             Handles error injection for supported schemes.
#
# Inputs:     s_in: list[int] - Input word to encode
#             c_prev: list[int] - Previous code word
#             codeword: list[int] - Word to apply errors to
#             error_vector: list[int] - Error pattern to apply
#
# Outputs:    get_bus_size(): int - Required bus width
#             encode(): list[int] - Encoded word
#             decode(): list[int] - Decoded word
#             apply_error(): list[int] - Word with errors applied

class CodingScheme(ABC):
    name: str
    supports_errors: bool = False  

    def __init__(self):
        self.s_prev = None  
        self.c_prev = None
    

    @abstractmethod
    def get_bus_size(self, *args, **kwargs) -> int:
        pass
    

    @abstractmethod
    def encode(self, *args, **kwargs) -> list[int]:
        pass
    

    @abstractmethod
    def decode(self, *args, **kwargs) -> list[int]:
        pass
    

    def apply_error(self, codeword, error_vector):
        if not self.supports_errors:
            return codeword
            
        if len(codeword) != len(error_vector):
            raise ValueError("Codeword and error vector must have the same length")
            
        return [c ^ e for c, e in zip(codeword, error_vector)]