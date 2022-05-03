

TITLE_ABOUT_INPUTS_POPUP = 'Simulator Inputs'
TEXT_ABOUT_INPUTS_POPUP = (
    'Iterations: the number of individual simulations to run, each starting with different initial line failures and running until the cascading failure stops. Higher numbers of iterations will take longer to run, but will produce more reliable results.',
    'Load: This is the load-generation ratio for the grid. The load-generation ratio is the load on the grid as a percentage of the generation. 1.0 represents the sum of the loads being equivalent to the generation and 0.0 represents no load.',
    'Initial Failures: This is the number of random line failures that occur at the start or each simulation iteration.',
    # TODO change this to 'Load Shedding Constant'
    'Operator Constraints: This represents the constraints to which grid operators are held when making load-shedding decisions. Load-shedding is when a grid operator reduces or turns off electricity distribution to an area when the demand is higher than the grid can supply. 1.0 represents no load shedding permitted, while 0.0 represents no load shedding constraints.',
    'Line Capacity Uncertainty: This represents the estimation error operators have when determining the highest capacity of a line. 0.0 represents perfect knowledge of line capacities, 1.0 represents minimum knowledge of line capacities.'
)

TITLE_ABOUT_OUTPUTS_POPUP = 'Simulator Outputs'
# TODO populate this. explain the outputs and why they are significant
TEXT_ABOUT_OUTPUTS_POPUP = (

)

TITLE_ABOUT_SIMULATOR_POPUP = 'About The Simulator'
# TODO populate this, explains history of software and why it is important
TEXT_ABOUT_SIMULATOR_POPUP = (

)

FORMAT_TEXT_TOP_LABEL = 'Results for %d iterations, %d initial failures, %.2f load generation ratio, %.2f load shedding constant, and %.2f estimation error'
FORMAT_TEXT_SELECTED_SIM = 'Simulation %d out of %d'
FORMAT_TEXT_SIM_STEP = 'Step %d of %d'
FORMAT_TEXT_SIM_STATUS = '%s'
