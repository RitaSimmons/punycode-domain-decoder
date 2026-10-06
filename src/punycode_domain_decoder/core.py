"""Pure-Python Punycode domain name decoder.

This module implements full-domain decoding by reusing the standard
library's single-label Punycode decoder (``encodings.punycode``).

The standard library has a private helper ``ToUnicode`` that does this
job, but it is intentionally undocumented and may change between Python
versions. This module re-implements the same algorithm in terms of the
stable, public ``punycode_decode`` codec so that behavior is predictable
and testable.
"""

from __future__ import annotations


class PunycodeDecodeError(ValueError):
    """Raised when input is malformed according to this library's contract."""


def _decode_label(label: str) -> str:
    """Decode a single label, handling both ACE (``xn--``) and plain labels.

    The caller is responsible for not passing an empty string. Empty
    labels are structurally invalid and are handled at the domain level.

    The lowercase-normalizing step is here because a caller may pass
    a label with stray uppercase characters (``XN--`` or ``Xn--``). RFC
    3490 Section 4 requires comparison on the ASCII form, and the prefix
    comparison must be case-insensitive.
    """
    prefix = "xn--"
    plen = len(prefix)
    if len(label) < plen:
        return label

    # ASCII lowercase. ``.lower()`` on ASCII letters is a subset of the
    # RFC 3454 B.2 mapping for this case, and because we only compare
    # against an ASCII prefix it is sufficient here. We do not apply
    # full Unicode casefolding because this decoder is not a DNS
    # verifier; it decodes what it is given.
    lowered = label[:plen].lower()
    if lowered != prefix:
        return label

    rest = label[plen:]
    # A bare "xn--" with no code points is not a valid ACE label.
    if not rest:
        raise PunycodeDecodeError("invalid ACE label: missing encoded data")

    try:
        decoded = rest.encode("ascii").decode("punycode")
    except (UnicodeDecodeError, UnicodeError) as exc:
        # ``punycode_decode`` raises UnicodeDecodeError or UnicodeError
        # for malformed base-36 digit runs and bad insertion orders.
        # We re-raise as our own type so callers do not have to catch
        # the stdlib codec error directly.
        raise PunycodeDecodeError(f"malformed punycode in label: {exc}") from exc

    return decoded


def decode_domain(domain: str) -> str:
    """Decode an internationalized domain name from ACE to Unicode.

    The input must already be in ASCII / ACE form (each internationalized
    label prefixed with ``xn--``). Non-ACE labels pass through unchanged.

    Label boundaries are the ASCII dot (``.``). Empty labels (consecutive
    dots, or a leading/trailing dot) are rejected. This is stricter than
    what the underlying codec tolerates, because a domain name with an
    empty label has no well-formed Unicode representation.
    """
    if not isinstance(domain, str):
        raise TypeError(f"expected str, got {type(domain).__name__}")

    if not domain:
        return ""

    labels = domain.split(".")
    decoded_labels = []
    for label in labels:
        if not label:
            raise PunycodeDecodeError("empty label in domain")
        decoded_labels.append(_decode_label(label))

    return ".".join(decoded_labels)
