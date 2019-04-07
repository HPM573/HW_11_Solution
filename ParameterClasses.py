from enum import Enum
import InputData as D


class HealthStates(Enum):
    """ health states of patients with HIV """
    WELL = 0
    STROKE = 1
    POST_STROKE = 2
    DEATH = 3


class Therapies(Enum):
    """ mono vs. combination therapy """
    NONE = 0
    ANTICOAG = 1


class ParametersFixed():
    def __init__(self, therapy):

        # selected therapy
        self.therapy = therapy

        #initial health state
        self.initialHealthState = HealthStates.WELL

        # simulation time step
        self.delta_t = D.DELTA_T

        self.adjDiscountRate = D.DISCOUNT * D.DELTA_T

        # annual treatment cost
        if self.therapy == Therapies.NONE:
            self.annualTreatmentCost = 0
        if self.therapy == Therapies.ANTICOAG:
            self.annualTreatmentCost = D.ANTICOAG_COST

        # transition probability matrix of the selected therapy
        self.prob_matrix = []
        # treatment relative risk
        self.treatmentRR = 0

        # calculate transition probabilities depending of which therapy options is in use
        if therapy == Therapies.NONE:
            self.prob_matrix = D.TRANS_RATE_MATRIX_1
        else:
            self.prob_matrix = get_prob_matrix_anticoag(D.TRANS_RATE_MATRIX_1)

        self.annualStateCosts = D.HEALTH_COST
        self.annualStateUtilities = D.HEALTH_UTILITY


def get_prob_matrix_anticoag(trans_matrix):
    """
    :param prob_matrix_mono: (list of lists) transition probability matrix under mono therapy
    :param combo_rr: relative risk of the combination treatment
    :returns (list of lists) transition probability matrix under combination therapy """

    # create an empty list of lists
    matrix_combo = []
    for row in trans_matrix:
        matrix_combo.append(np.zeros(len(row)))  # adding a row [0, 0, 0]

    # populate the combo matrix
    # calculate the effect of combo-therapy on non-diagonal elements
    for s in range(len(matrix_combo)):
        for next_s in range(s + 1, len(HealthStates)):
            if s == HealthStates.POST_STROKE:
                #post stroke to stroke changes
                matrix_combo[s][HealthStates.STROKE.value] = 0.25 * trans_matrix[s][HealthStates.STROKE.value]
                #post stroke to death changes
                matrix_combo[s][HealthStates.DEATH.value] = 1.05 * trans_matrix[s][HealthStates.DEATH.value]
                #remaining in post stroke
                matrix_combo[s][s] = 1- matrix_combo[s][HealthStates.STROKE.value] - matrix_combo[s][HealthStates.DEATH]

    # diagonal elements are calculated to make sure the sum of each row is 1
    for s in range(len(matrix_combo)):
        matrix_combo[s][s] = 1 - sum(matrix_combo[s][s+1:])

    return matrix_combo



