import os
import re
from datetime import date, datetime

import pytz
from requests import Session, HTTPError
import pandas as pd
import bs4 as bs

from umap.models import Result, Log


def get_soup(_url):
    try:
        session = Session()
        html = session.get(_url)
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


def fore_end(_date):
    year = _date.year
    month = _date.month
    return date(year, month, 1)


def str_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def round_3(_value):
    return round(_value, 3) if _value is not None else 0


def pd_result(columns, result_flg):
    if "key" not in columns:
        columns.append("key")

    results = Result.objects.filter(race__result_flg=result_flg).exclude(rank=0).exclude(odds=0).exclude(race__type="障害").values(*columns)
    df = pd.DataFrame.from_records(results)

    # Formalization
    df = df.rename(columns={"race__max_prize": "max_prize",
                            "race__weather": "weather",
                            "race__condition": "condition",
                            "race__head_count": "head_count",
                            "race__odds_stdev": "odds_stdev",
                            "race__length": "length",
                            "race__race_id": "race_id",
                            "race__race_dt": "race_dt"
                            })
    df = df.set_index("key")
    return df


def set_log(_label):
    _pid = os.getpid()
    _now = datetime.now(pytz.timezone('Asia/Tokyo'))

    # Update exec_time to previous record
    try:
        q = Log.objects.get(pid=_pid, finish=False)
        q.exec_time = _now - q.start_time
        q.finish = True
        q.save()
    except Log.DoesNotExist:
        pass

    # Set record
    Log(start_time=_now, pid=_pid, label=_label).save()

    return


def end_log():
    _pid = os.getpid()
    _now = datetime.now(pytz.timezone('Asia/Tokyo'))

    try:
        q = Log.objects.get(pid=_pid, finish=False)
        q.exec_time = _now - q.start_time
        q.finish = True
        q.save()
    except Log.DoesNotExist:
        pass

    return
