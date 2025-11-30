# Operátor szótár – minden kulcshoz hozzárendeljük a "jelentést"

OPERATOR_WORDS = {
    # Logikai / szerkezeti operátorok
    "if":                {"type": "logical", "operator": "IF"},
    "when":              {"type": "logical", "operator": "IF"},
    "whenever":          {"type": "logical", "operator": "IF"},
    "provided that":     {"type": "logical", "operator": "IF"},
    "assuming that":     {"type": "logical", "operator": "IF"},

    "then":              {"type": "logical", "operator": "THEN"},
    "in that case":      {"type": "logical", "operator": "THEN"},
    "as a result":       {"type": "logical", "operator": "THEN"},
    "thereby":           {"type": "logical", "operator": "THEN"},
    "so that":           {"type": "logical", "operator": "THEN"},
    "so":                {"type": "logical", "operator": "THEN"},
    "therefore":         {"type": "logical", "operator": "THEN"},
    "thus":              {"type": "logical", "operator": "THEN"},

    "and":               {"type": "logical", "operator": "AND"},
    "as well as":        {"type": "logical", "operator": "AND"},
    "both":              {"type": "logical", "operator": "AND"},

    "or":                {"type": "logical", "operator": "OR"},
    "either":            {"type": "logical", "operator": "OR"},
    "alternatively":     {"type": "logical", "operator": "OR"},

    "not":               {"type": "logical", "operator": "NOT"},
    "no":                {"type": "logical", "operator": "NOT"},

    # Összehasonlítás: >=
    "at least":          {"type": "comparison", "operator": ">="},
    "not less than":     {"type": "comparison", "operator": ">="},
    "no less than":      {"type": "comparison", "operator": ">="},
    "minimum of":        {"type": "comparison", "operator": ">="},
    "from ... upwards":  {"type": "comparison", "operator": ">="},
    "reach":             {"type": "comparison", "operator": ">="},
    "reaches":           {"type": "comparison", "operator": ">="},
    "reaching":          {"type": "comparison", "operator": ">="},
    "or more":           {"type": "comparison", "operator": ">="},
    "or older":          {"type": "comparison", "operator": ">="},
    "or above":          {"type": "comparison", "operator": ">="},
    "is at least":       {"type": "comparison", "operator": ">="},

    # Összehasonlítás: >
    "more than":         {"type": "comparison", "operator": ">"},
    "greater than":      {"type": "comparison", "operator": ">"},
    "over":              {"type": "comparison", "operator": ">"},
    "above":             {"type": "comparison", "operator": ">"},
    "exceeds":           {"type": "comparison", "operator": ">"},
    "exceeding":         {"type": "comparison", "operator": ">"},
    "strictly more than":{"type": "comparison", "operator": ">"},
    "older than":        {"type": "comparison", "operator": ">"},

    # Összehasonlítás: <=
    "at most":           {"type": "comparison", "operator": "<="},
    "no more than":      {"type": "comparison", "operator": "<="},
    "not more than":     {"type": "comparison", "operator": "<="},
    "maximum of":        {"type": "comparison", "operator": "<="},
    "up to":             {"type": "comparison", "operator": "<="},
    "or less":           {"type": "comparison", "operator": "<="},
    "or below":          {"type": "comparison", "operator": "<="},
    "is at most":        {"type": "comparison", "operator": "<="},

    # Összehasonlítás: <
    "less than":         {"type": "comparison", "operator": "<"},
    "fewer than":        {"type": "comparison", "operator": "<"},
    "below":             {"type": "comparison", "operator": "<"},
    "under":             {"type": "comparison", "operator": "<"},
    "strictly less than":{"type": "comparison", "operator": "<"},
    "younger than":      {"type": "comparison", "operator": "<"},

    # Összehasonlítás: ==
    "equal to":          {"type": "comparison", "operator": "=="},
    "equals":            {"type": "comparison", "operator": "=="},
    "exactly":           {"type": "comparison", "operator": "=="},
    "precisely":         {"type": "comparison", "operator": "=="},
    "the same as":       {"type": "comparison", "operator": "=="},

    # Összehasonlítás: !=
    "not equal to":      {"type": "comparison", "operator": "!="},
    "different from":    {"type": "comparison", "operator": "!="},

    # Tartomány / range
    "between":           {"type": "range", "operator": "BETWEEN"},
    "from ... to":       {"type": "range", "operator": "BETWEEN"},
    "in the range":      {"type": "range", "operator": "BETWEEN"},

    # Kötelezettség / engedély
    "must":              {"type": "modality", "operator": "MUST"},
    "have to":           {"type": "modality", "operator": "MUST"},
    "shall":             {"type": "modality", "operator": "MUST"},
    "may":               {"type": "modality", "operator": "MAY"},
    "is allowed to":     {"type": "modality", "operator": "MAY"},
    "can":               {"type": "modality", "operator": "MAY"},

    # Változás (növekedés / csökkenés)
    "increase":          {"type": "change", "operator": "INC"},
    "increases":         {"type": "change", "operator": "INC"},
    "decrease":          {"type": "change", "operator": "DEC"},
    "decreases":         {"type": "change", "operator": "DEC"},
    "reduced by":        {"type": "change", "operator": "DEC"},
    "reduction of":      {"type": "change", "operator": "DEC"},

    # Értékadás jellegű szavak (nem kötelező, de hasznos lehet)
    "is":                {"type": "assignment", "operator": "="},
    "gets":              {"type": "assignment", "operator": "="},
    "is set to":         {"type": "assignment", "operator": "="},
    "will be":           {"type": "assignment", "operator": "="},

    # Segítség: 'free' → 0 értékre utal
    "free":              {"type": "value_hint", "operator": "0"},
}
