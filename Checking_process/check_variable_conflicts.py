"""
check_variable_conflicts.py

Cél:
- Olyan változókat keresni, amelyek ugyanazzal a formulával
  kerülnek kiszámításra (duplikált / szinonima változók).

Heurisztika:
- Minden effect/rule, ahol operator "=" és a value string (képlet),
  normalizált formulaként kerül csoportosításra.
- Ha ugyanazt a normalizált formulát több különböző változónévhez
  használják, azt potenciális ütközésként jelentjük.
"""

from __future__ import annotations

from typing import Any, Dict, List


def _normalize_expression(expr: str) -> str:
    """
    Egyszerű normalizálás:
    - szóközök elhagyása
    - ha van benne '+', akkor a tagokat rendezzük (a+b == b+a)
    """
    expr = expr.replace(" ", "")
    if "+" in expr:
        parts = expr.split("+")
        parts = sorted(parts)
        expr = "+".join(parts)
    return expr


def _iter_all_effect_like_entries(data: Dict[str, Any]):
    """
    Bejárja az összes szabály "hatás" részét:
    - inputs[*].effects
    - outputs[*].rules (ha létezik)
    - outputs[*].effects (ha régebbi struktúra)
    """
    for rule in data.get("inputs", []):
        for eff in rule.get("effects", []):
            yield rule, eff

    for rule in data.get("outputs", []):
        # új struktúra: question + rules
        for eff in rule.get("rules", []):
            yield rule, eff
        # kompatibilitás kedvéért: ha esetleg effects kulcs maradt
        for eff in rule.get("effects", []):
            yield rule, eff


def check(requirements_data: Dict[str, Any]) -> List[str]:
    """
    Keres duplikált formulákat eltérő változóneveken.

    Visszatér:
        list[str] – emberi olvasásra alkalmas figyelmeztetések.
    """
    formula_map: Dict[str, List[str]] = {}

    for rule, eff in _iter_all_effect_like_entries(requirements_data):
        var = eff.get("variable")
        op = eff.get("operator")
        val = eff.get("value")
        if var is None or op != "=":
            continue

        if not isinstance(val, str):
            # tipikusan szám, ilyenkor nem nagyon tudunk mit normalizálni
            continue

        sig = _normalize_expression(val)
        formula_map.setdefault(sig, []).append(var)

    messages: List[str] = []

    for sig, vars_used in formula_map.items():
        unique_vars = sorted(set(vars_used))
        if len(unique_vars) > 1:
            messages.append(
                f"Az alábbi változók ugyanazzal a formulával számítódnak: "
                f"{', '.join(unique_vars)}  (formula: '{sig}')"
            )

    return messages
