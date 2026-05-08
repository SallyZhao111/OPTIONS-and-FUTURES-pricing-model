from datetime import date, datetime, timedelta

# get parameter S_t --> equity price
def get_stock_price(ticker=None, known_price=None, price_date="today"):
    """
    Get a stock price for pricing calculations.

    If the user already knows the stock price, pass it as known_price.
    If known_price is not given, pass a ticker symbol and the price will be
    fetched from Yahoo Finance using yfinance.

    price_date can be "today" or a date in YYYY-MM-DD format.

    For an exact Yahoo Finance lookup, returns OHLC:
        {"date": "YYYY-MM-DD", "open": price, "high": price, "low": price, "close": price}

    If the requested date is not a trading day, returns:
        {
            "requested_date": "YYYY-MM-DD",
            "previous": {"date": "YYYY-MM-DD", "open": price, "high": price, "low": price, "close": price},
            "next": {"date": "YYYY-MM-DD", "open": price, "high": price, "low": price, "close": price},
        }
    """
    if known_price is not None:
        return _validate_positive_number(known_price, "known_price")

    if not ticker:
        raise ValueError("ticker is required when known_price is not provided")

    try:
        import yfinance as yf
    except ImportError as exc:
        raise ImportError(
            "yfinance is required to fetch stock prices. Install it with: pip install yfinance"
        ) from exc

    stock = yf.Ticker(ticker)

    if price_date in (None, "", "today"):
        history = stock.history(period="1d")
        if history.empty:
            raise ValueError(f"No price data found for ticker {ticker!r} on {price_date!r}")

        return _format_price_row(history.iloc[-1], history.index[-1])
    else:
        target_date = _to_date(price_date, "price_date")
        return _get_price_for_date_or_neighbors(stock, target_date, ticker)


def get_stock_ohlc(ticker, price_date="today"):
    """
    Get stock OHLC data from Yahoo Finance.

    price_date can be "today" or a date in YYYY-MM-DD format.
    If price_date is not a trading day, returns both previous and next trading
    day OHLC data.
    """
    return get_stock_price(ticker=ticker, known_price=None, price_date=price_date)


# get parameter T--> time to maturity
def get_time_to_maturity(expiry_date, from_date="today", day_count=252, count_type="business"):
    """
    Calculate the time left until an option expires.

    from_date can be "today" or any date in YYYY-MM-DD format.

    day_count can be:
        252 - business-day year fraction
        365 - calendar-day year fraction
        "business" - shortcut for count_type="business" and day_count=252
        "calendar" - shortcut for count_type="calendar" and day_count=365

    count_type can be:
        "business" - count US market business days, excluding weekends and
                     standard US market holidays
        "calendar" - count real calendar days
    """
    if isinstance(day_count, str):
        count_type = day_count
        day_count = 252 if count_type.lower() == "business" else 365

    expiry = _to_date(expiry_date, "expiry_date")
    start = date.today() if from_date in (None, "", "today") else _to_date(from_date, "from_date")

    if day_count <= 0:
        raise ValueError("day_count must be positive")

    if expiry < start:
        raise ValueError("expiry_date must be on or after from_date")

    count_type = count_type.lower()
    if count_type == "business":
        days_left = _count_us_market_business_days(start, expiry)
    elif count_type == "calendar":
        days_left = (expiry - start).days
    else:
        raise ValueError("count_type must be either 'business' or 'calendar'")

    return {
        "days": days_left,
        "years": days_left / day_count,
        "count_type": count_type,
    }


def _to_date(value, name):
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError(f"{name} must be in YYYY-MM-DD format") from exc

    raise TypeError(f"{name} must be a string, date, or datetime")


def _get_price_for_date_or_neighbors(stock, target_date, ticker, search_days=7):
    start = target_date
    end = target_date + timedelta(days=1)
    history = stock.history(start=start, end=end)

    if not history.empty:
        return _format_price_row(history.iloc[-1], history.index[-1])

    start = target_date - timedelta(days=search_days)
    end = target_date + timedelta(days=search_days + 1)
    history = stock.history(start=start, end=end)

    if history.empty:
        raise ValueError(
            f"No price data found for ticker {ticker!r} near {target_date.isoformat()!r}"
        )

    previous_history = history[
        [index.date() < target_date for index in history.index]
    ]
    next_history = history[
        [index.date() > target_date for index in history.index]
    ]

    previous_price = None
    next_price = None

    if not previous_history.empty:
        previous_price = _format_price_row(
            previous_history.iloc[-1],
            previous_history.index[-1],
        )

    if not next_history.empty:
        next_price = _format_price_row(
            next_history.iloc[0],
            next_history.index[0],
        )

    return {
        "requested_date": target_date.isoformat(),
        "previous": previous_price,
        "next": next_price,
    }


def _format_price_row(row, index):
    return {
        "date": index.date().isoformat(),
        "open": _validate_positive_number(row["Open"], "open_price"),
        "high": _validate_positive_number(row["High"], "high_price"),
        "low": _validate_positive_number(row["Low"], "low_price"),
        "close": _validate_positive_number(row["Close"], "close_price"),
    }


def _count_us_market_business_days(start, expiry):
    days = 0
    current = start + timedelta(days=1)

    while current <= expiry:
        if _is_us_market_business_day(current):
            days += 1
        current += timedelta(days=1)

    return days


def _is_us_market_business_day(day):
    return day.weekday() < 5 and day not in _us_market_holidays(day.year)


def _us_market_holidays(year):
    holidays = {
        _observed_holiday(date(year, 1, 1)),
        _nth_weekday_of_month(year, 1, 0, 3),   # Martin Luther King Jr. Day
        _nth_weekday_of_month(year, 2, 0, 3),   # Presidents' Day
        _good_friday(year),
        _last_weekday_of_month(year, 5, 0),     # Memorial Day
        _observed_holiday(date(year, 7, 4)),
        _nth_weekday_of_month(year, 9, 0, 1),   # Labor Day
        _nth_weekday_of_month(year, 11, 3, 4),  # Thanksgiving Day
        _observed_holiday(date(year, 12, 25)),
    }

    if year >= 2022:
        holidays.add(_observed_holiday(date(year, 6, 19)))  # Juneteenth

    return holidays


def _observed_holiday(holiday):
    if holiday.weekday() == 5:
        return holiday - timedelta(days=1)
    if holiday.weekday() == 6:
        return holiday + timedelta(days=1)
    return holiday


def _nth_weekday_of_month(year, month, weekday, n):
    current = date(year, month, 1)

    while current.weekday() != weekday:
        current += timedelta(days=1)

    return current + timedelta(days=7 * (n - 1))


def _last_weekday_of_month(year, month, weekday):
    if month == 12:
        current = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        current = date(year, month + 1, 1) - timedelta(days=1)

    while current.weekday() != weekday:
        current -= timedelta(days=1)

    return current


def _good_friday(year):
    return _easter_sunday(year) - timedelta(days=2)


def _easter_sunday(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1

    return date(year, month, day)


def _validate_positive_number(value, name):
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be a number") from exc

    if number <= 0:
        raise ValueError(f"{name} must be positive")

    return number


