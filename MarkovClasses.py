import numpy as np

import SimPy.EconEval as Econ
import SimPy.Markov as Markov
import SimPy.Plots.SamplePaths as Path
import SimPy.Statistics as Stat
from InputData import HealthStates


class Patient:
    def __init__(self, id, parameters):

        self.id = id
        self.params = parameters
        self.stateMonitor = PatientStateMonitor(parameters=self.params)

    def simulate(self, n_time_steps):

        # random number generator
        rng = np.random.RandomState(seed=self.id)
        # jump process
        markov_jump = Markov.MarkovJumpProcess(transition_prob_matrix=self.params.probMatrix)

        k = 0  # simulation time step

        # while the patient is alive and simulation length is not yet reached
        while self.stateMonitor.get_if_alive() and k < n_time_steps:
            # sample from the Markov jump process to get a new state
            # (returns an integer from {0, 1, 2, ...})
            new_state_index = markov_jump.get_next_state(
                current_state_index=self.stateMonitor.currentState.value,
                rng=rng)

            # update health state
            self.stateMonitor.update(time_step=k, new_state=HealthStates(new_state_index))

            # increment time
            k += 1


class PatientStateMonitor:
    def __init__(self, parameters):

        self.currentState = parameters.initialHealthState    # assuming everyone starts in "Well"
        self.survivalTime = None
        self.nStrokes = 0
        self.costUtilityMonitor = PatientCostUtilityMonitor(parameters=parameters)

    def update(self, time_step, new_state):

        if self.currentState == HealthStates.DEAD:
            return

        if new_state == HealthStates.DEAD:
            self.survivalTime = time_step + 0.5  # correct for half cycle effect

        if new_state == HealthStates.STROKE:
            self.nStrokes += 1

        self.costUtilityMonitor.update(t=time_step,
                                       current_state=self.currentState,
                                       next_state=new_state)
        self.currentState = new_state

    def get_if_alive(self):
        if self.currentState != HealthStates.DEAD:
            return True
        else:
            return False


class PatientCostUtilityMonitor:
    def __init__(self, parameters):

        self.params = parameters
        self.totalDiscountedCost = 0
        self.totalDiscountedUtility = 0

    def update(self, t, current_state, next_state):

        cost = 0.5 * (self.params.annualStateCosts[current_state.value] +
                      self.params.annualStateCosts[next_state.value])

        utility = 0.5 * (self.params.annualStateUtilities[current_state.value] +
                         self.params.annualStateUtilities[next_state.value])

        # add the cost of anti-coagulation if applied
        if next_state == HealthStates.DEAD:
            cost += 0.5 * self.params.annualTreatmentCost
        else:
            cost += 1 * self.params.annualTreatmentCost

        self.totalDiscountedCost += Econ.pv_single_payment(payment=cost,
                                                           discount_rate=self.params.discountRate/2,
                                                           discount_period=2 * t+1)
        self.totalDiscountedUtility += Econ.pv_single_payment(payment=utility,
                                                              discount_rate=self.params.discountRate/2,
                                                              discount_period=2 * t+1)


class Cohort:
    def __init__(self, id, pop_size, parameters):
        self.id = id
        self.popSize = pop_size
        self.params = parameters
        self.cohortOutcomes = CohortOutcomes()

    def simulate(self, n_time_steps):

        # populate the cohort
        for i in range(self.popSize):
            # create a new patient (use id * pop_size + n as patient id)
            patient = Patient(id=self.id * self.popSize + i,
                              parameters=self.params)
            # simulate
            patient.simulate(n_time_steps)

            # store outputs of this simulation
            self.cohortOutcomes.extract_outcome(simulated_patient=patient)

        # calculate cohort outcomes
        self.cohortOutcomes.calculate_cohort_outcomes(initial_pop_size=self.popSize)


class CohortOutcomes:
    def __init__(self):

        self.survivalTimes = []
        self.nStrokes = []
        self.nLivingPatients = None
        self.costs = []
        self.utilities = []

        self.statSurvivalTime = None
        self.statCost = None
        self.statUtility = None
        self.statNumStrokes = None

    def extract_outcome(self, simulated_patient):

        if simulated_patient.stateMonitor.survivalTime is not None:
            self.survivalTimes.append(simulated_patient.stateMonitor.survivalTime)
        self.nStrokes.append(simulated_patient.stateMonitor.nStrokes)
        self.costs.append(simulated_patient.stateMonitor.costUtilityMonitor.totalDiscountedCost)
        self.utilities.append(simulated_patient.stateMonitor.costUtilityMonitor.totalDiscountedUtility)

    def calculate_cohort_outcomes(self, initial_pop_size):
        """ calculates the cohort outcomes
        :param initial_pop_size: initial population size
        """
        self.statSurvivalTime = Stat.SummaryStat(
            name='Survival Time', data=self.survivalTimes)
        self.statCost = Stat.SummaryStat(
            name='Discounted cost', data=self.costs)
        self.statUtility = Stat.SummaryStat(
            name='Discounted utility', data=self.utilities)
        self.statNumStrokes = Stat.SummaryStat(
            name='Total Number of Strokes', data=self.nStrokes)

        self.nLivingPatients = Path.PrevalencePathBatchUpdate(
            name='# of living patients',
            initial_size=initial_pop_size,
            times_of_changes=self.survivalTimes,
            increments=[-1]*len(self.survivalTimes)
        )
