"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from coding_schemes.base_coding_scheme import CodingScheme
from logging_config import configure_logging

# Configure logging
configure_logging()


class DAPBI(CodingScheme):
    name = "DAPBI"

    def encode(self, s):
        pass
    

    def decode(self, c):
        pass