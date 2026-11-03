from test_results_storage.base import BaseStorageStrategy


class ReportingModule:
    def __init__(self, storage_strategy: BaseStorageStrategy) -> None:
        self._storage_strategy = storage_strategy

    def generate_report(self, test_run_id: str):
        raw_report_dictionary = self._storage_strategy.get_test_run_details(test_run_id)
        test_success_checklist = []
        report = {}
        for result in raw_report_dictionary.get("results", {}):
            test_success_checklist.append(result["passed"])
        report["is_success"] = test_success_checklist
        return report
