from abc import ABC, abstractmethod


class OptionPricer(ABC):
    """
    Abstract base class for option pricing models.

    Any specific pricing model, such as BSM, Binomial Tree,
    Monte Carlo, or Local Volatility model, should inherit from this class.
    """

    def __init__(self, option):
        self.option = option

    @abstractmethod
    def price(self):
        """
        Return the option price.
        """
        pass

    @abstractmethod
    def greeks(self):
        """
        Return option Greeks such as delta, gamma, vega, theta, and rho.
        """
        pass

    def summary(self):
        """
        Return a simple summary of the pricing result.
        """
        return {
            "model": self.__class__.__name__,
            "option": self.option,
            "price": self.price(),
            "greeks": self.greeks(),
        }