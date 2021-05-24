import decimal

import click
import pytest

from src import constant, main


@pytest.mark.parametrize("instrument", ("BTCETH", "BTCUSD"))
def test_pair_exceeding_digits(instrument):
    with pytest.raises(click.exceptions.BadParameter):
        main.validate_order_size(instrument, decimal.Decimal("1.1234567"))


@pytest.mark.parametrize("max_digits, instrument", (
        (constant.Instruments.MAX_DIGITS_CRYPTO, "BTCETH"),
        (constant.Instruments.MAX_DIGITS_FIAT, "BTCUSD"),
))
def test_max_digits(max_digits, instrument):
    price = decimal.Decimal("0.1") ** max_digits

    try:
        main.validate_order_size(instrument, price)
    except Exception as e:
        assert False, f"{e}"
