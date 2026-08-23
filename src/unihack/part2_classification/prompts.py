CLASSIFICATION_SYSTEM_PROMPT = """
You classify industrial/consumer product rows into a
fixed Classpath taxonomy supplied to you.

You NEVER invent a Classpath that is not present
in the supplied allowed list.

If nothing fits well, return your best candidate
with low confidence instead of forcing a match.
"""


def build_classification_prompt(
    part_desc: str,
    mpn: str,
    manufacturer: str,
    classpath_list: list[str],
) -> str:

    allowed = "\n".join(
        f"- {value}"
        for value in classpath_list
    )

    return f"""
PRODUCT ROW:

Part_Desc: "{part_desc}"

Mfg_Part_Num: "{mpn}"

Manufacturer:
"{manufacturer}"


ALLOWED CLASSPATHS:

{allowed}


TASK:

1. Choose the single best-fitting Classpath
   from the allowed list.

2. If the description is ambiguous, give the
   best candidate with confidence below 0.5.

3. Provide up to 3 alternative candidates.

4. Do not invent a Classpath.


Return JSON only:

{{
    "classpath": "...",
    "confidence": 0.0,
    "alternative_candidates": [],
    "reasoning": "..."
}}
"""


# ============================================================
# ATTRIBUTE PROMPT
# ============================================================

ATTRIBUTE_SYSTEM_PROMPT = """
You extract product attributes strictly from
the supplied source text.

You ONLY output attribute values that occur in
the permitted normalized values supplied for
that attribute.

Never invent an attribute value.

Never guess a numeric value that is not stated
or clearly implied in the source text.
"""


def build_attribute_prompt(
    classpath: str,
    part_desc: str,
    attributes: dict[str, list[str]],
) -> str:

    attribute_text = []

    for name, values in attributes.items():

        permitted = ", ".join(
            values
        )

        attribute_text.append(
            f"{name}: [{permitted}]"
        )

    attribute_list = "\n".join(
        attribute_text
    )

    return f"""
CLASSPATH:

{classpath}


SOURCE TEXT:

"{part_desc}"


ATTRIBUTES AND PERMITTED VALUES:

{attribute_list}


TASK:

For each attribute:

1. Extract a value only when supported
   by the source text.

2. Use the EXACT normalized permitted
   value.

3. For unit-bearing values, preserve the
   raw value and set:

   needs_unit_normalization = true

4. If the source does not support the
   attribute, omit it.


Return JSON:

{{
    "attributes": [
        {{
            "attribute": "...",
            "value": "...",
            "confidence": 0.0,
            "needs_unit_normalization": false,
            "raw_text_span": "..."
        }}
    ]
}}
"""