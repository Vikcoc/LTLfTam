
from typing import Dict, Tuple, Iterable
import networkx

def build_loop_restrictions(dfg: Dict[Tuple[str, str], int],
                            fr_name: str,
                            max_iterations :int) -> str:

    num_points = max_iterations + 1
    time_vars = [f"#t{i}" for i in range(1, num_points + 1)]
    ex_vars = f"{fr_name} " + " ".join(time_vars)
    orderings = [f"{time_vars[i]} < {time_vars[i+1]}" for i in range(num_points - 1)]

    rules = ['// 4 Loop restriction']

    G = networkx.DiGraph(dfg.keys())
    for node in [cycle[0] for cycle in networkx.simple_cycles(G)]:
        events = [f"{node.capitalize()}({fr_name})@{t}" for t in time_vars]
        body = " &\n       ".join(events + orderings)
        restriction_name = f"Max_{max_iterations}_{node}"
        rules.append(
            f"restriction {restriction_name}:\n"
            f'  "not (Ex {ex_vars}.\n'
            f'       {body})"\n'
        )
    
    return "\n".join(rules)

def build_must_end_restriction(fr_name: str, start_action: str, end_action: str) -> str:
    return (
        f"// 5. Complete traces\n"
        f"restriction Force_Trace_Completion:\n"
        f'  "not (Ex {fr_name} #tinit. {start_action.capitalize()}({fr_name})@#tinit &\n'
        f'       not (Ex #tend. {end_action.capitalize()}({fr_name})@tend))"\n'
    )

if __name__ == "__main__":
    d: Dict[Tuple[str, str], int] = {("A", "B"): 2, ("B", "C"): 1, ("C", "A"): 1, ("C", "D"): 3, ("D", "A"): 1}
    edges = [("A", "B"), ("B", "C"), ("C", "A"), ("C", "D")]
    build_loop_restrictions(d, '', '')