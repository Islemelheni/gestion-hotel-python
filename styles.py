from tkinter import ttk

def appliquer_theme(app):
    style = ttk.Style(app)
    style.theme_use("clam")

    # Boutons
    style.configure(
        "TButton",
        font=("Segoe UI", 10),
        padding=6
    )

    # Labels
    style.configure(
        "TLabel",
        font=("Segoe UI", 10)
    )

    # Titres
    style.configure(
        "Title.TLabel",
        font=("Segoe UI", 16, "bold")
    )

    # Table
    style.configure(
        "Treeview",
        font=("Segoe UI", 10),
        rowheight=28
    )

    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 10, "bold")
    )
