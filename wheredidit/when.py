"""Tiny date phrases: 'last week', 'yesterday', 'امبارح', 'الاسبوع اللي فات'. Returns (since_ts, until_ts, cleaned_query)."""
import re
import time

DAY = 86400
RULES = [
    (r"\b(today)\b|النهارده|انهارده|النهاردة", 0, 1),
    (r"\b(yesterday)\b|امبارح|إمبارح|أمس", 1, 1),
    (r"\blast week\b|\bthis week\b|الاسبوع اللي فات|الأسبوع اللي فات|الاسبوع الماضي|الأسبوع الماضي|الاسبوع ده|الأسبوع ده", 7, 7),
    (r"\blast month\b|الشهر اللي فات|الشهر الماضي", 31, 31),
    (r"\blast year\b|السنة اللي فاتت|العام الماضي", 366, 366),
]


def parse(query, now=None):
    now = now or time.time()
    for pat, days_back, span in RULES:
        m = re.search(pat, query, re.I)
        if m:
            start_day = now - (now % DAY)
            since = start_day - (days_back - 1) * DAY if days_back else start_day
            if days_back == 1 and span == 1:
                since, until = start_day - DAY, start_day
            else:
                until = now + DAY
            q = (query[: m.start()] + " " + query[m.end():]).strip()
            return since, until, q
    return None, None, query
