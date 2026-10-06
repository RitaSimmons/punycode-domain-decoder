import unittest

from punycode_domain_decoder import decode_domain
from punycode_domain_decoder.core import PunycodeDecodeError, _decode_label


class TestDecodeLabel(unittest.TestCase):
    def test_ace_label_decodes(self):
        # "münchen" in ACE form
        self.assertEqual(_decode_label("xn--mnchen-3ya"), "münchen")

    def test_plain_ascii_label_passes_through(self):
        self.assertEqual(_decode_label("example"), "example")

    def test_uppercase_prefix_is_recognized(self):
        # RFC 3490 requires case-insensitive prefix matching
        self.assertEqual(_decode_label("XN--mnchen-3ya"), "münchen")
        self.assertEqual(_decode_label("Xn--mnchen-3ya"), "münchen")

    def test_bare_prefix_without_data_raises(self):
        with self.assertRaises(PunycodeDecodeError):
            _decode_label("xn--")

    def test_malformed_punycode_raises(self):
        # Invalid base-36 run that the codec rejects
        with self.assertRaises(PunycodeDecodeError):
            _decode_label("xn--_")


class TestDecodeDomain(unittest.TestCase):
    def test_single_ace_label(self):
        self.assertEqual(decode_domain("xn--mnchen-3ya"), "münchen")

    def test_multi_label_domain(self):
        # münchen.example in ACE form
        self.assertEqual(
            decode_domain("xn--mnchen-3ya.example"),
            "münchen.example",
        )

    def test_multiple_ace_labels(self):
        # münchen.straße in ACE form
        self.assertEqual(
            decode_domain("xn--mnchen-3ya.xn--strae-oqa"),
            "münchen.straße",
        )

    def test_empty_string_returns_empty(self):
        self.assertEqual(decode_domain(""), "")

    def test_leading_dot_raises(self):
        with self.assertRaises(PunycodeDecodeError):
            decode_domain(".xn--mnchen-3ya")

    def test_trailing_dot_raises(self):
        with self.assertRaises(PunycodeDecodeError):
            decode_domain("xn--mnchen-3ya.")

    def test_consecutive_dots_raises(self):
        with self.assertRaises(PunycodeDecodeError):
            decode_domain("a..b")

    def test_non_string_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            decode_domain(b"xn--mnchen-3ya")  # type: ignore[arg-type]

    def test_malformed_punycode_propagates(self):
        with self.assertRaises(PunycodeDecodeError):
            decode_domain("xn--_")


if __name__ == "__main__":
    unittest.main()
