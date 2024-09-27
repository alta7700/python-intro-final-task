def show_to_user(text: str):
    print(text)


def get_number(text: str, gt: int = None, lt: int = None) -> int:
    try:
        num = int(input(f"{text}: "))
    except ValueError:
        show_to_user("Введено некорректное число")
        return get_number(text, gt)

    if lt is not None and num >= lt:
        show_to_user(f"Число должно быть меньше {lt}")
        return get_number(text, gt)

    if gt is not None and num <= gt:
        show_to_user(f"Число должно быть больше {gt}")
        return get_number(text, gt)
    return num


_yes_values = {"yes", "y", "да", "+"}
_no_values = {"no", "n", "нет", "-"}


def yes_no_input(text: str) -> bool:
    answer = input(f"{text}(y/n): ")
    if answer in _yes_values:
        return True
    if answer in _no_values:
        return False
    else:
        return yes_no_input(f"Введите корректное значение ({", ".join(_yes_values)}/{", ".join(_no_values)})")
