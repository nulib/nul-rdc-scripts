import datetime


def guess_date (string):
    for fmt in ["%m/%d/%Y","%d-%m-%Y", "%m/%d/%y", "%Y-%m-%d"]:
        try:
            return datetime.datetime.strptime(string, fmt).date()
        except ValueError:
            continue
    raise ValueError (string)