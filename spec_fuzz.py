import argparse
import os
import sys

from spec_factory import SpecFactory

def main():
    """

    This function handles the arguments for the CLI command used. It makes sure that the file exists and checks the extension of the file.

    """
    parser = argparse.ArgumentParser(
        description="SpecFuzz🔍: An automated API Spec Compliance and Robustness Testing System."
    )

    parser.add_argument(
        "spec_file",
        help="📂 The path to the OpenAPI specification file (YAML or JSON)",
        type=str,
    )

    # Parse the arguments
    args = parser.parse_args()

    # Check if file exists
    if not os.path.exists(args.spec_file):
        print(f"⛔️Error: The file '{args.spec_file}' was not found.")
        sys.exit(1)

    if not args.spec_file.endswith((".yaml", ".yml", ".json")):
        print(f"Warning: '{args.spec_file}' does not look like a YAML or JSON file.")

    print(f"Loading specification from: {args.spec_file}")
    print("Initializing the parser...")

    # parser_main(args.spec_file)
    try:
        parser = SpecFactory.peek_parser_type(args.spec_file)
        parsed_data = parser.parse(args.spec_file)


    except ValueError as e:
        print(f"⛔️{e}")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected fatal error occurred: {e}")
        sys.exit(1)        

if __name__ == "__main__":
    main()
