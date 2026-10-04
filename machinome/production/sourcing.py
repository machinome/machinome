"""Explicit supplier listing, distinct from a component requirement."""

from dataclasses import dataclass
from machinome.components import Product, _text


@dataclass(frozen=True)
class Offer:
    product: Product
    supplier: str
    sku: str
    url: str | None = None

    def __init__(self, product, supplier, sku, *, url=None):
        if not isinstance(product, Product):
            raise ValueError("Offer requires a Product")
        _text(supplier, "supplier")
        _text(sku, "sku")
        if url is not None and (
            not isinstance(url, str)
            or not url.startswith(("https://", "http://"))
        ):
            raise ValueError("Offer URL must be http or https")
        for key, value in locals().copy().items():
            if key != "self":
                object.__setattr__(self, key, value)
