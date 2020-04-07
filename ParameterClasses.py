import copy
import InputData as D
from enum import Enum


class Therapies(Enum):
    """ none vs anticoagulation """
    NONE = 0
    ANTICOAG = 1


class ParametersFixed:
    def __init__(self, therapy):

        # selected therapy
        self.therapy = therapy

        # initial health state
        self.initialHealthState = D.HealthStates.WELL

        # annual treatment cost
        if self.therapy == Therapies.NONE:
            self.annualTreatmentCost = 0
        if self.therapy == Therapies.ANTICOAG:
            self.annualTreatmentCost = D.ANTICOAG_COST

        # transition probability matrix of the selected therapy
        self.prob_matrix = []

        # calculate transition probabilities depending of which therapy options is in use
        if therapy == Therapies.NONE:
            self.prob_matrix = get_prob_matrix_no_anticoag()
        else:
            self.prob_matrix = get_prob_matrix_anticoag(
                prob_matrix_no_anticoag=get_prob_matrix_no_anticoag())

        self.annualStateCosts = D.ANNUAL_STATE_COST
        self.annualStateUtilities = D.ANNUAL_STATE_UTILITY

        # discount rate
        self.discountRate = D.DISCOUNT


def get_prob_matrix_no_anticoag():

    # transition probability matrix with temporary state Stroke
    matrix = [
        [1 - D.P_STROKE,    0,                  0,      D.P_STROKE],        # WELL
        [0,                 1 - D.P_RE_STROKE,  0,      D.P_RE_STROKE],     # POST-STROKE
        [0,                 0,                  0,      1],                 # DEATH
        [0,                 D.P_SURV,           1 - D.P_SURV, 0]            # STROKE
    ]

    return matrix


def get_prob_matrix_anticoag(prob_matrix_no_anticoag):
    """
    :param prob_matrix_no_anticoag: (list of lists) transition probability matrix under no anticoagolation
    :returns (list of lists) transition probability matrix under anticoagolation """

    # There are two ways to build the probability matrix under anti-coagulation:
    # 1. to get the probability matrix under no anti-coagulation and modify the row that corresponds to 'Post-Stroke',
    # 2. build the matrix from scratch (similar to what we did in get_prob_matrix_no_anticoag() method).
    # Here we use the first approach.

    # copy all the elements of probability matrix under no anti-coagulation to a
    # new matrix. Note that we have to 'deepcopy' the elements of prob_matrix_no_anticoag
    # to prob_matrix. Otherwise, any change we make to prob_matrix will also change
    # prob_matrix_no_anticoag (see HW 1, Problem 4 for an example).
    prob_matrix = copy.deepcopy(prob_matrix_no_anticoag)

    # change the probability of moving from 'post-stroke' to 'stroke' when anti-coagulation is used
    prob_matrix[D.HealthStates.POST_STROKE.value][D.HealthStates.STROKE.value] = \
        prob_matrix_no_anticoag[D.HealthStates.POST_STROKE.value][D.HealthStates.STROKE.value] * \
            D.ANTICOAG_RR

    # change the probability of staying in 'post-stroke' when anti-coagulation is used
    prob_matrix[D.HealthStates.POST_STROKE.value][D.HealthStates.POST_STROKE.value] = \
        1 - prob_matrix[D.HealthStates.POST_STROKE.value][D.HealthStates.STROKE.value]

    return prob_matrix


# tests
matrix_no_anticoag = get_prob_matrix_no_anticoag()
matrix_with_anticoag = get_prob_matrix_anticoag(matrix_no_anticoag)

print(matrix_no_anticoag)
print(matrix_with_anticoag)
