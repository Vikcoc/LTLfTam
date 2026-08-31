from Declare4Py.D4PyEventLog import D4PyEventLog
from Declare4Py.ProcessMiningTasks.ConformanceChecking.LTLAnalyzer import LTLAnalyzer

def run_check(log_path: str, ltl_models: list):
    event_log = D4PyEventLog()
    event_log.parse_xes_log(log_path)

    analyzer = LTLAnalyzer(event_log, ltl_models)
    results_df = analyzer.run_multiple_models()

    print(results_df)