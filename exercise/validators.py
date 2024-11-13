from django.core.exceptions import ValidationError
import re


def validate_exercise_name(name):
    """
    Make sure that:
    - exercise name can only contains:
        - letters
        - numbers
        - spaces
        - hyphens
        - parentheses
        - apostrophes
    - exercise name can only start with a character
    - exercise name must not contain consecutive spaces
    """

    # Ensure the name starts with a letter
    if not name[0].isalpha():
        raise ValidationError("Name must start with a letter.")

    # Check for consecutive spaces
    if re.search(r'\s\s+', name.strip()):
        raise ValidationError("Name cannot contain consecutive spaces.")

    # Define a pattern to allow only the specified characters
    pattern = r"^[a-zA-Z0-9\s\-\(\)']+$"
    if not re.fullmatch(pattern, name.strip()):

        raise ValidationError(
            "Name can only contain: (letters, numbers, spaces, hyphens, parentheses, and apostrophes)" # noqa
        )
