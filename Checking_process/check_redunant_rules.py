"""
check_redundant_rules.py

Cél:
- Olyan szabályokat találni, amelyek pontosan ugyanazokat a feltételeket
  és pontosan ugyanazokat a hatásokat tartalmazzák, azaz duplikált /
  redundáns szabályok.

Heurisztika:
- Minden szabályhoz (inputs + outputs) készül egy 'signature'
  (rendezett Causes + rendezett effects/rules).
- Ha ugyanaz a signature több szabályhoz tartozik, az ismétlés.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _normalize_condition(cond: Dict[str, Any]) -> Tuple[str, str, str]:
    return (
        str(cond.get("variable")),
        str(cond.get("operator")),
        str(cond.get("value")),
    )


def _normalize_effect(eff: Dict[str, Any]) -> Tuple[str, str, str]:
    # 'value' vagy 'expression', esetleg más – mindent stringgé alakítunk
    val = eff.get("value")
    if val is None and "expression" in eff:
        val = eff.get("expression")
    return (
        str(eff.get("variable")),
        str(eff.get("operator")),
        str(val),
    )


def _iter_all_rules(data: Dict[str, Any]):
    """
    Visszaadja az összes szabályobjektumot, egységesített 'effects' listával.
    """
    for rule in data.get("inputs", []):
        effects = rule.get("effects", [])
        yield rule, rule.get("Causes", []), effects

    for rule in data.get("outputs", []):
        causes = rule.get("Causes", [])
        effects = []
        if "rules" in rule:
            effects.extend(rule.get("rules", []))
        if "effects" in rule:
            effects.extend(rule.get("effects", []))
        yield rule, causes, effects


def check(requirements_data: Dict[str, Any]) -> List[str]:
    """
    Redundáns (duplikált) szabályok keresése.

    Visszatér:
        list[str] – figyelmeztetések.
    """
    signature_map: Dict[Tuple, str] = {}
    redundant_ids: List[str] = []

    for rule, causes, effects in _iter_all_rules(requirements_data):
        rid = rule.get("id", "<no-id>")

        conds_sig = tuple(sorted(_normalize_condition(c) for c in causes))
        effs_sig = tuple(sorted(_normalize_effect(e) for e in effects))
        signature = (conds_sig, effs_sig)

        if signature in signature_map:
            first_id = signature_map[signature]
            redundant_ids.append((rid, first_id))
        else:
            signature_map[signature] = rid

    messages: List[str] = []
    for rid, first_id in redundant_ids:
        messages.append(
            f"Szabály {rid} redundáns: logikailag megegyezik a(z) {first_id} szabállyal."
        )

    return messages
