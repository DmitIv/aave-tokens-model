# AAVE <> Lido simplify tokens model.

The implementation of rebasable aStETH and non-rebasable variableDebtStETH.
Also includes the market model with coherent deposits->borrowings->rebasings->
repays.

## Usage

1. Clone the repo

2. In the root of repo:

```shell
pip instal poetry
poetry install
```

3. Run tests:

```shell
poetry run pytest
```

4. Run the simple market model:

```shell
poetry run aave_market_model
```

## Adjustment the market model

You are able to adjust the market model steps in `__main__.py` of
`aave_tokens_model` package.