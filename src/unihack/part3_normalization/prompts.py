# ============================================================
# PART 3 PROMPTS
# ============================================================

DESCRIPTION_GENERATION_SYSTEM_PROMPT = """
You are a product-content normalization assistant.

Use ONLY the supplied normalized product information.

Do not invent:
- specifications
- measurements
- materials
- features
- certifications
- performance claims
- compatibility claims
- manufacturer information

Follow the supplied content rules exactly.

The deterministic validation layer will enforce:
- character limits
- casing
- required fields
- approved normalized values
"""


DESCRIPTION_GENERATION_USER_PROMPT = """
Create product descriptions from the normalized product data.

Product:
{product}

Normalized attributes:
{attributes}

Required output fields:
- Invoice Description
- Mobile Description
- Product Title
- Long Description

Use only supplied facts.
"""


def build_description_prompt(
    product,
    attributes,
) -> str:

    return (
        DESCRIPTION_GENERATION_USER_PROMPT
        .format(
            product=product,
            attributes=attributes,
        )
    )