import math
from base_pricer import OptionPricer
from instruments import EuropeanOption


class BSMEuropeanPricer(OptionPricer):
    """
    Black-Scholes-Merton pricer for European call and put options.
    """

    def __init__(self, option: EuropeanOption):
        super().__init__(option)

    @staticmethod
    def _normal_cdf(x):
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    @staticmethod
    def _normal_pdf(x):
        return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)

    def _d1_d2(self):
        S = self.option.S
        K = self.option.K
        T = self.option.T
        r = self.option.r
        q = self.option.q
        sigma = self.option.sigma

        d1 = (
            math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T
        ) / (sigma * math.sqrt(T))

        d2 = d1 - sigma * math.sqrt(T)

        return d1, d2

    def price(self):
        S = self.option.S
        K = self.option.K
        T = self.option.T
        r = self.option.r
        q = self.option.q
        option_type = self.option.option_type

        d1, d2 = self._d1_d2()

        if option_type == "call":
            return (
                S * math.exp(-q * T) * self._normal_cdf(d1)
                - K * math.exp(-r * T) * self._normal_cdf(d2)
            )

        return (
            K * math.exp(-r * T) * self._normal_cdf(-d2)
            - S * math.exp(-q * T) * self._normal_cdf(-d1)
        )

    def greeks(self):
        S = self.option.S
        K = self.option.K
        T = self.option.T
        r = self.option.r
        q = self.option.q
        sigma = self.option.sigma
        option_type = self.option.option_type

        d1, d2 = self._d1_d2()
        pdf_d1 = self._normal_pdf(d1)

        gamma = math.exp(-q * T) * pdf_d1 / (S * sigma * math.sqrt(T))
        vega = S * math.exp(-q * T) * pdf_d1 * math.sqrt(T)

        if option_type == "call":
            delta = math.exp(-q * T) * self._normal_cdf(d1)

            theta = (
                -S * math.exp(-q * T) * pdf_d1 * sigma / (2 * math.sqrt(T))
                - r * K * math.exp(-r * T) * self._normal_cdf(d2)
                + q * S * math.exp(-q * T) * self._normal_cdf(d1)
            )

            rho = K * T * math.exp(-r * T) * self._normal_cdf(d2)

        else:
            delta = math.exp(-q * T) * (self._normal_cdf(d1) - 1)

            theta = (
                -S * math.exp(-q * T) * pdf_d1 * sigma / (2 * math.sqrt(T))
                + r * K * math.exp(-r * T) * self._normal_cdf(-d2)
                - q * S * math.exp(-q * T) * self._normal_cdf(-d1)
            )

            rho = -K * T * math.exp(-r * T) * self._normal_cdf(-d2)

        return {
            "delta": delta,
            "gamma": gamma,
            "vega": vega / 100,
            "theta": theta / 365,
            "rho": rho / 100,
        }