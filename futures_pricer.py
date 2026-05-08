import math
from dataclasses import dataclass


@dataclass
class FuturesContract:
    """
    Futures contract inputs supplied by the user.
    """
    S: float
    T: float
    r: float = 0.0
    c: float = 0.0
    q: float = 0.0

    def __post_init__(self):
        self.S = _validate_positive_number(self.S, "S")
        self.T = _validate_positive_number(self.T, "T")
        self.r = _validate_number(self.r, "r")
        self.c = _validate_number(self.c, "c")
        self.q = _validate_number(self.q, "q")


class FuturesPricer:
    """
    Cost-of-carry futures pricer.

    Formula:
        F = S * exp((r + c - q) * T)

    where:
        S = current spot price
        r = risk-free rate
        c = storage cost or other carrying cost
        q = dividend yield or income yield
        T = time to maturity in years
    """

    def __init__(self, contract: FuturesContract):
        self.contract = contract

    def price(self):
        S = self.contract.S
        T = self.contract.T
        r = self.contract.r
        c = self.contract.c
        q = self.contract.q

        return S * math.exp((r + c - q) * T)

    def summary(self):
        return {
            "model": self.__class__.__name__,
            "spot_price": self.contract.S,
            "time_to_maturity": self.contract.T,
            "risk_free_rate": self.contract.r,
            "cost_of_carry": self.contract.c,
            "dividend_yield": self.contract.q,
            "futures_price": self.price(),
        }


def price_futures(
    S,
    T,
    r=0.0,
    c=0.0,
    q=0.0,
):
    """
    Quick function to calculate a futures price.

    Examples
    --------
    price_futures(S=100, T=0.5, r=0.05, c=0.02, q=0.01)
    """
    contract = FuturesContract(
        S=S,
        T=T,
        r=r,
        c=c,
        q=q,
    )
    return FuturesPricer(contract).price()


def _validate_positive_number(value, name):
    number = _validate_number(value, name)

    if number <= 0:
        raise ValueError(f"{name} must be positive")

    return number


def _validate_number(value, name):
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be a number") from exc
