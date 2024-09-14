def to_snake(string):
    return string.strip().replace(" ", "_").replace("-", "_").lower()


def to_percentage(num, total, dec=2):
    return round((num / total) * 100, dec)


def to_percentages(num, total, dec=2):
    return {name: to_percentage(n, total, dec) for name, n in num.items()}
