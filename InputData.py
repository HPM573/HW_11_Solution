from enum import Enum

# simulation settings
POP_SIZE = 2000         # cohort population size
SIM_TIME_STEPS = 50    # length of simulation (years)
ALPHA = 0.05

P_STROKE = 0.05         # annual probability of stroke in state Well
P_RE_STROKE = 0.2     # annual probability of recurrent stroke
P_SURV = 0.7       # probability of surviving a stroke

DELTA_T = 1
DISCOUNT = 0.03


class HealthState(Enum):
    """ health states of patients """
    WELL = 0
    POST_STROKE = 1
    DEAD = 2
    STROKE = 3


# transition probability matrix without anticoagulation
TRANS_RATE_MATRIX_1 = [
    [0.75,  0.15,   0.0,    0.1],   # Well
    [0,     0.0,    1.0,    0.0],   # Stroke
    [0,     0.25,   0.55,   0.2],   # Post-Stroke
    [0.0,   0.0,    0.0,    1.0],   # Dead
    ]



HEALTH_UTILITY = [
    1,#WELL
    0.8865, #STROKE WHEN CYCLE IS 1 YEAR
    0.9, #POST- STROKE
    0 #DEATH
]


HEALTH_COST = [
    0, #WELL
    5000, #STROKE
    200, #POST-STROKE
    0 #DEATH
]

ANTICOAG_COST = 2000
