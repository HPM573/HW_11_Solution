from enum import Enum

# simulation settings
POP_SIZE = 50000         # cohort population size
SIM_TIME_STEPS = 50    # length of simulation (years)
ALPHA = 0.05        # significance level for calculating confidence intervals
DISCOUNT = 0.03     # annual discount rate

P_MORTALITY = 0.15  # annual probability of death due to all causes
P_STROKE = 0.05         # annual probability of stroke in state Well
P_RE_STROKE = 0.2     # annual probability of recurrent stroke
P_SURV = 0.7       # probability of surviving a stroke


class HealthStates(Enum):
    """ health states of patients """
    WELL = 0
    POST_STROKE = 1
    STROKE_DEATH = 2
    ALL_CAUSE_DEATH = 3
    STROKE = 4


# annual health utility of each health state
ANNUAL_STATE_UTILITY = [
    1,          # WEL
    0.9,        # POST- STROKE
    0,          # DEATH
    0,          # ALL_CAUSE_DEATH
    0.8865,     # STROKE WHEN CYCLE IS 1 YEAR
]

# annual cost of each health state
ANNUAL_STATE_COST = [
    0,      # WELL
    200,    # POST-STROKE
    0,      # DEATH
    0,      # ALL_CAUSE_DEATH
    5000,   # STROKE
]

ANTICOAG_COST = 5000

# anticoagulation relative risk in reducing stroke incidence while in “Post-Stroke”
ANTICOAG_RR = 0.65
