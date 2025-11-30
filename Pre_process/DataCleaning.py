"""
Pre_process/DataCleaning.py

Általános célú "DataCleaning", ami folyószöveges követelményekből
(R1, R2, R2-1, stb.) megpróbál JSON struktúrát építeni:

{
  "variables": [...],
  "inputs":  [...],
  "outputs": [...]
}

FIGYELEM:
- A feldolgozás erősen heurisztikus.
- A kimenet jó kiindulási alap, de gyakran manuális finomhangolást igényel.
"""

from __future__ import annotations

import json
import os
import re
from typing import Dict, Any, List, Tuple, Optional

from Dictionaries.operator_words import OPERATOR_WORDS


# -------------------- Szám-szó → szám -------------------- #

WORD_NUMBERS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def normalize_number_words(text: str) -> str:
    """
    Az angol szám-szavakat arab számokra cseréli (pl. five -> 5).
    Nem változtatja meg a szöveg egyéb részeit.
    """

    def repl(match: re.Match) -> str:
        return str(WORD_NUMBERS[match.group(0)])

    pattern = r"\b(" + "|".join(WORD_NUMBERS.keys()) + r")\b"
    return re.sub(pattern, repl, text.lower())


# -------------------- Segéd: snake_case változónév -------------------- #

STOPWORDS = {
    "the", "a", "an", "of", "to", "for", "with", "from", "on", "in",
    "customer", "employees", "employee", "any", "every", "each",
    "new", "books", "book", "second", "hand", "goods", "total",
    "price", "sum", "points", "age", "years", "year", "service",
    "if", "when", "whenever", "provided", "that", "at", "least",
    "most", "more", "less", "output", "result", "final",
}


