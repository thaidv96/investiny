from datetime import datetime, timedelta
from typing import Any, Dict, Literal, Union

from investiny.config import Config
from investiny.info import investing_info
from investiny.utils import calculate_date_intervals, request_to_investing


def historical_data(
    investing_id: int,
    from_date: Union[str, None] = None,
    to_date: Union[str, None] = None,
    interval: Literal[1, 5, 15, 30, 60, 300, "D", "W", "M"] = "D",
    splash_server_url: str = None,
) -> Dict[str, Any]:
    """Get historical data from Investing.com.

    Args:
        investing_id: Investing.com's ID for the asset.
        from_date: Initial date to retrieve historical data (formatted as m/d/Y). Defaults to None.
        to_date:
            Final date to retrieve historical data (formatted as m/d/Y). Defaults to None,
            unless `from_date` is specified, that defaults to current date.
        interval: Interval between each historical data point. Defaults to "D".

    Note:
        If no dates are introduced, the function will retrieve the last 30 days of historical data.

    Returns:
        A dictionary with the historical data from Investing.com.
    """
    from_datetimes, to_datetimes = calculate_date_intervals(
        from_date=from_date, to_date=to_date, interval=interval
    )

    result: Dict[str, Any] = {
        "date": [],
        "open": [],
        "high": [],
        "low": [],
        "close": [],
        "volume": [],
    }

    datetime_format = (
        Config.time_format if interval not in ["D", "W", "M"] else Config.date_format
    )

    info = investing_info(
        investing_id=investing_id, splash_server_url=splash_server_url
    )

    has_volume = not info["has_no_volume"]
    days_shift = 1 if info["type"] in ["Yield"] else 0

    for to_datetime, from_datetime in zip(to_datetimes, from_datetimes):
        params = {
            "symbol": investing_id,
            "from": int(from_datetime.timestamp()),
            "to": int(to_datetime.timestamp()),
            "resolution": interval,
        }
        data = request_to_investing(
            endpoint="history", params=params, splash_server_url=splash_server_url
        )
        result["date"] += [
            (datetime.fromtimestamp(t) - timedelta(days=days_shift)).strftime(
                datetime_format
            )
            for t in data["t"]  # type: ignore
        ]
        result["open"] += data["o"]  # type: ignore
        result["high"] += data["h"]  # type: ignore
        result["low"] += data["l"]  # type: ignore
        result["close"] += data["c"]  # type: ignore
        if has_volume:
            result["volume"] += data["v"]  # type: ignore
    if len(result["volume"]) < 1:
        result.pop("volume")
    return result
