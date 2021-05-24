import datetime
import decimal
import logging
import sys
import uuid

import click
import yaml

from src import constant
from src.util import http_client, log


logger = logging.getLogger()


def validate_order_size(instrument: str, quantity: decimal.Decimal) -> None:
    """
    Quantity precision (base currency) is 2 decimal digits for crypto-to-crypto instruments, 4 for crypto-to-fiat and
    crypto-to-stablecoin instruments.
    """
    digits = quantity.as_tuple()[-1] * (-1)
    is_fiat_or_stablecoin_pair = any([fiat in instrument for fiat in constant.Instruments.supported_fiat_currencies])
    logger.debug(f"Digits: {digits}")
    logger.debug(f"is fiat: {is_fiat_or_stablecoin_pair}")

    if is_fiat_or_stablecoin_pair:
        if digits > constant.Instruments.MAX_DIGITS_FIAT:
            raise click.exceptions.BadParameter(
                f"Fiat and stablecoins pairs support only {constant.Instruments.MAX_DIGITS_FIAT} decimal digits, "
                f"got {digits}!")
    else:
        if digits > constant.Instruments.MAX_DIGITS_CRYPTO:
            raise click.exceptions.BadParameter(
                f"Crypto pairs support only {constant.Instruments.MAX_DIGITS_CRYPTO} decimal digits, "
                f"got {digits}!")


@click.group()
@click.pass_context
def cli(ctx) -> None:  # type: ignore
    with open(constant.Path.CONFIG) as f:
        config = yaml.safe_load(f)

    log.configure_logger(logger, constant.Path.LOG, config[constant.ConfigFile.LOG_LEVEL])

    ctx.obj = http_client.HttpClient(
        config[constant.ConfigFile.BASE_URL],
        config[constant.ConfigFile.AUTH_TOKEN],
        config[constant.ConfigFile.MAX_CONNECTION_RETRIES],
        config[constant.ConfigFile.CONNECTION_TIMEOUT],
        config[constant.ConfigFile.SLEEP_BETWEEN_RECONNECTS]
    )


@cli.command()
@click.pass_context
def list_instruments(ctx) -> None:  # type: ignore
    """
    List all your tradable instruments. Please ask your sales representative if you want access to more instruments.
    """
    click.echo("Requesting instruments...")
    response = ctx.obj.get_instruments()
    click.echo("\n".join(dct["name"] for dct in response))


@cli.command()
@click.pass_context
def show_balance(ctx) -> None:  # type: ignore
    """
    This shows the available balances in the supported currencies. Your account balance is the net result of all your
    trade and settlement activity. A positive number indicates that B2C2 owes you the amount of the given currency.
    A negative number means that you owe B2C2 the given amount.
    """
    click.echo("Requesting balance...")
    response = ctx.obj.get_balance()
    click.echo("\n".join(f"{k}: {v}" for k, v in response.items()))


@click.option(
    "--quantity",
    required=True,
    type=decimal.Decimal,
    help="Quantity precision (base currency) is 2 decimal digits for crypto-to-crypto instruments, 4 for crypto-to-fiat"
         " and crypto-to-stablecoin instruments."
)
@click.option("--side", required=True, type=click.Choice(("buy", "sell")))
@click.option("--instrument", required=True, type=str, help="One of available instruments")
@cli.command()
@click.pass_context
def get_rfq(ctx, quantity: decimal.Decimal, side: str, instrument: str) -> None:    # type: ignore
    """
    Post a Request For Quote
    """
    validate_order_size(instrument, quantity)

    click.echo("Sending request...")
    data = {
        "instrument": instrument,
        "side": side,
        "quantity": quantity,
        "client_rfq_id": str(uuid.uuid4())
    }
    response = ctx.obj.send_request_for_quote(data)
    click.echo("\n".join(f"{k}: {v}" for k, v in response.items()))
    click.confirm("\nExecute RFQ?", abort=True)

    # check that the RFQ is still valid
    valid_until = response["valid_until"]
    dt_until = datetime.datetime.strptime(valid_until, "%Y-%m-%dT%H:%M:%S.%f%z")
    dt_now = datetime.datetime.now(datetime.timezone.utc)
    time_available = dt_now - dt_until

    if time_available.seconds > constant.APIEndpoint.MIN_ORDER_VALID_SECONDS:
        ctx.invoke(send_order, response["price"], quantity, side, instrument, valid_until)
    else:
        logger.error(f"CFQ was valid till {valid_until}")
        raise RuntimeError("CFQ no longer valid.")


@click.option("--price", required=True, type=str, help="FOK order price.")
@click.option(
    "--quantity",
    required=True,
    type=decimal.Decimal,
    help="Quantity precision (base currency) is 2 decimal digits for crypto-to-crypto instruments, 4 for crypto-to-fiat"
         " and crypto-to-stablecoin instruments."
)
@click.option("--side", required=True, type=click.Choice(("buy", "sell")))
@click.option("--instrument", required=True, type=str, help="One of available instruments")
@click.option("--valid-until", required=True, type=str, help="Datetime e.g. 2011-11-23T23:59:59")
@cli.command()
@click.pass_context
def send_order(ctx, price: str, quantity: decimal.Decimal, side: str, instrument: str, valid_until: str) -> None:  # type: ignore
    """
    API endpoint to send orders. At the moment, we only support FOK order type.
    """
    validate_order_size(instrument, quantity)
    click.echo("Sending order...")

    data = {
        "instrument": instrument,
        "side": side,
        "quantity": quantity,
        "client_order_id": str(uuid.uuid4()),
        "price": price,
        "order_type": "FOK",
        "valid_until": valid_until,
        "executing_unit": "risk-adding-strategy"
    }
    response = ctx.obj.send_order(data)

    executed_price = response['executed_price']
    if executed_price is None:
        click.secho("Order rejected.", fg="red")
        return
    click.secho(f"Order placed at {executed_price}", fg="green")

    for trade in response["trades"]:
        click.secho(trade, fg="blue")

    ctx.invoke(show_balance)


def safe_entry_point():
    """
    Click requires a function as an entry point if we want to handle exceptions ourselves.
    """
    try:
        cli()
    except Exception as e:
        logger.exception(e)
        click.secho(f"Error: {e}", fg="red")
        sys.exit(2)


if __name__ == "__main__":
    safe_entry_point()
