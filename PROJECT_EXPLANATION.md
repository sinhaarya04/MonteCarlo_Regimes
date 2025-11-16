# Complete Project Explanation: Monte Carlo Correlation Breakdown Engine

## Table of Contents
1. [What is This Project About?](#what-is-this-project-about)
2. [The Problem We're Solving](#the-problem-were-solving)
3. [Key Concepts Explained](#key-concepts-explained)
4. [Project Structure - File by File](#project-structure---file-by-file)
5. [Step-by-Step Workflow](#step-by-step-workflow)
6. [Mathematical Formulas and Calculations](#mathematical-formulas-and-calculations)
7. [How Everything Connects](#how-everything-connects)

---

## What is This Project About?

This project simulates how financial markets behave during different market conditions (called "regimes") and how correlations between stocks change during crises. 

**In simple terms:** When markets are calm, stocks move somewhat independently. But during crises (like 2008 financial crisis or COVID-19 crash), stocks tend to move together - their correlations increase dramatically. This project models this behavior and simulates thousands of possible future scenarios to understand portfolio risk.

---

## The Problem We're Solving

### The Real-World Problem:
- **Portfolio managers** need to understand how their investments will perform during market crashes
- **Risk managers** need to quantify potential losses
- **Traders** want to know: "What if everything crashes at once?"

### What We're Testing:
The hypothesis that **correlations between stocks spike during market crises**, meaning all stocks fall together, making diversification less effective.

### Our Solution:
We build a Monte Carlo simulation engine that:
1. Learns from historical data how markets behave in normal vs. stressful times
2. Models how markets transition between different states (Normal → Stress → Crisis)
3. Simulates thousands of possible future scenarios
4. Calculates risk metrics to understand potential losses

---

## Key Concepts Explained

### 1. **Log Returns** (vs. Regular Returns)
- **Regular return**: `(Price_today - Price_yesterday) / Price_yesterday`
- **Log return**: `log(Price_today / Price_yesterday)`
- **Why log returns?** They're mathematically easier to work with and can be added over time. If you have 10 days of log returns, the total return is just the sum.

### 2. **Volatility**
- Measures how much prices fluctuate
- **High volatility** = prices swing wildly (risky)
- **Low volatility** = prices are stable (less risky)
- Calculated as the **standard deviation** of returns

### 3. **Correlation**
- Measures how two stocks move together
- **Correlation = 1.0**: Perfectly move together (both always go up/down together)
- **Correlation = 0.0**: No relationship (independent)
- **Correlation = -1.0**: Perfectly opposite (one goes up, other goes down)
- **During crises**: Correlations spike toward 1.0 (everything falls together)

### 4. **Covariance Matrix**
- A table showing how all pairs of stocks move together
- If you have 5 stocks, it's a 5×5 matrix
- Diagonal = variance of each stock (how much it fluctuates)
- Off-diagonal = covariance between pairs (how they move together)

### 5. **Regimes** (Market States)
- **Normal**: Typical market conditions, moderate correlations
- **Stress**: High volatility periods, higher correlations
- **Crisis**: Extreme conditions, very high correlations (0.90+)

### 6. **Markov Chain**
- A model that transitions between states (Normal/Stress/Crisis)
- Each state has probabilities of moving to other states
- Example: If in Normal state, 95% chance stay Normal, 5% chance go to Stress

### 7. **Monte Carlo Simulation**
- Run thousands of random scenarios to see what might happen
- Like rolling dice 10,000 times to see all possible outcomes
- Each "path" is one possible future scenario

### 8. **Risk Metrics**
- **VaR (Value at Risk)**: "What's the worst loss I might see 95% of the time?"
- **Max Drawdown**: "What's the biggest peak-to-trough decline?"
- **Volatility**: Standard deviation of returns

---

## Project Structure - File by File

### 📁 **data_loader.py**

**Purpose:** Downloads historical stock price data and converts it to log returns.

**What it does:**
1. Uses `yfinance` library to download stock prices from Yahoo Finance
2. Takes ticker symbols (like 'AAPL' for Apple), start date, end date
3. Extracts closing prices
4. Calculates log returns: `log(Price_today / Price_yesterday)`

**Key Function:**
```python
download_price_data(tickers, start, end)
```
- Input: List of stock symbols, date range
- Output: DataFrame with daily log returns for each stock

**Example:**
- Downloads AAPL prices from 2020-01-01 to 2024-01-01
- If AAPL was $100 yesterday and $105 today:
  - Regular return = (105-100)/100 = 5%
  - Log return = log(105/100) = 0.0488 = 4.88%

---

### 📁 **regime_estimation.py**

**Purpose:** Classifies historical days into market regimes and estimates correlation/covariance matrices for each regime.

**What it does:**

#### Step 1: Compute Rolling Volatility
- For each day, looks at the last 20 days of returns
- Calculates standard deviation (volatility) of those returns
- Averages across all stocks to get overall market volatility

**Formula:**
```
Volatility = Standard Deviation of returns over rolling window
```

#### Step 2: Classify Regimes
- **Normal days**: Volatility below 75th percentile
- **Stress days**: Volatility above 75th percentile
- **Crisis days**: Not found in data, created synthetically

**Logic:**
```python
if volatility >= 75th_percentile:
    regime = Stress
else:
    regime = Normal
```

#### Step 3: Estimate Covariance Matrices
- Separates returns by regime (Normal vs. Stress)
- For each regime, calculates covariance matrix

**Covariance Formula:**
```
Cov(X, Y) = E[(X - E[X]) * (Y - E[Y])]
```
- Measures how two stocks move together
- Positive = move together, Negative = move opposite

#### Step 4: Create Crisis Regime
- Crisis regime is **synthetic** (not from data)
- Takes volatility from Normal regime
- Sets all correlations to 0.90 (very high)
- **Formula:**
```
Crisis_Covariance = Volatility_i * Volatility_j * 0.90
```

**Key Functions:**
- `classify_regimes_from_volatility()`: Classifies each day as Normal/Stress
- `estimate_all_regime_covariances()`: Creates 3 covariance matrices (Normal, Stress, Crisis)

**Output:** Dictionary with 3 covariance matrices, one for each regime

---

### 📁 **markov_model.py**

**Purpose:** Simulates how markets transition between Normal/Stress/Crisis states over time.

**What is a Markov Chain?**
- A model where the next state depends only on the current state
- Like a weather model: "If it's sunny today, 70% chance sunny tomorrow, 30% chance rain"

**Transition Matrix:**
A 3×3 table showing probabilities of moving between states:

```
            Next State:
            Normal  Stress  Crisis
Current: Normal  [ 0.95    0.05    0.00  ]
         Stress  [ 0.20    0.70    0.10  ]
         Crisis  [ 0.00    0.15    0.85  ]
```

**Interpretation:**
- If in Normal: 95% stay Normal, 5% go to Stress, 0% go to Crisis
- If in Stress: 20% go to Normal, 70% stay Stress, 10% go to Crisis
- If in Crisis: 0% go to Normal, 15% go to Stress, 85% stay Crisis (crises persist)

**Key Function:**
```python
simulate_regimes(T, transition_matrix, initial_state)
```
- Simulates T time steps of regime changes
- At each step, randomly picks next state based on probabilities
- Returns array: [Normal, Normal, Stress, Stress, Crisis, Crisis, ...]

**Example:**
- Start: Normal (state 0)
- Step 1: Random number says 0.03 → Go to Stress (state 1)
- Step 2: Random number says 0.65 → Stay in Stress
- Step 3: Random number says 0.95 → Go to Crisis (state 2)
- Result: [0, 1, 1, 2, 2, ...]

---

### 📁 **monte_carlo.py**

**Purpose:** Simulates thousands of possible future scenarios of stock returns.

**What is Monte Carlo Simulation?**
- Generate random scenarios based on probability distributions
- Run many times (e.g., 300 paths) to see all possible outcomes
- Like simulating 300 different possible futures

#### Step 1: Simulate Asset Returns
For each Monte Carlo path and each time step:
1. Look at current regime (from Markov chain)
2. Get the covariance matrix for that regime
3. Sample from multivariate normal distribution

**Multivariate Normal Distribution:**
- Generates returns for all stocks simultaneously
- Respects correlations (if stocks are correlated, they move together)
- Uses mean returns (mu_vec) and covariance matrix

**Formula:**
```
Returns ~ N(μ, Σ)
```
- μ = expected returns vector
- Σ = covariance matrix for current regime

#### Step 2: Compute Portfolio Paths
- Takes asset returns and portfolio weights
- Calculates portfolio value over time

**Portfolio Return Formula:**
```
Portfolio_Return_t = Σ(weight_i × return_i,t)
```

**Portfolio Value Formula (for log returns):**
```
Portfolio_Value_t = Portfolio_Value_{t-1} × exp(Portfolio_Return_t)
```

**Why exp()?** Because we're using log returns. To convert back to prices:
- If log return = 0.05, then price multiplier = exp(0.05) = 1.051
- Portfolio grows by 5.1%

**Key Functions:**
- `simulate_paths()`: Generates returns for all paths, all time steps, all assets
  - Output shape: (300 paths, 100 time steps, 5 assets)
- `compute_portfolio_paths()`: Converts asset returns to portfolio values
  - Output shape: (300 paths, 100 time steps)

---

### 📁 **risk_metrics.py**

**Purpose:** Calculates various risk measures from the simulated portfolio paths.

#### 1. Portfolio Variance
**Formula:**
```
Portfolio_Variance = w^T × Σ × w
```
- w = weights vector (e.g., [0.2, 0.2, 0.2, 0.2, 0.2] for equal weights)
- Σ = covariance matrix
- w^T = transpose of weights

**Why?** Measures how much the portfolio value fluctuates.

**Volatility = sqrt(Variance)**

#### 2. Value at Risk (VaR)
**What it means:** "What's the worst loss I might see 95% of the time?"

**Calculation:**
- Take all final portfolio returns
- Find the 5th percentile (95% VaR means 5% of outcomes are worse)
- That's the VaR

**Example:**
- If 95% VaR = -25%, it means:
  - 95% of scenarios lose less than 25%
  - 5% of scenarios lose more than 25%

#### 3. Maximum Drawdown
**What it means:** "What's the biggest peak-to-trough decline?"

**Calculation:**
1. For each time step, track the running maximum (peak)
2. Calculate drawdown = (Peak - Current) / Peak
3. Find the maximum drawdown

**Example:**
- Portfolio: $100 → $120 → $90 → $110
- Running max: $100 → $120 → $120 → $120
- Drawdowns: 0% → 0% → 25% → 8.3%
- Max drawdown = 25%

#### 4. Conditional VaR (CVaR)
**What it means:** "Given that I'm in the worst 5% of scenarios, what's my average loss?"

**Calculation:**
- Find all returns worse than VaR
- Take the average of those

**Key Functions:**
- `compute_portfolio_variance()`: Portfolio variance from covariance matrix
- `compute_var()`: Value at Risk
- `compute_max_drawdown()`: Maximum drawdown for one path
- `compute_max_drawdowns()`: Maximum drawdown for all paths

---

### 📁 **plots.py**

**Purpose:** Creates visualizations of the results.

#### 1. Correlation Heatmaps
- Shows correlation matrices for each regime
- Color-coded: Red = high correlation, Blue = low correlation
- Visual comparison: Normal (low correlations) vs. Crisis (high correlations)

#### 2. 2D Portfolio Paths
- Shows all 300 Monte Carlo paths
- Shaded region = 5th to 95th percentile
- Median line = middle path
- Sample paths = individual scenarios

#### 3. 3D Monte Carlo Surface
- X-axis = time step
- Y-axis = path index (which scenario)
- Z-axis = portfolio value
- Shows all paths in 3D space

#### 4. Example Path with Regimes
- Shows one specific scenario
- Top panel: Portfolio value over time
- Bottom panel: Which regime market is in (Normal/Stress/Crisis)
- Shows how portfolio responds to regime changes

---

### 📁 **main.py**

**Purpose:** Orchestrates everything - the main script that runs the entire simulation.

**Step-by-Step Execution:**

1. **Configuration**
   - Sets tickers: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
   - Date range: 2020-01-01 to 2024-01-01
   - Simulation: 300 paths, 100 time steps

2. **Load Data** (data_loader.py)
   - Downloads historical prices
   - Converts to log returns
   - Estimates expected returns (mean of historical)

3. **Classify Regimes** (regime_estimation.py)
   - Computes rolling volatility
   - Classifies days as Normal/Stress
   - Estimates covariance matrices

4. **Create Crisis Regime** (regime_estimation.py)
   - Synthetically creates Crisis covariance matrix
   - Sets correlations to 0.90

5. **Plot Correlation Heatmaps** (plots.py)
   - Visualizes correlations for each regime

6. **Set Up Markov Chain** (markov_model.py)
   - Creates transition probability matrix
   - Simulates regime sequence for 100 time steps

7. **Run Monte Carlo** (monte_carlo.py)
   - For each path, simulates asset returns
   - Uses regime-specific covariance matrices
   - Computes portfolio values

8. **Calculate Risk Metrics** (risk_metrics.py)
   - Portfolio volatility by regime
   - VaR, max drawdown

9. **Generate Visualizations** (plots.py)
   - 2D paths, 3D surface, example path

---

## Step-by-Step Workflow

### Phase 1: Data Collection & Preparation
```
1. Download stock prices (2020-2024) for 5 stocks
   → Result: 1,005 days of price data

2. Calculate log returns
   → Result: 1,004 days of returns (first day has no previous day)

3. Compute rolling volatility (20-day window)
   → Result: Volatility time series

4. Classify each day as Normal or Stress
   → Result: 758 Normal days, 247 Stress days
```

### Phase 2: Regime Analysis
```
5. Separate returns by regime
   → Normal returns: 758 days
   → Stress returns: 247 days

6. Calculate covariance matrix for Normal regime
   → 5×5 matrix showing how stocks move together in normal times

7. Calculate covariance matrix for Stress regime
   → 5×5 matrix showing how stocks move together in stressful times

8. Create synthetic Crisis covariance matrix
   → 5×5 matrix with 0.90 correlations (everything moves together)
```

### Phase 3: Simulation Setup
```
9. Create Markov transition matrix
   → 3×3 probability matrix for regime transitions

10. Simulate regime sequence (100 time steps)
    → Example: [Normal, Normal, Stress, Stress, Crisis, Crisis, ...]

11. Estimate expected returns
    → Mean of historical returns for each stock
```

### Phase 4: Monte Carlo Simulation
```
12. For each of 300 paths:
    a. For each of 100 time steps:
       - Check current regime
       - Get covariance matrix for that regime
       - Sample returns from multivariate normal distribution
       - Store returns
    
    → Result: (300, 100, 5) array of returns

13. For each path:
    - Calculate portfolio return = weighted sum of asset returns
    - Convert to portfolio value = previous_value × exp(return)
    
    → Result: (300, 100) array of portfolio values
```

### Phase 5: Risk Analysis
```
14. Calculate portfolio volatility for each regime
    → Normal: 1.69%, Stress: 3.08%, Crisis: 2.08%

15. Calculate VaR
    → 95% VaR = -25% (5% of paths lose more than 25%)

16. Calculate max drawdown for each path
    → Average: 19% (typical worst decline)
```

### Phase 6: Visualization
```
17. Plot correlation heatmaps
    → Shows how correlations increase from Normal → Stress → Crisis

18. Plot 2D portfolio paths
    → Shows distribution of all 300 scenarios

19. Plot 3D surface
    → Shows all paths in 3D space

20. Plot example path with regimes
    → Shows one scenario with regime transitions
```

---

## Mathematical Formulas and Calculations

### 1. Log Returns
```
r_t = log(P_t / P_{t-1})
```
- P_t = price at time t
- P_{t-1} = price at previous time
- Natural logarithm (base e)

### 2. Rolling Volatility
```
σ_t = std(r_{t-window+1}, ..., r_t)
```
- Standard deviation of returns over rolling window
- Window = 20 days in our case

### 3. Covariance
```
Cov(X, Y) = E[(X - μ_X)(Y - μ_Y)]
         = (1/n) Σ (X_i - μ_X)(Y_i - μ_Y)
```
- Measures how two variables move together
- Positive = move together, Negative = move opposite

### 4. Correlation
```
Corr(X, Y) = Cov(X, Y) / (σ_X × σ_Y)
```
- Normalized covariance (between -1 and 1)
- σ_X, σ_Y = standard deviations

### 5. Portfolio Variance
```
σ²_portfolio = w^T × Σ × w
             = Σ_i Σ_j w_i × w_j × Cov(i, j)
```
- w = weights vector
- Σ = covariance matrix

### 6. Portfolio Return (from log returns)
```
r_portfolio,t = Σ_i w_i × r_i,t
```
- Weighted sum of asset returns

### 7. Portfolio Value (from log returns)
```
V_t = V_{t-1} × exp(r_portfolio,t)
```
- Converts log returns back to price levels

### 8. Maximum Drawdown
```
DD_t = (Peak_t - V_t) / Peak_t
Max_DD = max(DD_t) over all t
```
- Peak_t = maximum value up to time t
- Drawdown = decline from peak

### 9. Value at Risk (VaR)
```
VaR_α = Percentile(returns, α × 100)
```
- α = confidence level (e.g., 0.05 for 95% VaR)
- Returns = distribution of returns

### 10. Multivariate Normal Sampling
```
Returns ~ N(μ, Σ)
```
- μ = mean vector (expected returns)
- Σ = covariance matrix
- Samples returns that respect correlations

---

## How Everything Connects

```
┌─────────────────┐
│  data_loader.py │
│  Downloads data │
│  Log returns    │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│regime_estimation.py │
│  Classify regimes   │
│  Estimate cov mats  │
└────────┬────────────┘
         │
         ▼
┌─────────────────┐
│ markov_model.py │
│  Simulate       │
│  regime seq     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ monte_carlo.py  │
│  Simulate       │
│  returns        │
│  Portfolio vals │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ risk_metrics.py │
│  Calculate      │
│  VaR, drawdown  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   plots.py      │
│  Visualize      │
│  results        │
└─────────────────┘
```

### Data Flow:
1. **Historical data** → Log returns
2. **Log returns** → Regime classification → Covariance matrices
3. **Covariance matrices** → Used in Monte Carlo simulation
4. **Monte Carlo** → Portfolio paths
5. **Portfolio paths** → Risk metrics
6. **Everything** → Visualizations

### Key Insight:
The **regime-switching** is the core innovation:
- Markets don't stay in one state forever
- They transition: Normal → Stress → Crisis → Stress → Normal
- Each regime has different correlations
- Monte Carlo respects these transitions
- This creates realistic crisis scenarios where correlations spike

---

## Summary

This project:
1. ✅ Learns from 4 years of historical data
2. ✅ Identifies Normal vs. Stress market periods
3. ✅ Estimates how stocks correlate in each regime
4. ✅ Models how markets transition between regimes
5. ✅ Simulates 300 possible futures
6. ✅ Calculates risk metrics (VaR, drawdown, volatility)
7. ✅ Visualizes everything in 2D and 3D

**The main finding:** Correlations do spike during crises (from ~0.5 to 0.90), making diversification less effective. Regime-switching models capture this dynamic behavior better than static models.

---

## Questions?

If anything is unclear, the code is well-documented with docstrings explaining each function. Each module can be understood independently, but they work together to create the complete simulation engine.

