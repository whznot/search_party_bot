def validate_age(age_text: str) -> int | None:
    if not age_text.isdigit():
        return None

    age = int(age_text)
    if 1 <= age <= 100:
        return age

    return None
