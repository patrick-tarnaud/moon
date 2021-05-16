import datetime


def convert_date_to_datetime(date: datetime.date, hhmmss: str) -> datetime:
    """
    Convert a datetime to a date with hhmmss supplied
    Ex : date=2021-05-15 with hhmmss='02:00:00' will return 2021-05-15 02:00:00

    :param date: the date to convert
    :param hhmmss: the hours:minutes:secondes for the time
    :return: the datetime computed
    """
    return datetime.datetime.strptime(str(date) + f' {hhmmss}', "%Y-%m-%d %H:%M:%S")
