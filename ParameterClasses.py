import copy

from InputData import *


class Therapies(Enum):
    """ none vs anticoagulation """
    NONE = 0
    ANTICOAG = 1


class Parameters:
    def __init__(self, therapy):

        # selected therapy
        self.therapy = therapy

        # initial health state
        self.initialHealthState = HealthStates.WELL

        # transition probability matrix of the selected therapy
        self.probMatrix = []

        # calculate transition probabilities depending on which therapy options is in use
        if therapy == Therapies.NONE:
            self.probMatrix = get_prob_matrix_no_anticoag()
        else:
            self.probMatrix = get_prob_matrix_anticoag(
                prob_matrix_no_anticoag=get_prob_matrix_no_anticoag())

        self.annualStateCosts = ANNUAL_STATE_COST
        self.annualStateUtilities = ANNUAL_STATE_UTILITY

        # adding annual cost of anticoagulation
        if self.therapy == Therapies.ANTICOAG:
            self.annualStateCosts[HealthStates.POST_STROKE.value] += ANTICOAG_COST

        # discount rate
        self.discountRate = DISCOUNT


def get_prob_matrix_no_anticoag():

    # transition probability matrix with temporary state Stroke
    matrix =[
        [  # Well
            (1 - P_MORTALITY) * (1 - P_STROKE),  # Well
            0,  # Post-stroke
            0,  # Stroke-death
            P_MORTALITY,  # All-cause mortality
            (1 - P_MORTALITY) * P_STROKE],  # Stroke

        [  # POST_STROKE
            0,  # Well
            (1 - P_MORTALITY) * (1 - P_RE_STROKE),  # Post-stroke
            0,  # Stroke-death
            P_MORTALITY,  # All-cause mortality
            (1 - P_MORTALITY) * P_RE_STROKE],  # Stroke

        [  # STOKE DEATH
            0,  # Well
            0,  # Post-stroke
            1,  # Stroke-death
            0,  # All-cause mortality
            0],  # Stroke

        [  # ALL_CAUSE DEATH
            0,  # Well
            0,  # Post-stroke
            0,  # Stroke-death
            1,  # All-cause mortality
            0],  # Stroke
        [  # STOKE
            0,  # Well
            P_SURV,  # Post-stroke
            1 - P_SURV,  # Stroke-death
            0,  # All-cause mortality
            0],  # Stroke
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

    # prob_matrix[HealthStates.WELL.value][HealthStates.STROKE.value] = \
    #     prob_matrix_no_anticoag[HealthStates.WELL.value][HealthStates.STROKE.value] * \
    #         ANTICOAG_RR
    # prob_matrix[HealthStates.WELL.value][HealthStates.WELL.value] = \
    #     1 - prob_matrix[HealthStates.WELL.value][HealthStates.STROKE.value] - \
    #         prob_matrix[HealthStates.WELL.value][HealthStates.ALL_CAUSE_DEATH.value]

    # change the probability of moving from 'post-stroke' to 'stroke' when anti-coagulation is used
    prob_matrix[HealthStates.POST_STROKE.value][HealthStates.STROKE.value] = \
        prob_matrix_no_anticoag[HealthStates.POST_STROKE.value][HealthStates.STROKE.value] * \
            ANTICOAG_RR

    # change the probability of staying in 'post-stroke' when anti-coagulation is used
    prob_matrix[HealthStates.POST_STROKE.value][HealthStates.POST_STROKE.value] = \
        1 - prob_matrix[HealthStates.POST_STROKE.value][HealthStates.STROKE.value] - \
        prob_matrix[HealthStates.POST_STROKE.value][HealthStates.ALL_CAUSE_DEATH.value]

    return prob_matrix


if __name__ == '__main__':
    # tests
    matrix_no_anticoag = get_prob_matrix_no_anticoag()
    matrix_with_anticoag = get_prob_matrix_anticoag(matrix_no_anticoag)

    print(matrix_no_anticoag)
    print(matrix_with_anticoag)
