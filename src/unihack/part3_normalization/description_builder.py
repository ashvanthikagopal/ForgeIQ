from __future__ import annotations

from .models import (
    DescriptionField,
    NormalizedProduct,
)


# ============================================================
# GET LEAF CLASS
# ============================================================

def get_leaf_class(
    classpath: str,
) -> str:

    if not classpath:
        return ""

    parts = [
        part.strip()
        for part in classpath.split(">")
        if part.strip()
    ]

    if not parts:
        return ""

    return parts[-1]


# ============================================================
# GET ATTRIBUTE
# ============================================================

def get_attribute(
    product: NormalizedProduct,
    name: str,
) -> str:

    for attribute in product.attributes:

        if (
            attribute.attribute.lower()
            == name.lower()
        ):

            return (
                attribute.normalized_value
            )

    return ""


# ============================================================
# GET ALL ATTRIBUTES
# ============================================================

def get_attribute_pairs(
    product: NormalizedProduct,
) -> list[str]:

    values = []

    for attribute in (
        product.attributes
    ):

        value = (
            attribute.normalized_value
        )

        if value:

            values.append(
                f"{attribute.attribute} "
                f"{value}"
            )

    return values


# ============================================================
# INVOICE DESCRIPTION
# ============================================================

def build_invoice_description(
    product: NormalizedProduct,
) -> DescriptionField:

    parts = []

    leaf = get_leaf_class(
        product.classpath
    )

    if leaf:
        parts.append(
            leaf
        )

    if product.mpn:
        parts.append(
            product.mpn
        )

    for attribute in (
        product.attributes
    ):

        if attribute.normalized_value:

            parts.append(
                attribute.normalized_value
            )

    value = " ".join(
        parts
    ).upper()

    # --------------------------------------------------------
    # Maximum 40 characters
    # --------------------------------------------------------

    if len(value) > 40:

        value = value[:40].rstrip()

    return DescriptionField(

        value=value,

        char_count=len(value),

        within_limit=(
            len(value) <= 40
        ),

        casing_valid=(
            value == value.upper()
        ),

        needs_review=False,
    )


# ============================================================
# MOBILE DESCRIPTION
# ============================================================

def build_mobile_description(
    product: NormalizedProduct,
) -> DescriptionField:

    parts = []

    if product.brand:

        parts.append(
            product.brand
        )

    leaf = get_leaf_class(
        product.classpath
    )

    if leaf:

        parts.append(
            leaf
        )

    if product.mpn:

        parts.append(
            product.mpn
        )

    for attribute in (
        product.attributes
    ):

        if attribute.normalized_value:

            parts.append(
                f"{attribute.attribute}: "
                f"{attribute.normalized_value}"
            )

    value = ", ".join(
        parts
    )

    # --------------------------------------------------------
    # Hard maximum
    # --------------------------------------------------------

    if len(value) > 80:

        value = value[:80].rstrip(
            " ,"
        )

    within_limit = (
        60 <= len(value) <= 80
    )

    return DescriptionField(

        value=value,

        char_count=len(value),

        within_limit=within_limit,

        casing_valid=True,

        needs_review=(
            not within_limit
        ),

        review_reason=(
            "Mobile Description must contain "
            "60–80 characters."
            if not within_limit
            else None
        ),
    )


# ============================================================
# PRODUCT TITLE
# ============================================================

def build_product_title(
    product: NormalizedProduct,
) -> DescriptionField:

    parts = []

    if product.brand:

        parts.append(
            product.brand
        )

    leaf = get_leaf_class(
        product.classpath
    )

    if leaf:

        parts.append(
            leaf
        )

    if product.mpn:

        parts.append(
            product.mpn
        )

    for attribute in (
        product.attributes
    ):

        if attribute.normalized_value:

            parts.append(
                f"{attribute.attribute}: "
                f"{attribute.normalized_value}"
            )

    value = " ".join(
        parts
    )

    return DescriptionField(

        value=value,

        char_count=len(value),

        within_limit=True,

        casing_valid=True,
    )


# ============================================================
# LONG DESCRIPTION
# ============================================================

def build_long_description(
    product: NormalizedProduct,
) -> DescriptionField:

    parts = []

    if product.brand:

        parts.append(
            product.brand
        )

    leaf = get_leaf_class(
        product.classpath
    )

    if leaf:

        parts.append(
            leaf
        )

    if product.mpn:

        parts.append(
            f"Model: {product.mpn}"
        )

    for attribute in (
        product.attributes
    ):

        if attribute.normalized_value:

            parts.append(
                f"{attribute.attribute}: "
                f"{attribute.normalized_value}"
            )

    value = ". ".join(
        parts
    )

    if value:

        value += "."

    return DescriptionField(

        value=value,

        char_count=len(value),

        within_limit=True,

        casing_valid=True,
    )


# ============================================================
# MARKETING COPY
# ============================================================

def build_marketing_copy(
    product: NormalizedProduct,
) -> DescriptionField:

    # --------------------------------------------------------
    # No unsupported claims.
    #
    # This uses only facts already present in the normalized
    # product.
    # --------------------------------------------------------

    title = build_product_title(
        product
    ).value

    attributes = get_attribute_pairs(
        product
    )

    if attributes:

        value = (
            f"{title}. "
            f"Key attributes: "
            f"{', '.join(attributes)}."
        )

    else:

        value = title

    return DescriptionField(

        value=value,

        char_count=len(value),

        within_limit=True,

        casing_valid=True,
    )


# ============================================================
# BUILD ALL
# ============================================================

def build_descriptions(
    product: NormalizedProduct,
):

    return {

        "invoice_desc":
            build_invoice_description(
                product
            ),

        "mobile_desc":
            build_mobile_description(
                product
            ),

        "product_title":
            build_product_title(
                product
            ),

        "long_description":
            build_long_description(
                product
            ),

        "marketing_copy":
            build_marketing_copy(
                product
            ),
    }