# pytui.syntax.themes - theme (token type -> color)


# RGBA
ColorTuple = tuple[int, int, int, int]


def get_theme(name: str = "default") -> dict[str, ColorTuple]:
    """返回主题：token_type -> (r, g, b, a)。"""
    themes: dict[str, dict[str, ColorTuple]] = {
        "default": {
            "keyword": (204, 120, 50, 255),
            "string": (206, 145, 120, 255),
            "comment": (106, 153, 85, 255),
            "number": (181, 206, 168, 255),
            "function": (220, 220, 170, 255),
            "plain": (220, 220, 220, 255),
        },
        "dark": {
            "keyword": (197, 134, 192, 255),
            "string": (152, 195, 121, 255),
            "comment": (127, 132, 142, 255),
            "number": (209, 154, 102, 255),
            "function": (97, 175, 239, 255),
            "plain": (220, 220, 220, 255),
        },
    }
    return themes.get(name, themes["default"]).copy()