def to_snake_case(text: str) -> str:
    text = re.sub(r"[^0-9a-zA-Z]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text.lower() or "var"


def guess_variable_name(pre_chunk: str) -> str:
    """
    Heurisztikusan változónevet próbál kitalálni az operátor előtti rész alapján.
    Pl. "the price of the goods" -> "price_goods"
    """
    tokens = re.findall(r"[a-zA-Z]+", pre_chunk.lower())
    filtered = [t for t in tokens if t not in STOPWORDS]
    if not filtered:
        return "var"

    # Utolsó 1-2 "értelmes" szót használjuk
    if len(filtered) >= 2:
        candidate = filtered[-2] + "_" + filtered[-1]
    else:
        candidate = filtered[-1]
    return to_snake_case(candidate)


# -------------------- Operátor + szám keresése -------------------- #

def find_comparison(text: str,
                    pick: str = "first") -> Tuple[Optional[str], Optional[float], Optional[str]]:
    """
    OPERATOR_WORDS alapján megpróbál operátort + számértéket találni.
    Visszatér: (operator, value, phrase), pl. (\">=\", 200, \"reaches\").
    """
    t = normalize_number_words(text)

    best_phrase = None
    best_operator = None
    for phrase, meta in sorted(OPERATOR_WORDS.items(), key=lambda kv: -len(kv[0])):
        if meta["type"] == "comparison" and phrase in t:
            best_phrase = phrase
            best_operator = meta["operator"]
            break

    numbers = re.findall(r"(\d+(?:\.\d+)?)", t)
    if not numbers:
        return best_operator, None, best_phrase

    num_str = numbers[-1] if pick == "last" else numbers[0]
    val = float(num_str)
    if val.is_integer():
        val = int(val)

    return best_operator, val, best_phrase


# -------------------- R-szabályok kinyerése -------------------- #

def extract_rules(text: str) -> Dict[str, str]:
    """
    A szövegből kinyeri az R1, R2, R2-1, ... szabályokat.
    Elvárás: sor elején 'R1 ', 'R2 ' stb.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # R1, R2, R2-1, R10 stb.
    pattern = r"(R\d+(?:-\d+)?)\s+(.*?)(?=\nR\d+(?:-\d+)?\s+|\Z)"
    matches = re.findall(pattern, text, flags=re.S)

    rules: Dict[str, str] = {}
    for rule_id, desc in matches:
        normalized = " ".join(desc.strip().split())
        rules[rule_id] = normalized
    return rules


# -------------------- IF / THEN szétválasztás -------------------- #

IF_WORDS = [w for w, meta in OPERATOR_WORDS.items() if meta["type"] == "logical" and meta["operator"] == "IF"]
THEN_WORDS = [w for w, meta in OPERATOR_WORDS.items() if meta["type"] == "logical" and meta["operator"] == "THEN"]


def split_condition_action(desc: str) -> Tuple[str, str]:
    """
    Heurisztikusan szétválasztja egy szabály leírását condition / action részekre.
    Két alapminta:
      1) IF ... THEN ...   (if a > b, then X)
      2) X ... IF ...      (X is true if a > b)
    Visszaad: (condition_text, action_text) – bármelyik lehet "" (ha nem talál mintát).
    """
    lower = desc.lower()

    found_if = None
    for w in sorted(IF_WORDS, key=len, reverse=True):
        idx = lower.find(w)
        if idx != -1:
            found_if = (w, idx)
            break

    if not found_if:
        # Nincs IF – teljes leírást "action"-nek tekintjük
        return "", desc

    if_word, if_idx = found_if
    if_end = if_idx + len(if_word)

    # Nézzük, van-e THEN szó
    found_then = None
    for w in sorted(THEN_WORDS, key=len, reverse=True):
        idx = lower.find(w, if_end)
        if idx != -1:
            found_then = (w, idx)
            break

    # Ha az IF a mondat elején van → IF ... THEN ... minta
    if if_idx < len(desc) * 0.3:
        if found_then:
            then_word, then_idx = found_then
            cond = desc[if_end:then_idx].strip(" ,.")
            action = desc[then_idx + len(then_word):].strip(" ,.")
        else:
            cond = desc[if_end:].strip(" ,.")
            action = ""
    else:
        # X ... IF ...  minta – a bal oldal az action, jobb a condition
        action = desc[:if_idx].strip(" ,.")
        cond = desc[if_end:].strip(" ,.")

    return cond, action


# -------------------- Condition / effect parszolás -------------------- #

def parse_conditions(condition_text: str) -> List[Dict[str, Any]]:
    """
    A condition_text-et logikai 'and' mentén darabolja, majd minden darabra
    megpróbál (variable, operator, value) hármast kinyerni.
    """
    if not condition_text:
        return []

    # Egyszerű "and" bontás
    parts = re.split(r"\band\b", condition_text, flags=re.I)
    results: List[Dict[str, Any]] = []

    for part in parts:
        part = part.strip(" ,.")
        if not part:
            continue

        op, val, phrase = find_comparison(part)
        if op is None:
            # Nincs összehasonlító operátor – kihagyjuk vagy placeholder
            continue

        # Operátor előtti rész a változójelölt
        if phrase:
            idx = normalize_number_words(part.lower()).find(phrase)
            pre = part[:idx]
        else:
            pre = part
        var_name = guess_variable_name(pre)

        results.append(
            {
                "variable": var_name,
                "operator": op,
                "value": val,
                "raw": part,
            }
        )

    return results


def parse_effects(action_text: str, rule_id: str) -> List[Dict[str, Any]]:
    """
    Nagyon általános, óvatos heurisztika:

    - Megpróbál értéket kinyerni (számot) az action_text-ből.
    - Ha nincs elég info, egy 'rule_<id>_effect' placeholder változót használ.

    A cél itt inkább a struktúra kitöltése, semmint a tökéletes szemantika.
    """
    action_text = action_text.strip()
    if not action_text:
        return []

    # Próbáljunk számot keresni (pl. 10% discount)
    numbers = re.findall(r"(\d+(?:\.\d+)?)", normalize_number_words(action_text))
    value: Any
    if numbers:
        num = float(numbers[0])
        if num.is_integer():
            num = int(num)
        # Ha %-t látunk, tegyük aránnyá
        if "%" in action_text:
            value = num / 100.0
        else:
            value = num
    else:
        value = action_text  # fallback: teljes szöveg

    # Változónév becslése: próbáljunk egy kulcsszót keresni
    keyword_candidates = [
        "price", "cost", "discount", "reduction", "weight",
        "grade", "result", "output", "days", "vacation",
        "delivery", "fee", "label", "category",
    ]
    lower = action_text.lower()
    var_name = None
    for kw in keyword_candidates:
        if kw in lower:
            var_name = to_snake_case(kw)
            break

    if var_name is None:
        var_name = f"rule_{rule_id.lower()}_effect"

    return [
        {
            "variable": var_name,
            "operator": "=",
            "value": value,
            "raw": action_text,
        }
    ]


# -------------------- Szabályok JSON struktúrává alakítása -------------------- #

def build_rules_structure(rules: Dict[str, str]) -> Dict[str, Any]:
    """
    A kinyert R-szabályokat (id -> szöveg) JSON struktúrává alakítja:
    - inputs: IF-es szabályok
    - outputs: olyan szabályok, amik 'output', 'result' stb. szót tartalmaznak
    """
    inputs: List[Dict[str, Any]] = []
    outputs: List[Dict[str, Any]] = []

    for rule_id, desc in rules.items():
        lower = desc.lower()
        is_output = any(w in lower for w in ["output", "result", "display"])

        cond_text, action_text = split_condition_action(desc)
        causes = parse_conditions(cond_text)

        if is_output:
            # Output típus – question + rules
            question_var = None
            for kw in ["price to be paid", "result", "output", "grade", "vacation days"]:
                if kw in lower:
                    question_var = to_snake_case(kw)
                    break
            if question_var is None:
                question_var = "result_value"

            question = [
                {
                    "variable": question_var,
                    "operator": "=",
                    "value": "?",
                }
            ]

            rules_list = []
            # az action_text-ből próbálunk effects-szerű szabályt építeni
            effects_like = parse_effects(action_text or desc, rule_id)
            for eff in effects_like:
                rules_list.append(
                    {
                        "variable": eff["variable"],
                        "operator": eff["operator"],
                        "value": eff["value"],
                        "raw": eff["raw"],
                    }
                )

            outputs.append(
                {
                    "id": rule_id,
                    "description": desc,
                    "question": question,
                    "rules": rules_list,
                }
            )
        else:
            effects = parse_effects(action_text or desc, rule_id)
            inputs.append(
                {
                    "id": rule_id,
                    "description": desc,
                    "Causes": causes,
                    "effects": effects,
                }
            )

    return {
        "inputs": inputs,
        "outputs": outputs,
    }


# -------------------- Változók kinyerése -------------------- #

def infer_variables(struct: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    A inputs/outputs részekből kinyeri a változóneveket és
    heurisztikusan típus/role értéket rendel hozzájuk.
    """
    vars_set = set()

    for rule in struct.get("inputs", []):
        for c in rule.get("Causes", []):
            vars_set.add((c["variable"], "input"))
        for e in rule.get("effects", []):
            vars_set.add((e["variable"], "eternal-truth"))

    for rule in struct.get("outputs", []):
        for q in rule.get("question", []):
            vars_set.add((q["variable"], "output"))
        for r in rule.get("rules", []):
            vars_set.add((r["variable"], "eternal-truth"))

    # Ha ugyanarra a névre több szerepkör is jön, preferálunk:
    # output > input > eternal-truth
    role_priority = {"output": 3, "input": 2, "eternal-truth": 1}
    best_role: Dict[str, str] = {}

    for name, role in vars_set:
        if name not in best_role or role_priority[role] > role_priority[best_role[name]]:
            best_role[name] = role

    variables: List[Dict[str, Any]] = []
    for name, role in best_role.items():
        var_type = "decimal"  # default
        if name.startswith("is_") or name.endswith("_flag"):
            var_type = "boolean"

        variables.append(
            {
                "name": name,
                "type": var_type,
                "role": role,
            }
        )

    return variables


