import pm4py
def make_image(log_path: str, output_image_path: str):
    log = pm4py.read_xes(log_path)
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    pm4py.save_vis_dfg(dfg, start_activities, end_activities, output_image_path)
    print(f"DFG visual: {output_image_path}")

