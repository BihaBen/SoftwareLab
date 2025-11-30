import os

from Pre_process.DataCleaning import load_json_requirements
from Checking_process import (
    check_variable_conflicts,
    check_logical_exclusions,
    check_redundant_rules,
)


def run_all_checks(requirements_data):
    errors = []

    # 1. Változóütközés ellenőrzés
    variable_conflicts = check_variable_conflicts.check(requirements_data)
    if variable_conflicts:
        errors.append(("Változóütközések", variable_conflicts))

    # 2. Logikai kizárások ellenőrzése
    logical_exclusions = check_logical_exclusions.check(requirements_data)
    if logical_exclusions:
        errors.append(("Logikai kizárások", logical_exclusions))

    # 3. Redundáns szabályok ellenőrzése
    redundant_rules = check_redundant_rules.check(requirements_data)
    if redundant_rules:
        errors.append(("Redundáns szabályok", redundant_rules))

    return errors


def main():
    # Itt add meg, melyik szövegfájlból épüljön fel a JSON,
    # ha még nem létezik requirements.json
    text_source_path = os.path.join("Examples", "price_calculation_example.txt")
    json_path = "requirements.json"

    try:
        requirements = load_json_requirements(
            json_path=json_path,
            text_path=text_source_path,
        )
    except Exception as e:
        print(f"Hiba történt a JSON betöltése / generálása közben:\n{e}")
        return

    print("Ellenőrzés indítása...\n")
    errors = run_all_checks(requirements)

    if not errors:
        print("A JSON teljesen hibátlan.")
    else:
        print("❌ Hibák találhatók:")
        for error_type, details in errors:
            print(f"\n--- {error_type} ---")
            for detail in details:
                print(f"- {detail}")


if __name__ == "__main__":
    main()
