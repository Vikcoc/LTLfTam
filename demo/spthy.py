
import pm4py
from typing import List, Optional, Tuple, Union
from pylogics.syntax.ltl import Formula
import demo.transitions as demot
import demo.loops as demol
import demo.ltlf as ltlf
from Declare4Py.ProcessModels.LTLModel import LTLModel


def build_file(log_path: str,
                output_spthy_path: str,
                ltlf_formulas: Optional[List[LTLModel]],
                max_loop_iterations: int = 2,
                force_completion: bool = True):

    
    pm4py_log = pm4py.read_xes(log_path)
    dfg, start_acts, end_acts = pm4py.discover_dfg(pm4py_log)

    file_content = ['theory Generated\nbegin\n']

    fr_name = 'fr'
    always_action = 'TamAlways'
    start_action = 'TamStart'
    end_action = 'TamEnd'

    transitions = demot.build_transitions(dfg, start_acts, end_acts, fr_name, always_action, start_action, end_action)
    file_content.append(transitions)

    loops = demol.build_loop_restrictions(dfg, fr_name, max_loop_iterations)
    file_content.append(loops)

    if force_completion:
        end = demol.build_must_end_restriction(fr_name, start_action, end_action)
        file_content.append(end)

    generated_lemmas = []
    if ltlf_formulas:
        for idx, model in enumerate(ltlf_formulas, start=1):
            lemma_name = f"lemma_{idx}"

            lemma_str = ltlf.build_lemma(
                model,
                lemma_name,
                fr_name,
                always_action,
                start_action,
                end_action
            )
            generated_lemmas.append(lemma_str)

    file_content.append("\n\n".join(generated_lemmas))

    file_content.append('\nend')

    with open(output_spthy_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(file_content))
    print(f"Successfully saved Tamarin theory to: {log_path}")

    return
