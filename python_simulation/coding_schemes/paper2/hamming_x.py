"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

from coding_schemes.base_coding_scheme import CodingScheme
import logging
import math


# Description: Extended Hamming code implementation with added shielding bits.
#             Supports single error correction through parity bits. Adds extra
#             shielding zeros between parity bits for transition reduction.
#
# Inputs:     s_in: list[int] - Input word to encode
#             c_prev: list[int] - Previous code word (not used)
#             M: Optional[int] - Not used
#
# Outputs:    list[int] - Encoded/decoded word where:
#             encode(): [data_bits, parity_bits with shielding]
#             decode(): Corrects single bit errors using parity check matrix

class HammingX(CodingScheme):
    name = "HammingX"
    supports_errors = True
    r = 0


    def get_bus_size(self, k, M=None) -> int:
        for i in range(k):
            if(2**i >= k + i + 1):
                self.r = i
                break
        #n = k + self.r + (self.r - 1)
        n = k + self.r
        return n


    def encode(self, s_in: list[int], c_prev: list[int], M: int = None) -> list[int]:
        
        # Get positions with redundant bits
        pos = self._posRedundantBits(s_in)

        # Calculate parity bits
        c = self._calcParityBits(pos)
            
        logging.debug(f"HammingX encoded word:                  {c}")

        return c


    def decode(self, c: list[int], M: int = None) -> list[int]:
        n = len(c)
        res = 0

        # Calculate parity bits again
        for i in range(self.r):
            val = 0
            for j in range(1, n + 1):
                if(j & (2**i) == (2**i)):
                    val = val ^ int(c[-1 * j])

            res = res + val*(10**i)
            err = int(str(res), 2)

        if err != 0:
            # If error is detected, correct the bit
            c[-1 * err] = 1 - c[-1 * err]

        # Remove redundant bits and convert to list of integers
        s_out = []
        for i in range(1, n + 1):
            if(i != 2**int(math.log2(i))):
                s_out.append(int(c[-1 * i]))

        # Reverse the list to get the original order
        s_out = s_out[::-1]
        
        logging.debug(f"HammingX decoded word:                  {s_out}")
        return s_out


    def _posRedundantBits(self, data) -> list[int]:
        j = 0
        k = 1
        m = len(data)
        res = []

        # If position is power of 2 then insert 0, else append the data
        for i in range(1, m + self.r + 1):
            if(i == 2**j):
                res.append(0)
                j += 1
            else:
                res.append(data[-1 * k])
                k += 1

        # The result is reversed since positions are counted backwards
        return res[::-1]


    def _calcParityBits(self, arr) -> list[int]:
        n = len(arr)

        # For finding rth parity bit, iterate over
        # 0 to r - 1
        for i in range(self.r):
            val = 0
            for j in range(1, n + 1):

                # If position has 1 in ith significant
                # position then Bitwise OR the array value
                # to find parity bit value.
                if (j & (2**i) == (2**i)):
                    val = val ^ int(arr[-1 * j])
                    # -1 * j is given since array is reversed

            # String Concatenation
            # (0 to n - 2^r) + parity bit + (n - 2^r + 1 to n)
            arr[n - (2**i)] = val

        return arr