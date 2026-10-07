from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


# ============================================================
# CONSTANT
# ============================================================

BLOCK_SIZE = 16


# ============================================================
# PKCS#7 PADDING
# ============================================================

def pkcs7_pad(data):
    """
    Add PKCS#7 padding so that the data length
    becomes a multiple of 16 bytes.
    """

    padding_length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)

    padding = bytes([padding_length]) * padding_length

    return data + padding


# ============================================================
# PKCS#7 UNPADDING
# ============================================================

def pkcs7_unpad(data):
    """
    Remove PKCS#7 padding.

    Raises ValueError if padding is invalid.
    """

    if len(data) == 0:
        raise ValueError("Invalid padding")

    padding_length = data[-1]

    # Padding must be between 1 and 16
    if padding_length < 1 or padding_length > BLOCK_SIZE:
        raise ValueError("Invalid padding")

    # Check all padding bytes
    expected_padding = bytes([padding_length]) * padding_length

    if data[-padding_length:] != expected_padding:
        raise ValueError("Invalid padding")

    return data[:-padding_length]


# ============================================================
# AES-CBC ENCRYPTION
# ============================================================

def encrypt_message(key, iv, plaintext):
    """
    Encrypt plaintext using AES-CBC.
    """

    padded_plaintext = pkcs7_pad(plaintext)

    cipher = AES.new(
        key,
        AES.MODE_CBC,
        iv
    )

    ciphertext = cipher.encrypt(padded_plaintext)

    return ciphertext


# ============================================================
# PADDING ORACLE
# ============================================================

class PaddingOracle:
    """
    Simulates a vulnerable server.

    The AES key is stored ONLY here.

    The attacker can call check(), but does not
    receive the key.
    """

    def __init__(self, key):

        self.key = key

        # Count total oracle queries
        self.query_count = 0

    def check(self, iv, ciphertext):
        """
        Return:

        True  -> valid PKCS#7 padding
        False -> invalid PKCS#7 padding
        """

        self.query_count += 1

        try:

            cipher = AES.new(
                self.key,
                AES.MODE_CBC,
                iv
            )

            decrypted = cipher.decrypt(ciphertext)

            # This is the vulnerable operation.
            # The oracle reveals whether padding is valid.
            pkcs7_unpad(decrypted)

            return True

        except ValueError:

            return False


# ============================================================
# PADDING ORACLE ATTACK
# ============================================================

def recover_block(previous_block, target_block, oracle):
    """
    Recover one plaintext block.

    previous_block:
        IV or previous ciphertext block

    target_block:
        ciphertext block that we want to decrypt

    oracle:
        padding oracle

    IMPORTANT:
        The AES key is NOT available here.
    """

    # --------------------------------------------------------
    # Intermediate bytes:
    #
    # I = AES_decrypt(target_block)
    #
    # Plaintext:
    #
    # P = I XOR previous_block
    # --------------------------------------------------------

    intermediate = bytearray(BLOCK_SIZE)

    plaintext = bytearray(BLOCK_SIZE)

    # --------------------------------------------------------
    # Work from RIGHT to LEFT
    # --------------------------------------------------------

    for padding_value in range(1, BLOCK_SIZE + 1):

        byte_index = BLOCK_SIZE - padding_value

        found = False

        # ----------------------------------------------------
        # Try all 256 possible values
        # ----------------------------------------------------

        for guess in range(256):

            modified_previous = bytearray(previous_block)

            # ------------------------------------------------
            # Set already recovered bytes to the required
            # padding value.
            #
            # Example:
            #
            # padding = 2
            #
            # ... XX XX 02 02
            # ------------------------------------------------

            for j in range(
                BLOCK_SIZE - 1,
                byte_index,
                -1
            ):

                modified_previous[j] = (
                    intermediate[j] ^ padding_value
                )

            # ------------------------------------------------
            # Modify the current byte
            # ------------------------------------------------

            modified_previous[byte_index] = (
                guess ^ padding_value
            )

            # ------------------------------------------------
            # Ask the oracle
            # ------------------------------------------------

            valid = oracle.check(
                bytes(modified_previous),
                target_block
            )

            if valid:

                # ------------------------------------------------
                # Special check for padding = 1
                #
                # This reduces false positives caused by the
                # original ciphertext already ending in valid
                # multi-byte padding.
                # ------------------------------------------------

                if padding_value == 1:

                    test_previous = bytearray(
                        modified_previous
                    )

                    # Change the second-last byte.
                    test_previous[BLOCK_SIZE - 2] ^= 1

                    still_valid = oracle.check(
                        bytes(test_previous),
                        target_block
                    )

                    # For genuine 01 padding, changing the
                    # second-last byte should NOT destroy
                    # the valid 01 padding.
                    if not still_valid:
                        continue

                # ------------------------------------------------
                # We found the intermediate byte.
                # ------------------------------------------------

                intermediate[byte_index] = guess

                # ------------------------------------------------
                # P = I XOR original previous block
                # ------------------------------------------------

                plaintext[byte_index] = (
                    intermediate[byte_index]
                    ^ previous_block[byte_index]
                )

                print(
                    f"    Byte {byte_index:2d}: "
                    f"{plaintext[byte_index]:02x} "
                    f"({chr(plaintext[byte_index])!r})"
                )

                found = True
                break

        if not found:

            raise RuntimeError(
                f"Could not recover byte {byte_index}"
            )

    return bytes(plaintext)


