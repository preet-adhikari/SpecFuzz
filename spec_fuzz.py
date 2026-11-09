import argparse
import os
import sys
import json

from dotenv import load_dotenv
from reporting_module.orchestrator import ReportOrchestrator
from reporting_module.reporting_factory.base import ReportingFactory
from spec_factory import SpecFactory
from test_generator.fuzzing_strategy import HappyPathStrategy, MissingRequiredFieldsStrategy, TypeMismatchStrategy
from dataclasses import asdict
import pprint


from test_generator.test_generator import TestGenerator
from test_orchestrator.test_orchestrator import TestOrchestrator
from test_results_storage.storage_factory.base import StorageFactory
from validation_engine.validation_engine import ValidationEngine

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

    parser.add_argument(
        "--reports",
        nargs="+",
        default=["cli"],
        help="List of report formats to generate (e.g., --reports cli json csv)",
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

    # Clearing the results file for testing
    open("test_results.jsonl", "w").close()
    # parser_main(args.spec_file)
    try:
        parser = SpecFactory.peek_parser_type(args.spec_file)
        parsed_data = parser.parse()
        # print(parsed_data)
        # Testing if FuzzingStrategy works
        happy_path = HappyPathStrategy()
        # missing_fields = MissingRequiredFieldsStrategy()
        type_mismatch = TypeMismatchStrategy()
        # print(json.dumps(asdict(parsed_data), indent=4))
        # print(type(parsed_data.operations))
        # print(parsed_data.operations.index("request_body"))

        # result, response = happy_path.generate_payload(schema, expected_response)

        # TODO Pass an optional "seed" parameter to the args.spec_file and then pass it here
        result = TestGenerator(happy_path)
        test_suite = result.generate_test_cases(parsed_data)

        load_dotenv()
        config = {
            "base_directory": os.getenv("FILE_STORAGE_BASE_DIRECTORY"),
            "connection_url": os.getenv("MONGODB_DATABASE_URL"),
            "database_name": "test_db",
        }
        active_storage = StorageFactory.get_storage("all", config)
        orchestrator = TestOrchestrator(
            test_suite=test_suite,
            seed = result.current_seed,
            storage_strategy=active_storage
        )
        final_test_data = orchestrator.execute_tests()
        active_reporters = []
        for format_type in args.reports:
            factory = ReportingFactory(format_type)
            strategy = factory.choose_reporting_strategy()
            active_reporters.append(strategy)

        report_orchestrator = ReportOrchestrator(strategies=active_reporters)

        print(f"Publishing reports for formats: {args.reports}")
        report_orchestrator.publish_all_reports(final_test_data)

        # validator = ValidationEngine("test_results.jsonl")
        # validator.generate_report()

    except ValueError as e:
        print(f"⛔️{e}")
        sys.exit(1)

    except Exception as e:
        raise e
        print(f"An unexpected fatal error occurred: {e}")
        sys.exit(1)        

if __name__ == "__main__":
    main()
