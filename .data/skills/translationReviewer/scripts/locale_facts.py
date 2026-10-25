#!/usr/bin/env python3
"""
Print CLDR locale facts (numbers, dates, plurals, lists) for translation review.

Usage:
    python3 locale_facts.py                       # default 15-language set + regional variants
    python3 locale_facts.py de_CH fr_BE ar_EG     # specific locales
    python3 locale_facts.py --markdown > table.md # Markdown tables

Needs Babel (`pip install babel`), which bundles CLDR. Facts come from CLDR, not memory,
so use this instead of guessing a separator or date order.
"""

import argparse
import sys
from datetime import date, datetime, time

try:
    from babel import Locale
    from babel.dates import format_date, format_time
    from babel.numbers import format_currency, format_decimal, format_percent
    from babel.plural import to_gettext
except ImportError:
    sys.exit("Babel is required: pip install babel")

DEFAULT = [
    "en_GB", "en_US", "de_DE", "de_AT", "de_CH", "it_IT", "it_CH", "nl_NL", "nl_BE",
    "fr_FR", "fr_BE", "fr_CH", "pt_PT", "es_ES", "fi_FI", "cs_CZ", "nb_NO", "sv_SE",
    "da_DK", "el_GR", "pl_PL", "ar", "ar_AE", "ar_SA", "ar_EG",
]
SAMPLE_NUMBER = 1234567.891
SAMPLE_DATE = date(2026, 3, 7)
SAMPLE_TIME = time(14, 5)
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _list(loc) -> str:
    try:
        from babel.lists import format_list

        return format_list(["A", "B", "C"], locale=loc)
    except Exception:  # noqa: BLE001 - older Babel without list data
        return ""


def facts(code: str) -> dict:
    loc = Locale.parse(code)
    syms = loc.number_symbols.get(loc.default_numbering_system) or loc.number_symbols.get("latn", {})
    plural = to_gettext(loc.plural_form)
    local_currency = None
    if loc.territory:
        from babel.numbers import get_territory_currencies

        cur = get_territory_currencies(loc.territory, SAMPLE_DATE)
        local_currency = cur[0] if cur else None
    return {
        "locale": code,
        "digits": loc.default_numbering_system,
        "decimal": syms.get("decimal"),
        "group": syms.get("group"),
        "number": format_decimal(SAMPLE_NUMBER, locale=code, numbering_system="default"),
        "percent": format_percent(0.25, locale=code, numbering_system="default"),
        "currency": format_currency(1234.5, local_currency or "EUR", locale=code, numbering_system="default"),
        "date_short": format_date(SAMPLE_DATE, "short", locale=code),
        "date_medium": format_date(SAMPLE_DATE, "medium", locale=code),
        "date_long": format_date(SAMPLE_DATE, "long", locale=code),
        "time_short": format_time(SAMPLE_TIME, "short", locale=code),
        "first_day": WEEKDAYS[loc.first_week_day],
        "plurals": ", ".join(sorted(loc.plural_form.rules) + ["other"]),
        "gettext": plural.replace("Plural-Forms: ", "").strip(),
        "list": _list(loc),
        "rtl": loc.text_direction == "rtl",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("locales", nargs="*", default=DEFAULT)
    p.add_argument("--markdown", action="store_true")
    a = p.parse_args()
    rows = [facts(c) for c in a.locales]
    if not a.markdown:
        for r in rows:
            print(r["locale"])
            for k, v in r.items():
                if k != "locale":
                    print(f"  {k:12} {v}")
        return
    print("| Locale | Decimal | Group | 1234567.891 | 25% | Currency | Short date | Medium date | Time | Week starts |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        grp = {" ": "NBSP", " ": "NNBSP", "’": "’ (U+2019)", "'": "'", " ": "space"}.get(r["group"], r["group"])
        print(f"| `{r['locale']}` | `{r['decimal']}` | {grp} | `{r['number']}` | `{r['percent']}` | `{r['currency']}` | `{r['date_short']}` | `{r['date_medium']}` | `{r['time_short']}` | {r['first_day']} |")
    print()
    print("| Locale | CLDR plural categories | gettext Plural-Forms | List (A, B, C) | Digits | RTL |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        print(f"| `{r['locale']}` | {r['plurals']} | `{r['gettext']}` | {r['list']} | {r['digits']} | {'yes' if r['rtl'] else ''} |")


if __name__ == "__main__":
    import signal

    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet exit when piped into head/less
    main()
