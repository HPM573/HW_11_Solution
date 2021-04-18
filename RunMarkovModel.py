import InputData as D
import ParameterClasses as P
import MarkovClasses as Cls
import SupportMarkovModel as Support
import SimPy.Plots.SamplePaths as Path
import SimPy.Plots.Histogram as Hist

# selected therapy
therapy = P.Therapies.NONE

# create a cohort
myCohort = Cls.Cohort(id=1,
                      pop_size=D.POP_SIZE,
                      parameters=P.Parameters(therapy=therapy))

# simulate the cohort over the specified time steps
myCohort.simulate(n_time_steps=D.SIM_TIME_STEPS)

# plot the sample path (survival curve)
Path.plot_sample_path(
    sample_path=myCohort.cohortOutcomes.nLivingPatients,
    title='Survival Curve',
    x_label='Time-Step (Year)',
    y_label='Number Survived')

# plot the histogram of survival times
Hist.plot_histogram(
    data=myCohort.cohortOutcomes.survivalTimes,
    title='Histogram of Patient Survival Time',
    x_label='Survival Time (Year)',
    y_label='Count',
    bin_width=1)

# histogram of number of strokes
Hist.plot_histogram(
    data=myCohort.cohortOutcomes.nStrokes,
    title='Histogram of Number of Strokes',
    x_label='Number of Strokes',
    y_label='Count',
    bin_width=1
)

# print the outcomes of this simulated cohort
Support.print_outcomes(sim_outcomes=myCohort.cohortOutcomes,
                       therapy_name=therapy)

