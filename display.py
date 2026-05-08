import pandas as pd


class PricerDisplayVisitor:
    """
    Visitor class for displaying option pricing results as a vertical table.
    """

    def visit(self, pricer):
        price = pricer.price()
        greeks = pricer.greeks()
        option = pricer.option

        data = {
            "Model": pricer.__class__.__name__,
            "Option Type": option.option_type,
            "Spot": option.S,
            "Strike": option.K,
            "Maturity": option.T,
            "Rate": option.r,
            "Dividend Yield": option.q,
            "Volatility": option.sigma,
            "Price": price,
            "Delta": greeks.get("delta"),
            "Gamma": greeks.get("gamma"),
            "Vega": greeks.get("vega"),
            "Theta": greeks.get("theta"),
            "Rho": greeks.get("rho"),
        }

        return pd.DataFrame.from_dict(data, orient="index", columns=["Value"])


def display_pricer_result(pricer):
    visitor = PricerDisplayVisitor()
    return visitor.visit(pricer)