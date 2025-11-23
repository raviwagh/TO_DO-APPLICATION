"""Theme configurations for the application."""

THEMES = {
    "superhero": {
        "name": "Superhero",
        "type": "dark",
        "base_theme": "superhero",
        "colors": {
            "high_priority": "#e74c3c",
            "medium_priority": "#f39c12",
            "low_priority": "#2ecc71",
            "overdue_fg": "#c0392b",
            "overdue_bg": "#fadbd8",
            "completed": "#7f8c8d",
            "accent": "#4e73df",
        },
        "description": "Dark theme with blue accents"
    },
    "cosmo": {
        "name": "Cosmo",
        "type": "light",
        "base_theme": "cosmo",
        "colors": {
            "high_priority": "#d9534f",
            "medium_priority": "#f0ad4e",
            "low_priority": "#5cb85c",
            "overdue_fg": "#a94442",
            "overdue_bg": "#f2dede",
            "completed": "#999999",
            "accent": "#2780e3",
        },
        "description": "Clean light theme with modern aesthetics"
    },
    "darkly": {
        "name": "Darkly",
        "type": "dark",
        "base_theme": "darkly",
        "colors": {
            "high_priority": "#e74c3c",
            "medium_priority": "#f39c12",
            "low_priority": "#00bc8c",
            "overdue_fg": "#c0392b",
            "overdue_bg": "#3d1f1f",
            "completed": "#888888",
            "accent": "#375a7f",
        },
        "description": "Sleek dark theme with subtle colors"
    },
    "flatly": {
        "name": "Flatly",
        "type": "light",
        "base_theme": "flatly",
        "colors": {
            "high_priority": "#e74c3c",
            "medium_priority": "#f39c12",
            "low_priority": "#18bc9c",
            "overdue_fg": "#c0392b",
            "overdue_bg": "#fadbd8",
            "completed": "#95a5a6",
            "accent": "#2c3e50",
        },
        "description": "Flat design light theme"
    },
    "cyborg": {
        "name": "Cyborg",
        "type": "dark",
        "base_theme": "cyborg",
        "colors": {
            "high_priority": "#ee4444",
            "medium_priority": "#ff8800",
            "low_priority": "#33ff99",
            "overdue_fg": "#ff0000",
            "overdue_bg": "#2d1f1f",
            "completed": "#777777",
            "accent": "#2a9fd6",
        },
        "description": "Futuristic dark theme with cyan accents"
    },
    "solar": {
        "name": "Solar",
        "type": "light",
        "base_theme": "solar",
        "colors": {
            "high_priority": "#dc322f",
            "medium_priority": "#cb4b16",
            "low_priority": "#859900",
            "overdue_fg": "#dc322f",
            "overdue_bg": "#fdf6e3",
            "completed": "#93a1a1",
            "accent": "#268bd2",
        },
        "description": "Warm light theme with solarized colors"
    },
}


def get_theme_config(theme_name):
    """Get theme configuration by name."""
    return THEMES.get(theme_name, THEMES["superhero"])


def get_theme_names():
    """Get list of all available theme names."""
    return list(THEMES.keys())


def get_themes_by_type(theme_type):
    """Get themes filtered by type (light/dark)."""
    return {k: v for k, v in THEMES.items() if v["type"] == theme_type}
