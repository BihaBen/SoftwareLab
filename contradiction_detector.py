from typing import List, Dict, Any
from collections import defaultdict


# Ez a függvény azt vizsgálja, hogy két numerikus feltétel között van-e logikai ellentmondás.
# Például: "price >= 200" és "price < 150" nem lehet egyszerre igaz.
def has_numeric_conflict(op1, val1, op2, val2):
    if op1 == ">=" and op2 == "<":
        return val1 >= val2
    if op1 == "<" and op2 == ">=":
        return val2 >= val1
    if op1 == ">" and op2 == "<=":
        return val1 >= val2
    if op1 == "<=" and op2 == ">":
        return val2 >= val1
    if op1 == "==" and op2 == "!=" and val1 == val2:
        return True
    if op1 == "!=" and op2 == "==" and val1 == val2:
        return True
    if op1 == "==" and op2 == "==" and val1 != val2:
        return True
    return False


# Ez a függvény azt vizsgálja, hogy két logikai vagy szöveges feltétel ellentmond-e egymásnak.
# Például: "pay_with_card == true" ÉS "pay_with_card == false" — ez ellentmondás.
def has_logical_conflict(op1, val1, op2, val2):
    if op1 == "==" and op2 == "==" and val1 != val2:
        return True
    if op1 == "==" and op2 == "!=" and val1 == val2:
        return True
    if op1 == "!=" and op2 == "==" and val1 == val2:
        return True
    return False


# Ez a függvény végigmegy egy JSON-alapú szabálylistán, és kiszűri az egyazon szabályon belül található logikai vagy numerikus ellentmondásokat.
# Visszatér: egy lista az ellentmondásokról (melyik szabályban, melyik változóra vonatkozóan)
def detect_general_conflicts(rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    conflicts = []

    for rule in rules:
        rule_id = rule.get("rule_id", "UNKNOWN")
        conditions = rule.get("conditions", [])

        attr_conditions = defaultdict(list)
        for cond in conditions:
            attr = cond["attribute"]
            attr_conditions[attr].append((cond["operator"], cond["value"]))

        for attr, conds in attr_conditions.items():
            for i in range(len(conds)):
                for j in range(i + 1, len(conds)):
                    op1, val1 = conds[i]
                    op2, val2 = conds[j]

                    # Szám típusok
                    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                        if has_numeric_conflict(op1, val1, op2, val2):
                            conflicts.append({
                                "rule_id": rule_id,
                                "attribute": attr,
                                "conflict": f"{attr} {op1} {val1} <-> {attr} {op2} {val2}"
                            })
                    # Logikai vagy szöveges típusok
                    elif isinstance(val1, bool) and isinstance(val2, bool):
                        if has_logical_conflict(op1, val1, op2, val2):
                            conflicts.append({
                                "rule_id": rule_id,
                                "attribute": attr,
                                "conflict": f"{attr} {op1} {val1} <-> {attr} {op2} {val2}"
                            })
                    elif isinstance(val1, str) and isinstance(val2, str):
                        if has_logical_conflict(op1, val1, op2, val2):
                            conflicts.append({
                                "rule_id": rule_id,
                                "attribute": attr,
                                "conflict": f"{attr} {op1} '{val1}' <-> {attr} {op2} '{val2}'"
                            })

    return conflicts

# MEGHÍVÁSA
def check_and_report(rules: List[Dict[str, Any]], label: str = ""):
    print(f"\n Ellenőrzés: {label}")
    results = detect_general_conflicts(rules)
    if results:
        print("❗ Ellentmondások találhatók:")
        for r in results:
            print(f"- [{r['rule_id']}] {r['conflict']}")
    else:
        print("Nincs ellentmondás.")

