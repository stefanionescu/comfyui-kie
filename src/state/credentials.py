"""The KIE API key, kept out of every representation."""

from dataclasses import field, dataclass


@dataclass(frozen=True, slots=True)
class Credential:
    """A KIE API key that only a request to KIE reads.

    Attributes:
        value: The key; the dataclass representation leaves it out.

    """

    value: str = field(repr=False)


__all__ = ['Credential']
