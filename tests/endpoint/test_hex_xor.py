from diana.endpoint import hex_xor as xor

def test_hex_xor():

    h1 = "ff"
    h2 = "00"

    assert xor(h1, h2) == "ff"

    h1 = "1f"
    h2 = "1f"

    assert xor(h1, h2) == "00"


if __name__ == "__main__":

    test_hex_xor()