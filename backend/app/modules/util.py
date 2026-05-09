import datetime

def get_date(days_forwarded: int):
    """
    creates the date for URL
    days_forwarded = how many days in the future
    =1 => tomorrow etc.
    """
    now = datetime.datetime.now()
    if days_forwarded:
        now = now + datetime.timedelta(days=days_forwarded)
    formatted_string = now.strftime("%Y-%m-%d")
    return formatted_string