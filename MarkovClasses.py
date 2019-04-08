import SimPy.RandomVariantGenerators as RVGs
import SimPy.SamplePathClasses as PathCls
import SimPy.EconEvalClasses as Econ
import SimPy.StatisticalClasses as Stat
import ParameterClasses as P


class Patient:
    def __init__(self, id, parameters):

        self.id = id
        self.rng = RVGs.RNG(seed=id)
        self.params = parameters
        self.stateMonitor = PatientStateMonitor(parameters=parameters)

    def simulate(self, n_time_steps):

        t = 0

        while self.stateMonitor.get_if_alive() and t < n_time_steps:

            # find the transition probabilities to future states
            trans_prob = self.params.prob_matrix[self.stateMonitor.currentState.value]

            # create an empirical distribution
            empirical_dist = RVGs.Empirical(probabilities=trans_prob)

            # sample from the empirical distribution to get a new state
            new_state_index = empirical_dist.sample(rng=self.rng)

            # update health state
            self.stateMonitor.update(time_step=t, new_state=P.HealthStates(new_state_index))

            # increment time
            t += 1


class PatientStateMonitor:
    def __init__(self, parameters):

        self.currentState = parameters.initialHealthState    # assuming everyone starts in "Well"
        self.survivalTime = None
        self.nStrokes = 0
        self.costUtilityMonitor = PatientCostUtilityMonitor(parameters=parameters)

    def update(self, time_step, new_state):

        if self.currentState == P.HealthStates.DEAD:
            return

        if new_state == P.HealthStates.DEAD:
            self.survivalTime = time_step + 0.5  # correct for half cycle effect

        if self.currentState == P.HealthStates.STROKE:
            self.nStrokes += 1

        self.costUtilityMonitor.update(t=time_step,
                                       current_state=self.currentState,
                                       next_state=new_state)
        self.currentState = new_state

    def get_if_alive(self):
        if self.currentState != P.HealthStates.DEAD:
            return True
        else:
            return False


class PatientCostUtilityMonitor:
    def __init__(self,parameters):

        self.params = parameters

        self.totalDiscountedCost = 0
        self.totalDiscountedUtility = 0

    def update(self, t, current_state, next_state):

        cost = 0.5 * (self.params.annualStateCosts[current_state.value] +
                      self.params.annualStateCosts[next_state.value])

        utility = 0.5 * (self.params.annualStateUtilities[current_state.value] +
                         self.params.annualStateUtilities[next_state.value])

        # add the cost of anti-coagulation if applied
        if next_state == P.HealthStates.DEAD:
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
        self.patients = []
        self.cohortOutcomes = CohortOutcomes()
        self.initialPopSize = pop_size

        for i in range(pop_size):
            patient = Patient(id=id*pop_size + i, parameters=parameters)
            self.patients.append(patient)

    def simulate(self, n_time_steps):

        for patient in self.patients:
            patient.simulate(n_time_steps)

        self.cohortOutcomes.extract_outcomes(self.patients)


class CohortOutcomes:
    def __init__(self):

        self.survivalTimes = []
        self.nTotalStrokes = []
        self.nLivingPatients = None
        self.costs = []
        self.utilities = []

        self.statSurvivalTime = None
        self.statCost = None
        self.statUtility = None
        self.statNumStrokes = None

    def extract_outcomes(self, simulated_patients):

        for patient in simulated_patients:
            if patient.stateMonitor.survivalTime is not None:
                self.survivalTimes.append(patient.stateMonitor.survivalTime)
            self.nTotalStrokes.append(patient.stateMonitor.nStrokes)
            self.costs.append(patient.stateMonitor.costUtilityMonitor.totalDiscountedCost)
            self.utilities.append(patient.stateMonitor.costUtilityMonitor.totalDiscountedUtility)

        self.statSurvivalTime = Stat.SummaryStat('Survival Time',self.survivalTimes)
        self.statCost = Stat.SummaryStat('Discounted cost', self.costs)
        self.statUtility = Stat.SummaryStat('Discounted utility', self.utilities)
        self.statNumStrokes = Stat.SummaryStat('Total Number of Strokes', self.nTotalStrokes)

        self.nLivingPatients = PathCls.PrevalencePathBatchUpdate(
            name = '# of living patients',
            initial_size= len(simulated_patients),
            times_of_changes=self.survivalTimes,
            increments=[-1]*len(self.survivalTimes)
        )
