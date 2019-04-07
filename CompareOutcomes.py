import InputData as D
import ParameterClasses as P
import MarkovClasses as Cls
import SupportMarkovModel as Support


# simulating mono therapy
# create a cohort
cohort_none = Cls.Cohort(id=0,
                         pop_size=D.POP_SIZE,
                         parameters=P.ParametersFixed(therapy=P.Therapies.NONE))
# simulate the cohort
cohort_none.simulate(n_time_steps=D.SIM_TIME_STEPS)

# simulating combination therapy
# create a cohort
cohort_anticoag = Cls.Cohort(id=1,
                          pop_size=D.POP_SIZE,
                          parameters=P.ParametersFixed(therapy=P.Therapies.ANTICOAG))
# simulate the cohort
cohort_anticoag.simulate(n_time_steps=D.SIM_TIME_STEPS)

# print the estimates for the mean survival time and mean time to AIDS
Support.print_outcomes(sim_outcomes=cohort_none.cohortOutcomes,
                       therapy_name=P.Therapies.NONE)
Support.print_outcomes(sim_outcomes=cohort_anticoag.cohortOutcomes,
                       therapy_name=P.Therapies.ANTICOAG)

# draw survival curves and histograms
Support.plot_survival_curves_and_histograms(sim_outcomes_none=cohort_none.cohortOutcomes,
                                            sim_outcomes_combo=cohort_anticoag.cohortOutcomes)


# print comparative outcomes
Support.print_comparative_outcomes(sim_outcomes_none=cohort_none.cohortOutcomes,
                                   sim_outcomes_combo=cohort_anticoag.cohortOutcomes)

# report the CEA results
Support.report_CEA_CBA(sim_outcomes_none=cohort_none.cohortOutcomes,
                       sim_outcomes_combo=cohort_anticoag.cohortOutcomes)
