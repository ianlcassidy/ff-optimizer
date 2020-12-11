def is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def what_week_is_it() -> int:
    week = input("What NFL week number is it? ")
    try:
        week = int(week)
    except ValueError:
        raise Exception("NFL week number must be an integer")
    return week
