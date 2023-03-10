from destroy_operator import Destroy
from repair_operator import Repair
from operator_selection import OPSelection
from acceptance_criterion import Acceptance

class ALNSControl(Destroy, Repair, OPSelection, Acceptance):
    pass