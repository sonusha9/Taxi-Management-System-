"""Color theme and ttk style configuration."""

COLORS = {
    "bg": "#eef2f7",
    "sidebar": "#1a1a2e",
    "header": "#16213e",
    "accent": "#ffc107",
    "accent_dark": "#e6ac00",
    "primary": "#ff6b35",
    "primary_dark": "#e55a2b",
    "success": "#2ecc71",
    "info": "#3498db",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "text": "#2c3e50",
    "text_light": "#ffffff",
    "text_muted": "#7f8c8d",
    "card": "#ffffff",
    "card_border": "#dce3ed",
    "input_bg": "#ffffff",
    "tree_head": "#16213e",
    "login_gradient_top": "#1a1a2e",
    "login_gradient_bottom": "#0f3460",
    "stat_available": "#2ecc71",
    "stat_on_ride": "#f39c12",
    "stat_offline": "#95a5a6",
}


def setup_styles(style):
    style.theme_use("clam")

    style.configure(".", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 10))
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Card.TFrame", background=COLORS["card"])
    style.configure("Header.TFrame", background=COLORS["header"])

    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"])
    style.configure("Card.TLabel", background=COLORS["card"], foreground=COLORS["text"])
    style.configure("Header.TLabel", background=COLORS["header"], foreground=COLORS["text_light"])
    style.configure("Muted.TLabel", background=COLORS["bg"], foreground=COLORS["text_muted"])
    style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground=COLORS["accent"])
    style.configure("Subtitle.TLabel", font=("Segoe UI", 11), foreground=COLORS["text_muted"])

    style.configure(
        "TLabelframe",
        background=COLORS["card"],
        bordercolor=COLORS["card_border"],
        relief="solid",
    )
    style.configure(
        "TLabelframe.Label",
        background=COLORS["card"],
        foreground=COLORS["header"],
        font=("Segoe UI", 10, "bold"),
    )

    style.configure(
        "TNotebook",
        background=COLORS["bg"],
        tabmargins=[2, 6, 2, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background=COLORS["card_border"],
        foreground=COLORS["text"],
        padding=[14, 8],
        font=("Segoe UI", 10),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["accent"]), ("active", "#ffe082")],
        foreground=[("selected", COLORS["header"]), ("active", COLORS["header"])],
    )

    style.configure(
        "Accent.TButton",
        background=COLORS["accent"],
        foreground=COLORS["header"],
        font=("Segoe UI", 10, "bold"),
        padding=[16, 8],
        borderwidth=0,
    )
    style.map("Accent.TButton", background=[("active", COLORS["accent_dark"])])

    style.configure(
        "Primary.TButton",
        background=COLORS["primary"],
        foreground=COLORS["text_light"],
        font=("Segoe UI", 10, "bold"),
        padding=[14, 8],
        borderwidth=0,
    )
    style.map("Primary.TButton", background=[("active", COLORS["primary_dark"])])

    style.configure(
        "Success.TButton",
        background=COLORS["success"],
        foreground=COLORS["text_light"],
        font=("Segoe UI", 10, "bold"),
        padding=[12, 6],
        borderwidth=0,
    )
    style.map("Success.TButton", background=[("active", "#27ae60")])

    style.configure(
        "Info.TButton",
        background=COLORS["info"],
        foreground=COLORS["text_light"],
        font=("Segoe UI", 10),
        padding=[12, 6],
        borderwidth=0,
    )
    style.map("Info.TButton", background=[("active", "#2980b9")])

    style.configure(
        "TButton",
        padding=[10, 6],
        font=("Segoe UI", 10),
    )

    style.configure(
        "Treeview",
        background=COLORS["input_bg"],
        fieldbackground=COLORS["input_bg"],
        foreground=COLORS["text"],
        rowheight=28,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["tree_head"],
        foreground=COLORS["text_light"],
        font=("Segoe UI", 10, "bold"),
        relief="flat",
    )
    style.map("Treeview.Heading", background=[("active", COLORS["primary"])])

    style.configure("TEntry", fieldbackground=COLORS["input_bg"], padding=6)
    style.configure("TCombobox", fieldbackground=COLORS["input_bg"], padding=4)
