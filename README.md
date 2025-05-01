# IMC Trading Competition Analysis

## Overview
This repository contains my analysis and trading approach for the IMC Trading Competition. I focused on understanding relationships between products and developing effective statistical trading strategies across multiple rounds.

## Round 2 Analysis

### Products Analyzed
- Squid Ink
- Resin
- Kelp

### Key Findings
I performed extensive analysis with various plots and visualizations that can be found in the notebook section of this repository. Some notable findings include:

- Discovered that Resin exhibits mean-reverting properties
- When plotting the difference between Squid Ink and Resin signals, we found a pattern that was symmetrical to the Squid Ink pattern with respect to a horizontal line
- This relationship provided key insights that informed our trading strategy for Squid Ink using Resin as a reference

### Analysis Approach
The repository includes Jupyter notebooks with detailed plots tracking the day-to-day movements of Squid Ink and related analysis that guided our trading decisions.

## Round 3 Analysis

### Products Analyzed
- Jams
- Croissants
- Djembes
- Baskets 1
- Baskets 2

### Key Findings and Strategies
For this round, I expanded my statistical analysis approach:

- **Jams Analysis**: 
  - Applied stationarity testing (ACF test) which revealed Jams was not stationary
  - Used differentiation to transform the signal
  - Implemented EWMA (Exponentially Weighted Moving Average) models on the differentiated signal
  - Traded based on forecasts generated from these models

- **Croissants Analysis**:
  - Found that standard EWMA was insufficient for effective predictions
  - Developed a modified "moving alpha" approach to improve the EWMA model
  - The moving alpha represented the impact of the most recent observation (X_i) on the next price
  - Made alpha a function of trailing volatility, which significantly improved performance

- **Basket Trading Strategy**:
  - Applied these forecasting models to trade basket combinations
  - Specifically traded baskets consisting of 4 croissants and 2 jams
  - Used the forecasts to determine optimal trading positions

## Round 4 Analysis

### Products Analyzed
- Volcanic Rock
- Options on Volcanic Rock (various strike prices)

### Options Trading Strategy
For the final round, I developed an options trading approach:

- **Volatility Estimation**:
  - Used trailing volatility as an estimate for Volcanic Rock's future volatility
  - Applied this volatility estimate to inform options pricing and trading decisions

- **Directional Options Trading**:
  - Implemented strategies to trade options based on directional predictions of the underlying Volcanic Rock

- **Butterfly Spread Strategy**:
  - Created butterfly spread positions by simultaneously buying and selling call options at different strike prices
  - This approach allowed for profiting from specific price movement scenarios while managing risk
  - Strike price selection was informed by volatility estimates and directional predictions

## Learning Journey and Reflections

### Knowledge Gained
I entered this competition with no prior trading experience and gained valuable insights into multiple trading strategies and concepts:
- Mean reversion trading strategies
- Momentum trading approaches
- Volatility trading techniques
- Options trading fundamentals
- Statistical models for price prediction (EWMA, ARIMA)

### Areas for Improvement
Upon reflection, several aspects could have been improved:
- **Risk Management**: Should have implemented proper risk management tactics such as stop-loss and take-profit orders
- **Hedging**: Failed to adequately hedge positions during options trading, exposing the strategy to unnecessary risk
- **Volatility Modeling**: Could have used the Black-Scholes model to extract implied volatility rather than relying solely on trailing volatility as an estimate
- **Position Sizing**: Better position sizing techniques could have optimized returns while minimizing risk

This competition provided an invaluable learning experience that significantly enhanced my understanding of algorithmic trading and financial markets.
