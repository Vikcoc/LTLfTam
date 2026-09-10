from Declare4Py.ProcessModels.LTLModel import LTLTemplate, LTLModel
from typing import List

def ltl_rules() -> List[LTLModel]: 
    template = LTLTemplate('precedence')
    activities_a = ["Inspect"]
    activities_b = ["Approve"]
    model = template.fill_template(activities_a, activities_b)

    template2 = LTLTemplate('response')
    activities_a2 = ["Rework"]
    activities_b2 = ["Inspect"]
    model2 = template2.fill_template(activities_a2, activities_b2)

    return [model, model2]