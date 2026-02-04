# Usage of **I**nducible **S**qualene **P**roduction in *__E__. coli* **O**DE model (ispeo).

```
NAME
        ispeo — simulate, fit, and optimize squalene production in E. coli

SYNOPSIS
        ispeo simulate [OPTIONS]
        ispeo fit [OPTIONS]
        ispeo optimize [OPTIONS]

DESCRIPTION
        ispeo is the python implementation of inducible squalene production in 
        E. coli ODE model. The equations are defined in the project documentation. 
        The passable parameters are in `./params/params.yml`.

COMMANDS
    simulate
        Run a forward simulation of the fermentation process using the ODE model.

        Options:
            --param FILE
                YAML file containing kinetic and operational parameters.
                See `./params/params.yml`.
            
            --init FILE
                YAML file containing initial state variables (X, S, P, B, V).
                See `./params/init.yml`.
            
            --time FLOAT
                Total simulation time in hours.
            
            --step FLOAT
                Time step for reporting output (default: 0.1h).
            
            --output DIR
                Directory to save the simulation results (CSV) and plot (PNG).
                Defaults to current directory.
            
            --plot
                Flag to generate and save a visualization of the state variables.

    fit
        Estimate kinetic parameters by minimizing error against experimental data.
        Evaluations (like R^2) of the fitting will be output to stdout.

        Options:
            --data FILE
                CSV file containing experimental time-course data.
                See `./data/data.csv` which dictates the structure template.
            
            --param-init FILE
                YAML file with initial guesses and bounds for parameters to be fitted.
                See `./params/param-init.yml`.
            
            --fixed-param FILE
                YAML file with parameters to remain constant during fitting.
                See `./params/params.yml`. Can be empty if fitting all parameters.
            
            --output DIR
                Directory to save the fitted parameters (YAML) and overlay plot (PNG).
                Defaults to current directory.
            
            --plot
                Flag to show the fit quality (experimental vs. simulated curves).

    optimize
        Find the optimal operational strategy for a target objective by tuning
        selected parameters.

        Options:
            --param FILE
                YAML file with baseline kinetic and operational parameters.
                See `./params/params.yml`.
            
            --objective STRING
                Target objective to maximize:
                - "max_product": Maximize final product concentration [g/L].
                - "max_biomass": Maximize final biomass concentration [g/L].
            
            --bounds FILE
                YAML file defining search ranges [min, max] for parameters.
                See './params/bounds.yml`.
            
            --max-volume FLOAT
                Maximum working volume constraint [L] (default: 5.0).
            
            --opt-ti
                Flag to optimize induction time point (ti).
            
            --opt-k1
                Flag to optimize feeding acceleration in growth phase (k1).
            
            --opt-k2
                Flag to optimize feeding slope in production phase (k2).
            
            --opt-b
                Flag to optimize initial feeding rate (b).
            
            --opt-sf
                Flag to optimize substrate concentration in feed (Sf).

            --output DIR
                Directory to save the optimization summary, best parameters, and comparison plot.
                Defaults to current directory.

            --plot
                Flag to visualize the comparison between baseline and optimized strategies.
```
