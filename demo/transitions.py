from typing import Dict, Tuple, Iterable

def build_transitions(dfg: Dict[Tuple[str, str], int],
                      start_activities: Iterable[str],
                      end_activities: Iterable[str],
                      fr_name: str,
                      always_action: str,
                      start_action: str,
                      end_action: str) -> str:

    rules = ['// 1 Starts']

    for act in start_activities:
        rules.append(
                f"rule Start_{act}:\n"
                f"    [ Fr(~{fr_name}) ]\n"
                f"  --[ {always_action.capitalize()}(~{fr_name}), {act.capitalize()}(~{fr_name}), {start_action.capitalize()}(~{fr_name}) ]->\n"
                f"    [ State_{act}(~{fr_name}) ]\n"
            )

    rules.append('// 2. Transitions')

    # it's ok to repeat states because a process will only go one way
    for (src, tgt) in dfg.keys():
        rules.append(
            f"rule {src}_{tgt}:\n"
            f"    [ State_{src}({fr_name}) ]\n"
            f"  --[ {always_action.capitalize()}({fr_name}), {tgt.capitalize()}({fr_name}) ]->\n"
            f"    [ State_{tgt}({fr_name}) ]\n"
        )

    rules.append("// 3. Ends")

    for act in end_activities:
        rules.append(
            f"rule {act}_End:\n"
            f"    [ State_{act}({fr_name}) ]\n"
            f"  --[ {always_action.capitalize()}({fr_name}), {end_action.capitalize()}({fr_name}) ]->\n"
            f"    [ ]\n"
        )

    return "\n".join(rules)