# -------------------- Fő építőfüggvények -------------------- #

def text_to_requirements(text: str) -> Dict[str, Any]:
    """
    Nyers követelményszöveg → JSON struktúra (dict).
    """
    rules = extract_rules(text)
    struct = build_rules_structure(rules)
    variables = infer_variables(struct)

    struct["variables"] = variables
    return struct


def build_requirements_json(
    text_path: str,
    json_output_path: str = "requirements.json",
) -> Dict[str, Any]:
    """
    Beolvassa a folyószöveges követelményeket egy .txt fájlból,
    JSON struktúrát épít belőle, és kiírja requirements.json néven.
    """
    if not os.path.exists(text_path):
        raise FileNotFoundError(f"A megadott szövegfájl nem található: {text_path}")

    with open(text_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    data = text_to_requirements(raw_text)

    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data


def load_json_requirements(
    json_path: str = "requirements.json",
    text_path: str | None = None,
) -> Dict[str, Any]:
    """
    Betölti a requirements.json-t.
    Ha még nem létezik, de van text_path, akkor abból legenerálja.
    """
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    if text_path is None:
        raise FileNotFoundError(
            f"A(z) '{json_path}' nem található, és text_path sincs megadva."
        )

    return build_requirements_json(text_path, json_output_path=json_path)


if __name__ == "__main__":
    # Példa: feltételezzük, hogy az Examples mappában van egy .txt
    example_txt = os.path.join("Examples", "price_calculation_example.txt")
    data = build_requirements_json(example_txt)
    print("requirements.json legenerálva.")
