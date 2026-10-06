# punycode-domain-decoder

Decodes internationalized domain names from ACE form (`xn--...` labels) to Unicode using only the Python standard library.

```python
from punycode_domain_decoder import decode_domain

print(decode_domain("xn--mnchen-3ya.example"))  # münchen.example
```

## Why this exists

Python ships `encodings.punycode`, a single-label decoder, but not a documented whole-domain decoder. The private `encodings.idna.ToUnicode` does the job but is undocumented and may change between versions. This library wraps the stable single-label codec with label-boundary handling and input validation so callers get a predictable, testable whole-domain decode.

The trade-off: this library decodes only. It does not validate host syntax beyond rejecting empty labels, and it does not encode. Keeping the surface small means the behavior is easy to reason about.

## Edge cases

- Empty labels (leading, trailing, or consecutive dots) are rejected. A trailing dot is common in DNS zone files but is not accepted here.
- A bare `xn--` with no encoded data is rejected.
- Malformed Punycode runs are re-raised as `PunycodeDecodeError`, a subclass of `ValueError`, rather than the stdlib codec's `UnicodeDecodeError`.
- The `xn--` prefix match is case-insensitive per RFC 3490; the encoded payload itself is not case-normalized.

## Exported names

- `decode_domain(domain: str) -> str` — the decoder.
- `PunycodeDecodeError` — raised on malformed input, subclass of `ValueError`.
