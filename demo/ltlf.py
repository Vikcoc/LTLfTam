from pylogics.syntax.ltl import (
    Formula, Atomic, Next, WeakNext, Always, Eventually,
    Until, Release, WeakUntil
)
from pylogics.syntax.base import (
    TrueFormula, FalseFormula,
    Not, And, Or, Implies, Equivalence, _UnaryOp, _BinaryOp
)
import spot
from pylogics.parsers import ltl
from Declare4Py.ProcessModels.LTLModel import LTLModel

# Enable aggressive simplification rules
opts = spot.tl_simplifier_options()
opts.syntactic_red = True              # Enable syntactic rewrites (GG -> G, etc.)
opts.containment_checks = True          # Enable language containment checks
opts.containment_checks_strong = True   # Enable stronger language checks (more CPU, maximum reduction)
opts.glob_containment = True           # Check global containment properties
opts.eventuality_red = True            # Reduce eventualities

simplifier = spot.tl_simplifier(opts)

def translate_unary(formula: _UnaryOp,
                    fr_name: str,
                    parent_timestep: str,
                    current_timestep: str,
                    always_action: str,
                    end_action: str) -> str:
    factory_basic = lambda arg: translate_formula(arg, fr_name, parent_timestep, current_timestep, always_action, end_action)
    factory_ltl = lambda arg: translate_formula(arg, fr_name, current_timestep, current_timestep + 'c', always_action, end_action)
    sub_formula_basic = factory_basic(formula.argument)
    sub_formula_ltl = factory_ltl(formula.argument)

    if isinstance(formula, Not):
        return f"not({sub_formula_basic})"

    if isinstance(formula, Always):
        return f"(All #{current_timestep}. {always_action.capitalize()}({fr_name})@{current_timestep} & (#{parent_timestep} < #{current_timestep} | #{parent_timestep} = #{current_timestep}) ==> {sub_formula_ltl})"

    if isinstance(formula, Eventually):
        return f"(Ex #{current_timestep}. {always_action.capitalize()}({fr_name})@{current_timestep} & (#{parent_timestep} < #{current_timestep} | #{parent_timestep} = #{current_timestep}) & {sub_formula_ltl})"
     
    if isinstance(formula, Next):
        return (
            f"(Ex #{current_timestep} . #{parent_timestep} < #{current_timestep} & {always_action.capitalize()}({fr_name})@{current_timestep} & "
            f"not(Ex #{current_timestep}2 . #{parent_timestep} < #{current_timestep}2 & #{current_timestep}2 < #{current_timestep} & {always_action.capitalize()}({fr_name})@{current_timestep}2) & "
            f"{sub_formula_ltl})"
        )
    if isinstance(formula, WeakNext):
        sub_formula_basic = factory_basic(Next(formula.argument))
        return (
            f"({end_action.capitalize()}({fr_name})@{parent_timestep}) | {sub_formula_basic})"
        )

    raise NotImplementedError(f'{formula.__class__} Operation not supported.')

def translate_binary(formula: _UnaryOp,
                    fr_name: str,
                    parent_timestep: str,
                    current_timestep: str,
                    always_action: str,
                    end_action: str) -> str:

    operands = list(formula.operands)
    if len(operands) > 2:
        raise NotImplementedError('Ternary or higher-arity operators are not supported.')
    left_op, right_op = operands[0], operands[1]

    factory_basic = lambda arg: translate_formula(arg, fr_name, parent_timestep, current_timestep, always_action, end_action)
    factory_ltl = lambda arg, par, child: translate_formula(arg, fr_name, par, child, always_action, end_action)

    sub_l_basic = factory_basic(left_op)
    sub_r_basic = factory_basic(right_op)

    if isinstance(formula, Implies):
        return f"({sub_l_basic} ==> {sub_r_basic})"
    if isinstance(formula, And):
        return f"({sub_l_basic} & {sub_r_basic})"
    if isinstance(formula, Or):
        return f"({sub_l_basic} | {sub_r_basic})"
    if isinstance(formula, Equivalence):
        return f"({sub_l_basic} <=> {sub_r_basic})"

    if isinstance(formula, Until):
        sub_l_ltl = factory_ltl(left_op, current_timestep + 'k', current_timestep + 'kl')
        sub_r_ltl = factory_ltl(right_op, current_timestep + 'j', current_timestep + 'jr')
        return (
            f'(Ex #{current_timestep}j #{current_timestep}last . {always_action.capitalize()}({fr_name})@{current_timestep}j & {end_action.capitalize()}({fr_name})@{current_timestep}last &' # set up j and last
            f' ( #{parent_timestep} < #{current_timestep}j & #{current_timestep}j < #{current_timestep}last | #{parent_timestep} = #{current_timestep}j | #{current_timestep}j = #{current_timestep}last)' # state j between i and last
            f' & {sub_r_ltl} & '
            f' (All #{current_timestep}k . {always_action.capitalize()}({fr_name})@{current_timestep}k & (#{parent_timestep} < #{current_timestep}k & #{current_timestep}k < #{current_timestep}j | #{parent_timestep} = #{current_timestep}k)' # i <= k < j
            f'  ==> {sub_l_ltl}) )'
        )

    if isinstance(formula, WeakUntil):
        sub_l_basic = factory_basic(Until(left_op, right_op))
        sub_r_basic = factory_basic(Always(left_op))
        return f"({sub_l_basic} | {sub_r_basic})"

    if isinstance(formula, Release):
        return factory_basic(Not(Until(Not(left_op), Not(right_op))))

    raise NotImplementedError(f'{formula.__class__} Operation not supported.')


def translate_formula(formula: _UnaryOp,
                    fr_name: str,
                    parent_timestep: str,
                    current_timestep: str,
                    always_action: str,
                    end_action: str) -> str:

    if isinstance(formula, Atomic):
        return f"{formula.name[4:].capitalize() if formula.name[:4] == 'con_' else formula.name.capitalize()}({fr_name})@{parent_timestep}"
    if isinstance(formula, TrueFormula):
        return f"(1 = 1)@{parent_timestep}"
    if isinstance(formula, FalseFormula):
        return f"(1 = 0)@{parent_timestep}"

    if hasattr(formula, 'operands'):
        return translate_binary(formula, fr_name, parent_timestep, current_timestep, always_action, end_action)
    else:
        return translate_unary(formula, fr_name, parent_timestep, current_timestep, always_action, end_action)

def build_lemma(model: LTLModel,
                lemma_name: str,
                fr_name: str,
                always_action: str,
                start_action: str,
                end_action: str) -> str:

    spot_formula = spot.formula(str(model.formula))
    spot_formula = spot.negative_normal_form(simplifier.simplify(spot_formula))
    formula = None
    try:
        formula = ltl.parse_ltl(spot_formula.to_str())
    except:
        formula = model.parsed_formula

    root_timestemp = 't'
    rules = [
        f"// original: {model.formula}\n"
        f"// simpnorm: {spot_formula.to_str()}\n"
        f"lemma {lemma_name}:\n"
        f'  "All {fr_name} #{root_timestemp}. {start_action.capitalize()}({fr_name}) @{root_timestemp} ==> (\n'
        f'      {translate_formula(formula, fr_name, root_timestemp, root_timestemp + 't', always_action, end_action)}\n'
        f'  )"\n']

    
    return "\n".join(rules)