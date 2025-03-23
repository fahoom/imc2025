# IMC Prosperity 2025

## Usage

To use this project, you require the [`uv`](https://docs.astral.sh/uv/#installation) package manager.

## Project Structure

`rounds/`: Contains the models to be sumbitted for each round. A template for each round's script can be found in `base.py`. `datamodel.py` contains a description of the datamodel sourced from the [IMC Notion](https://imc-prosperity.notion.site/Programming-resources-19ee8453a09381e4b841f09d4add277d) for local development and type hints.

## Backtesting

For backtesting, firstly ensure that you have setup the uv project properly. We use a ready-made [backtesting framework](https://github.com/jmerle/imc-prosperity-3-backtester).

A sample command to test the tutorial round on data from round 0:
```
  uv run prosperity3bt rounds/tutorial.py 0
```

This will produce a file that you can then drag and drop onto [https://jmerle.github.io/imc-prosperity-3-visualizer/].
Supposedly, adding `--vis` will get it to automatically open the backtest, but this has not worked for me on Safari (Something about cross-origin requests).
