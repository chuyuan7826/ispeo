# ispeo: Inducible Squalene Production in *E. coli* ODE Model

**ispeo** is a Python CLI tool designed to simulate, fit, and optimize the fed-batch fermentation process of *E. coli* for squalene production. It utilizes a system of Ordinary Differential Equations (ODEs) incorporating Monod growth kinetics, Luedeking-Piret product formation, and a two-stage piecewise feeding strategy.

## Features

-   **Simulate:** Run forward simulations of biomass, substrate, product, and volume dynamics over time.
-   **Fit:** Estimate kinetic parameters (`mu_max`, `Ks`, etc.) by fitting the model to experimental data ($R^2$ metrics included).
-   **Optimize:** Find the optimal operational strategy (induction time, feeding rates) to maximize product or biomass, respecting volume constraints.
-   **Visualize:** Generate publication-ready 2x2 grid plots for simulation dynamics, model fitting quality, and optimization comparisons.

## Installation

Requires Python 3.9+. It is recommended to use a virtual environment.

```bash
# Clone the repository
git clone https://github.com/chuyuan7826/ispeo.git

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode
pip install -e .
```

## Quick Start

Check the help menu:
```bash
ispeo --help
```

See `USAGE.md` for detailed command documentation.

## Examples

### 1. Basic Simulation
Simulate a 48-hour fermentation using default parameters and save results to `results/`.

```bash
ispeo simulate \
    --param params/params.yml \
    --init params/init.yml \
    --time 48.0 \
    --output results \
    --plot
```
*Outputs: `results/simulation.csv`, `results/simulation.png`*

### 2. Parameter Fitting (Specific)
Fit only specific parameters (defined in `param-init.yml`) while keeping others fixed (from `params.yml`).

```bash
ispeo fit \
    --data data/experiment_01.csv \
    --param-init params/param-init.yml \
    --fixed-param params/params.yml \
    --output fit_results \
    --plot
```
*Outputs: `fit_results/fitted_params.yml`, `fit_results/fit_plot.png`*

### 3. Parameter Fitting (Global)
Fit **all** parameters from scratch. Requires `param-init.yml` to define bounds for all parameters. Pass an empty file (e.g., `null.yml`) to `--fixed-param`.

```bash
touch null.yml
ispeo fit \
    --data data/experiment_01.csv \
    --param-init params/param-init.yml \
    --fixed-param null.yml \
    --output fit_global
```

### 4. Process Optimization (Induction Time)
Find the optimal induction time (`ti`) to maximize product concentration.

```bash
ispeo optimize \
    --param params/params.yml \
    --bounds params/bounds.yml \
    --objective max_product \
    --opt-ti \
    --output opt_ti
```
*Outputs: `opt_ti/optimization_summary.txt`, `opt_ti/optimized_params.yml`*

### 5. Multi-Parameter Optimization with Volume Constraint
Optimize induction time and feeding strategy (`k1`, `b`) to maximize product, ensuring the final volume does not exceed 3.0L.

```bash
ispeo optimize \
    --param params/params.yml \
    --bounds params/bounds.yml \
    --objective max_product \
    --max-volume 3.0 \
    --opt-ti --opt-k1 --opt-b \
    --output opt_complex \
    --plot
```
*Outputs: Comparison plot `opt_complex/optimization_comparison.png`*

### 6. Biomass Maximization
Optimize the feed substrate concentration (`Sf`) and growth feed slope (`k1`) to maximize final biomass.

```bash
ispeo optimize \
    --param params/params.yml \
    --bounds params/bounds.yml \
    --objective max_biomass \
    --opt-sf --opt-k1 \
    --output opt_biomass \
    --plot
```

## Project Structure

-   `src/ispeo/`: Source code.
-   `params/`: Configuration files (kinetics, bounds, initial states).
-   `data/`: Experimental data templates.
-   `tests/`: Unit tests.

## License

MIT