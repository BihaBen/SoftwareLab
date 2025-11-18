from difflib import SequenceMatcher
from typing import List, Dict, Set, Tuple
from collections import defaultdict


# A függvény kigyűjti az összes különböző attribútumnevet (változónevet) egy szabályhalmazból.
# A bemenet egy szabálylista (rules), ahol minden szabály tartalmazhat "conditions" és "action" mezőt.
# A kimenet egy halmaz (set), amely minden egyedi attribútumot tartalmaz.
def extract_attributes(rules: List[Dict]) -> Set[str]:
    attributes = set()
    for rule in rules:
        for cond in rule.get("conditions", []):
            attributes.add(cond["attribute"])
        if "action" in rule:
            attributes.add(rule["action"]["attribute"])
    return attributes


# A függvény két szöveget hasonlít össze, és megállapítja, hogy mennyire "hasonlítanak" egymásra.
# A hasonlóság mértékét a Levenshtein-alapú SequenceMatcher algoritmus számítja ki.
# A visszatérési érték True, ha az egyezés aránya eléri vagy meghaladja a megadott küszöbértéket (alapértelmezetten 0.8).
def similar_strings(a: str, b: str, threshold: float = 0.8) -> bool:
    return SequenceMatcher(None, a, b).ratio() >= threshold

def token_overlap(a: str, b: str) -> bool:
    set_a = set(a.lower().split("_"))
    set_b = set(b.lower().split("_"))
    return len(set_a & set_b) > 0


# A függvény azt vizsgálja, hogy két változónév (sztring) között van-e közös rész (token),
# ha "_" karakter mentén feldaraboljuk őket. A cél az, hogy kiderüljön:
# például a "total_price" és a "price_eur" változókban szerepel-e közös jelentéstartalom ("price").
def detect_similar_attributes(attributes: Set[str]) -> List[Tuple[str, str, str]]:
    attributes = list(attributes)
    pairs = []
    for i in range(len(attributes)):
        for j in range(i + 1, len(attributes)):
            a, b = attributes[i], attributes[j]
            if similar_strings(a, b) or token_overlap(a, b):
                pairs.append((a, b, "similar name or token overlap"))
    return pairs

# A függvény egy változónév-párok listájából (pl. hasonló vagy azonos jelentésű változók) csoportokat képez.
# Cél: azonos vagy hasonló jelentésű változók csoportosítása – pl. ["price", "total_price", "price_eur"].
def suggest_alias_groups(pairs: List[Tuple[str, str, str]]) -> List[Dict[str, any]]:
    alias_groups = defaultdict(set)
    for a, b, _ in pairs:
        alias_groups[a].add(a)
        alias_groups[a].add(b)
    result = []
    seen = set()
    for key, group in alias_groups.items():
        frozen = frozenset(group)
        if frozen not in seen:
            seen.add(frozen)
            result.append({ "suggested_group": list(group) })
    return result

# MEGHÍVÁSA
def find_similar_variable_names(rules: List[Dict], label: str = ""):
    print(f"\n🔍 Változónév-összehasonlítás: {label}")
    attrs = extract_attributes(rules)
    similar_pairs = detect_similar_attributes(attrs)
    alias_groups = suggest_alias_groups(similar_pairs)

    if alias_groups:
        print("Lehetséges azonos jelentésű változók:")
        for group in alias_groups:
            print(f"→ {group['suggested_group']}")
    else:
        print("Nem találtunk hasonló változóneveket.")

