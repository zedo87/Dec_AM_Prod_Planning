class Acceptance:
    def __init__(self):
        """
        acceptance criterion for the ALNS, acceptance criterion is based on metropolis criterion, which is also used
        in simulated annealing.
        T is the cooling temperatur
        alpha
        """
        self.T = 0
        self.alpha = 0
        self.k = 0