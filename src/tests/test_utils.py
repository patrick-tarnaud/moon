import datetime

import utils.utils as utils


def test_convert_date_to_datetime():
    date = datetime.date.fromisoformat('2021-05-15')
    res = utils.convert_date_to_datetime(date, "14:00:15")
    assert res.strftime("%Y-%m-%d %H:%M:%S") == "2021-05-15 14:00:15"