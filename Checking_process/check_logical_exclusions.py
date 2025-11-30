"""
check_logical_exclusions.py

Cél:
- Logikai / matematikai ellentmondások keresése:
  1) Egyetlen szabályon belül: ugyanarra a változóra olyan feltételek
     vannak, amelyek együtt nem teljesülhetnek (üres intervallum).
  2) Két külön szabály: ugyanarra a kimeneti változóra (effect.variable)
     eltérő értéket adnak átfedő feltételhalmaz mellett.

Heurisztika:
- Csak numerikus összehasonlító operátorokat (<, <=, >, >=, ==) kezelünk.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple, Optional
from math import inf


Numeric = float | int


def _build_intervals(causes: List[Dict[str, Any]]) -> Dict[str, Tuple[Numeric, bool, Numeric, bool]]:
    """
    Egy szabály Causes listájából intervallumot épít az egyes változókra:
        var -> (lower, lower_inclusive, upper, upper_inclusive)
    """
    intervals: Dict[str, Tuple[Numeric, bool, Numeric, bool]] = {}

    for c in causes:
        var = c.get("variable")
        op = c.get("operator")
        val = c.get("value")

        if var is None or op is None:
            continue
        if not isinstance(val, (int, float)):
            # csak numerikus értékekkel tudunk dolgozni
            continue

        current = intervals.get(var, (-inf, False, inf, False))
        lo, lo_inc, hi, hi_inc = current

        if op == ">":
            if val > lo or (val == lo and lo_inc):
                lo, lo_inc = val, False
        elif op == ">=":
            if val > lo or (val == lo and not lo_inc):
                lo, lo_inc = val, True
        elif op == "<":
            if val < hi or (val == hi and hi_inc):
                hi, hi_inc = val, False
        elif op == "<=":
            if val < hi or (val == hi and not hi_inc):
                hi, hi_inc = val, True
        elif op == "==":
            # pontos érték – szűkítjük mindkét oldalról
            lo, lo_inc = val, True
            hi, hi_inc = val, True

        intervals[var] = (lo, lo_inc, hi, hi_inc)

    return intervals


def _interval_empty(interval: Tuple[Numeric, bool, Numeric, bool]) -> bool:
    lo, lo_inc, hi, hi_inc = interval
    if lo > hi:
        return True
    if lo == hi and (not lo_inc or not hi_inc):
        return True
    return False


def _intervals_overlap(
    i1: Tuple[Numeric, bool, Numeric, bool],
    i2: Tuple[Numeric, bool, Numeric, bool],
) -> bool:
    lo1, lo1_inc, hi1, hi1_inc = i1
    lo2, lo2_inc, hi2, hi2_inc = i2

    # alsó határ maximuma
    if lo1 > lo2:
        lo = lo1
        lo_inc = lo1_inc
    elif lo2 > lo1:
        lo = lo2
        lo_inc = lo2_inc
    else:
        lo = lo1
        lo_inc = lo1_inc and lo2_inc

    # felső határ minimuma
    if hi1 < hi2:
        hi = hi1
        hi_inc = hi1_inc
    elif hi2 < hi1:
        hi = hi2
        hi_inc = hi2_inc
    else:
        hi = hi1
        hi_inc = hi1_inc and hi2_inc

    if lo < hi:
        return True
    if lo == hi and lo_inc and hi_inc:
        return True
    return False


def _iter_rules_with_effects(data: Dict[str, Any]):
    """
    Visszaadja az összes (rule, effect) párost, ahol effect.operator "=".
    Csak azokat nézzük, amelyeknek van Causes listájuk is.
    """
    for rule in data.get("inputs", []):
        causes = rule.get("Causes", [])
        for eff in rule.get("effects", []):
            if eff.get("operator") == "=":
                yield rule, causes, eff

    for rule in data.get("outputs", []):
        causes = rule.get("Causes", [])
        # új struktúra: "rules"
        for eff in rule.get("rules", []):
            if eff.get("operator") == "=":
                yield rule, causes, eff
        # kompatibilitás kedvéért:
        for eff in rule.get("effects", []):
            if eff.get("operator") == "=":
                yield rule, causes, eff


def check(requirements_data: Dict[str, Any]) -> List[str]:
    """
    Kétféle problémát keres:
      - önellentmondó feltétel egy szabályon belül,
      - két szabály, amely ugyanarra a változóra eltérő értéket adhat
        átfedő feltételek mellett.

    Visszatér:
        list[str] – figyelmeztetések.
    """
    messages: List[str] = []

    # 1) önellentmondó feltételek
    for rule in requirements_data.get("inputs", []):
        rid = rule.get("id", "<no-id>")
        intervals = _build_intervals(rule.get("Causes", []))
        for var, iv in intervals.items():
            if _interval_empty(iv):
                messages.append(
                    f"Szabály {rid}: a(z) '{var}' változóra vonatkozó feltételek "
                    f"ellentmondásos intervallumot adnak (üres metszet)."
                )

    # 2) szabály-párok közti konfliktusok
    records = []
    for rule, causes, eff in _iter_rules_with_effects(requirements_data):
        rid = rule.get("id", "<no-id>")
        eff_var = eff.get("variable")
        eff_val = eff.get("value")
        if eff_var is None:
            continue
        records.append(
            {
                "id": rid,
                "effect_var": eff_var,
                "effect_val": eff_val,
                "intervals": _build_intervals(causes),
            }
        )

    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            r1 = records[i]
            r2 = records[j]
            if r1["effect_var"] != r2["effect_var"]:
                continue
            if r1["effect_val"] == r2["effect_val"]:
                # ugyanazt az értéket adják – nem ellentmondás, max. redundáns
                continue

            iv1 = r1["intervals"]
            iv2 = r2["intervals"]

            shared_vars = set(iv1.keys()) & set(iv2.keys())

            conflict_possible = False
            if not shared_vars:
                # nincs közös numerikus feltétel – potenciálisan egyszerre is igazak lehetnek
                conflict_possible = True
            else:
                # minden közös változóra legyen átfedés az intervallumok között
                conflict_possible = True
                for v in shared_vars:
                    if not _intervals_overlap(iv1[v], iv2[v]):
                        conflict_possible = False
                        break

            if conflict_possible:
                messages.append(
                    f"Szabály {r1['id']} és {r2['id']} ugyanarra a '{r1['effect_var']}' "
                    f"változóra eltérő értéket adnak ({r1['effect_val']} vs {r2['effect_val']}) "
                    f"átfedő feltételek mellett."
                )

    return messages
