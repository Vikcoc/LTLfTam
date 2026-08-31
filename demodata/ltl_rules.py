from Declare4Py.ProcessModels.LTLModel import LTLTemplate, LTLModel
from typing import List

def ltl_rules() -> List[LTLModel]: 
    template = LTLTemplate('precedence')
    activities_a = ["manualinspection"]
    activities_b = ["manualissuance"]
    model = template.fill_template(activities_a, activities_b)

    template2 = LTLTemplate('precedence')
    activities_a2 = ["automaticinspection"]
    activities_b2 = ["automaticissuance"]
    model2 = template.fill_template(activities_a2, activities_b2)

    return [model, model2]