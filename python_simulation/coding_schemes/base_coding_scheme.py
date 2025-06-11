"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from abc import ABC, abstractmethod


class CodingScheme(ABC):
    """
    Implements: Abstract base class defining the interface for all coding schemes,
                providing common functionality for encoding/decoding binary sequences
                and error handling for transmission simulation.

    Args:
        None (initialization handled by subclasses)

    Returns:
        None (abstract class cannot be instantiated directly)
    """
    name: str
    supports_errors: bool = False  

    def __init__(self):
        self.s_prev = None  
        self.c_prev = None
    

    @abstractmethod
    def get_bus_size(self, *args, **kwargs) -> int:
        """
        Implements: Calculation of the required bus width for the coding scheme
                    based on input parameters like word length and scheme-specific settings.

        Args:
            *args: Variable positional arguments specific to each coding scheme
            **kwargs: Variable keyword arguments specific to each coding scheme

        Returns:
            int: Required bus width in bits for the coding scheme.
        """
        pass
    

    @abstractmethod
    def encode(self, *args, **kwargs) -> list[int]:
        """
        Implements: Encoding of input binary words into codewords using the specific
                    coding scheme algorithm to reduce transitions or add error correction.

        Args:
            *args: Variable positional arguments specific to each coding scheme
            **kwargs: Variable keyword arguments specific to each coding scheme

        Returns:
            list[int]: Encoded codeword as a list of binary digits.
        """
        pass
    

    @abstractmethod
    def decode(self, *args, **kwargs) -> list[int]:
        """
        Implements: Decoding of received codewords back to original binary words,
                    including error detection and correction if supported by the scheme.

        Args:
            *args: Variable positional arguments specific to each coding scheme
            **kwargs: Variable keyword arguments specific to each coding scheme

        Returns:
            list[int]: Decoded binary word as a list of binary digits.
        """
        pass
    

    def apply_error(self, codeword, error_vector):
        """
        Implements: Application of transmission errors to codewords using XOR operation
                    for schemes that support error detection and correction testing.

        Args:
            codeword (list[int]): Original codeword to apply errors to
            error_vector (list[int]): Binary error pattern to apply via XOR

        Returns:
            list[int]: Codeword with errors applied, or original codeword if errors not supported.
        """
        if not self.supports_errors:
            return codeword
            
        if len(codeword) != len(error_vector):
            raise ValueError("Codeword and error vector must have the same length")
            
        return [c ^ e for c, e in zip(codeword, error_vector)]