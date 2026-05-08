from dataclasses import dataclass


@dataclass
class EuropeanOption:
    S: float
    K: float
    T: float
    r: float
    q: float
    sigma: float
    option_type: str = "call"

    def __post_init__(self):
        self.option_type = self.option_type.lower()
        self.validate()

    def validate(self):
        if self.S <= 0:
            raise ValueError("S must be positive.")

        if self.K <= 0:
            raise ValueError("K must be positive.")

        if self.T <= 0:
            raise ValueError("T must be positive.")

        if self.sigma <= 0:
            raise ValueError("sigma must be positive.")

        if self.option_type not in ["call", "put"]:
            raise ValueError("option_type must be either 'call' or 'put'.")


@dataclass
class AmericanOption:
    S: float
    K: float
    T: float
    r: float
    q: float
    sigma: float
    option_type: str

    
@dataclass
class BarrierOption:
    pass


@dataclass
class AsianOption:
    pass


@dataclass
class BasketOption:
    pass