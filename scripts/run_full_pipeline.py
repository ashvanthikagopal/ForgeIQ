from pathlib import Path
import sys

# Make src importable when running this file directly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from unihack.part1_foundation.data_loader import load_part1_data
from unihack.part2_classification.pipeline import run_part2
from unihack.part3_normalization.pipeline import run_part3_from_part2
from unihack.part4_enrichment_qa.pipeline import run_part4_from_part3


def main():

    print("=" * 70)
    print("                 FORGEIQ FULL PIPELINE")
    print("=" * 70)

    # =========================================================
    # PART 1
    # =========================================================

    print("\n[1/4] Loading actual input data...")

    part1_data = load_part1_data()

    print("      ✓ Part 1 completed")
    print(f"      Type: {type(part1_data).__name__}")

    # Check actual input size
    if hasattr(part1_data, "sample_input"):
        print(f"      Products: {len(part1_data.sample_input)}")

    # =========================================================
    # PART 2
    # =========================================================

    print("\n[2/4] Running Part 2...")

    part2_results = run_part2(
        part1_data
    )

    print("      ✓ Part 2 completed")
    print(f"      Products processed: {len(part2_results)}")

    # =========================================================
    # PART 3
    # =========================================================

    print("\n[3/4] Running Part 3...")

    part3_results = run_part3_from_part2(
        part2_results=part2_results,
        part1_data=part1_data,
    )

    print("      ✓ Part 3 completed")
    print(f"      Products processed: {len(part3_results)}")

    # =========================================================
    # PART 4
    # =========================================================

    print("\n[4/4] Running Part 4...")

    # These are the attributes Part 4 should ensure are present.
    #
    # Adjust this list if your project specification defines
    # additional required attributes.
    required_attributes = [
        "manufacturer",
        "brand",
    ]

    part4_results = run_part4_from_part3(
        part3_results,
        required_attributes=required_attributes,
    )

    print("      ✓ Part 4 completed")
    print(f"      Products processed: {len(part4_results)}")

    # =========================================================
    # FINAL VALIDATION
    # =========================================================

    print("\n" + "=" * 70)
    print("                 PIPELINE VERIFICATION")
    print("=" * 70)

    print(f"\nPart 1 products : {len(part1_data.sample_input)}")
    print(f"Part 2 products : {len(part2_results)}")
    print(f"Part 3 products : {len(part3_results)}")
    print(f"Part 4 products : {len(part4_results)}")

    # Make sure every stage processed the same number of products
    input_count = len(part1_data.sample_input)

    assert len(part2_results) == input_count, (
        "Part 2 output count does not match Part 1 input count"
    )

    assert len(part3_results) == input_count, (
        "Part 3 output count does not match Part 1 input count"
    )

    assert len(part4_results) == input_count, (
        "Part 4 output count does not match Part 1 input count"
    )

    print("\n✓ Part 1 → Part 2 connection verified")
    print("✓ Part 2 → Part 3 connection verified")
    print("✓ Part 3 → Part 4 connection verified")
    print("✓ Product counts preserved")
    print("\n🎉 COMPLETE PIPELINE WORKS WITH ACTUAL DATA!")
    print("=" * 70)

    # =========================================================
    # SHOW SAMPLE OUTPUT
    # =========================================================

    print("\nSample Part 4 output:")
    print("-" * 70)

    for i, result in enumerate(part4_results[:3], start=1):

        print(f"\nProduct {i}:")

        if isinstance(result, dict):

            for key, value in result.items():

                print(f"  {key}: {value}")

        else:

            print(result)


if __name__ == "__main__":
    main()