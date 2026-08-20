"""Part 4's prompt templates — Phase G (manufacturer-source enrichment)
and Phase H (validation/compliance QA pass)."""

ENRICHMENT_SYSTEM_PROMPT = """\
You fill missing product attributes using ONLY retrieved content that
originates from the manufacturer's own website or official documentation.
You explicitly reject and ignore any retrieved content from marketplaces
(Amazon, eBay, etc.) or distributor/reseller sites, per sourcing policy.
You never fabricate a spec when no qualifying source supports it."""

ENRICHMENT_USER_PROMPT = """\
PRODUCT: Brand="{brand}", MPN="{mpn}", Classpath="{classpath}"
MISSING ATTRIBUTES: {missing_attribute_list}

RETRIEVED CONTENT (each chunk tagged with its source domain/type):
{retrieved_chunks_with_source_type_tag}

TASK:
1. For each retrieved chunk, first check: is source_type ==
   "manufacturer_official"? If not, DISCARD it entirely regardless of
   relevance.
2. Using only manufacturer-sourced chunks, fill any missing attribute you
   can support with direct evidence, using the LOV's permitted normalized
   value where applicable.
3. If no qualifying source supports a field, return "not_available" — do
   not lower your standards to fill every field.

Return JSON array:
[
  {{ "attribute": "...", "value": "...", "source_url": "...",
    "confidence": 0-1, "method": "inferred_manufacturer_source" }}
]"""

VALIDATION_SYSTEM_PROMPT = """\
You are a QA pass that checks a generated product record against Unilog's
content rules before it is scored or shipped."""

VALIDATION_USER_PROMPT = """\
GENERATED RECORD:
{full_generated_record_json}

RULES TO CHECK:
- Every attribute value must appear in this classpath's LOV permitted
  values list: {permitted_values_lookup}
- Every unit-bearing value must use the approved UOM abbreviation and a
  space before the unit: {uom_rules}
- Manufacturer/brand strings must exactly match the canonical form
  (including (R)/(TM) and legal suffixes): {manufacturer_brand_lookup}
- Field character limits: {char_limits_per_field}
- Field casing rules: {casing_rules_per_field}
- No field should contain a placeholder string
  ("-- Unbranded --", "-- No Unilog Brand --", "-- No DIB Brand --")

TASK:
Return a JSON array of violations found, each with field, issue, and
severity. If a field is blank in the SOURCE data itself (not something your
pipeline should have filled), flag it as "source_gap", severity "low", not
as an error.

Return JSON:
[
  {{ "field": "...", "issue": "...", "severity": "low|medium|high",
    "type": "lov_mismatch|uom_violation|manufacturer_mismatch|
              char_limit_exceeded|casing_violation|placeholder_detected|
              source_gap" }}
]"""