"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from abc import ABC, abstractmethod


# Description: Defines an abstract base class for coding schemes. 
#              Subclasses must implement the `encode` and `decode` methods, 
#              which handle the encoding and decoding of binary sequences.

class CodingScheme(ABC):
    name: str
    supports_errors: bool = False  # Default to not supporting errors


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