import re

from requests import Session, HTTPError
import bs4 as bs

from umap.models import Race


def get_soup(url):
    try:
        session = Session()
        html = session.get(url)
        html.encoding = html.apparent_encoding
        soup = bs.BeautifulSoup(html.content, "html.parser", from_encoding=html.apparent_encoding)
    except HTTPError as e:
        print("HTTP error: {0}".format(e))
        raise
    return soup


def formatter(reg, target, type="char"):
    # Extract target variables
    fmt = re.compile(reg)
    val = fmt.findall(target)[0] if target is not None and fmt.search(target) else None

    # Redact comma from numerical values
    if type == "int" or type == "float":
        if val is None:
            val = 0
        else:
            val = re.sub(",", "", val)


    # Convert type
    if type == "int":
        value = int(val) if val is not None else 0
    elif type == "float":
        value = float(val) if val is not None else 0
    elif type == "char":
        value = str(val) if val is not None else ""
    else:
        value = None

    return value


def get_from_a(data, target="url"):
    if target == "url":
        value = data.a.get("href") if data.a is not None else None
    else:
        value = data.a.string if data.a is not None else None

    return value

