"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""


# Description: Checks if the input to the encoder is the same as the output of the decoder
# Inputs:
#              info_word (array): Initial information word (length - k)
#              output (array): Decoded word (length - k)
# Outputs:
#              isEqual (bool): True only if info_word == output
def Comparator(info_word, output):
    for i in range(len(info_word)):
        if info_word[i] != output[i]:
            return False
    return True