# ============================================================
# COMPLETE PADDING ORACLE ATTACK
# ============================================================

def padding_oracle_attack(iv, ciphertext, oracle):
    """
    Recover the complete plaintext.

    The AES key is NOT passed to this function.
    """

    # --------------------------------------------------------
    # Split ciphertext into 16-byte blocks
    # --------------------------------------------------------

    ciphertext_blocks = [
        ciphertext[i:i + BLOCK_SIZE]
        for i in range(
            0,
            len(ciphertext),
            BLOCK_SIZE
        )
    ]

    # --------------------------------------------------------
    # In CBC:
    #
    # C0 = IV
    #
    # So create:
    #
    # [IV, C1, C2, C3, ...]
    # --------------------------------------------------------

    blocks = [iv] + ciphertext_blocks

    recovered_plaintext = b""

    # --------------------------------------------------------
    # Attack every ciphertext block
    # --------------------------------------------------------

    for block_number in range(
        1,
        len(blocks)
    ):

        previous_block = blocks[block_number - 1]

        target_block = blocks[block_number]

        print()
        print("=" * 60)
        print(f"Attacking ciphertext block {block_number}")
        print("=" * 60)

        recovered_block = recover_block(
            previous_block,
            target_block,
            oracle
        )

        recovered_plaintext += recovered_block

        print()
        print(
            "Recovered block:",
            recovered_block
        )

    # --------------------------------------------------------
    # Remove PKCS#7 padding
    # --------------------------------------------------------

    recovered_plaintext = pkcs7_unpad(
        recovered_plaintext
    )

    return recovered_plaintext


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 60)
    print("PADDING ORACLE ATTACK - AES CBC")
    print("=" * 60)

    # --------------------------------------------------------
    # SECRET KEY
    #
    # IMPORTANT:
    # This key is only available to the encryption/oracle
    # side.
    #
    # The attack function never receives this key.
    # --------------------------------------------------------

    key = get_random_bytes(16)

    # --------------------------------------------------------
    # Random IV
    # --------------------------------------------------------

    iv = get_random_bytes(16)

    # --------------------------------------------------------
    # Original plaintext
    #
    # You can change this.
    # The attack is NOT hard-coded to this plaintext.
    # --------------------------------------------------------

    plaintext = (
        b"Padding oracle attacks show why "
        b"authenticated encryption is important."
    )

    # --------------------------------------------------------
    # Encrypt message
    # --------------------------------------------------------

    ciphertext = encrypt_message(
        key,
        iv,
        plaintext
    )

    print()
    print("Original plaintext:")
    print(plaintext)

    print()
    print("IV:")
    print(iv.hex())

    print()
    print("Ciphertext:")
    print(ciphertext.hex())

    # --------------------------------------------------------
    # Create vulnerable padding oracle
    #
    # The oracle knows the key.
    # The attacker does NOT.
    # --------------------------------------------------------

    oracle = PaddingOracle(key)

    # --------------------------------------------------------
    # START ATTACK
    #
    # Notice:
    #
    # padding_oracle_attack()
    #
    # receives:
    #     IV
    #     ciphertext
    #     oracle
    #
    # It DOES NOT receive:
    #     key
    # --------------------------------------------------------

    recovered_plaintext = padding_oracle_attack(
        iv,
        ciphertext,
        oracle
    )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("ATTACK COMPLETE")
    print("=" * 60)

    print()
    print("Original plaintext:")
    print(plaintext)

    print()
    print("Recovered plaintext:")
    print(recovered_plaintext)

    print()
    print("Plaintexts match:")
    print(plaintext == recovered_plaintext)

    print()
    print("Total oracle queries:")
    print(oracle.query_count)

    print()
    print("=" * 60)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
