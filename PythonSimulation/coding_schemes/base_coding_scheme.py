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
    name: str

    @abstractmethod
    def encode(self, *args, **kwargs) -> list[int]:
        """
        Encodes the input data using the specific coding scheme.

        Args:
            *args: Positional arguments specific to the coding scheme.
            **kwargs: Keyword arguments specific to the coding scheme.

        Returns:
            list[int]: Encoded codeword.
        """
        pass

    @abstractmethod
    def decode(self, *args, **kwargs) -> list[int]:
        """
        Decodes the input codeword using the specific coding scheme.

        Args:
            *args: Positional arguments specific to the coding scheme.
            **kwargs: Keyword arguments specific to the coding scheme.

        Returns:
            list[int]: Decoded information word.
        """
        pass