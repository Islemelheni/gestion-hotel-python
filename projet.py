import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import hashlib 
#---Hashlib---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
#---

DB_NAME = "hotel.db"

#  Base de données 
def connecter():
    return sqlite3.connect(DB_NAME)

def initialiser_bd():
    con = connecter()
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS Client (
        id_client INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        nom TEXT,
        prenom TEXT,
        cin TEXT,
        telephone TEXT,
        adresse TEXT,
        date_naissance TEXT
    );

    CREATE TABLE IF NOT EXISTS Chambre (
        num_chambre INTEGER PRIMARY KEY,
        type TEXT,
        prix_nuit REAL,
        statut TEXT
    );
    CREATE TABLE IF NOT EXISTS Reservation (
        id_res INTEGER PRIMARY KEY AUTOINCREMENT,
        id_client INTEGER,
        num_chambre INTEGER,
        date_debut TEXT,
        date_fin TEXT,
        statut TEXT DEFAULT 'en_attente',
        FOREIGN KEY(id_client) REFERENCES Client(id_client),
        FOREIGN KEY(num_chambre) REFERENCES Chambre(num_chambre)
    );

    CREATE TABLE IF NOT EXISTS Facture_Chambre (
        id_facture INTEGER PRIMARY KEY AUTOINCREMENT,
        num_chambre INTEGER,
        type_chambre TEXT,
        date_debut TEXT,
        date_fin TEXT,
        montant REAL,
        date_paiement TEXT
    );

    CREATE TABLE IF NOT EXISTS User (
        id_user INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    );
 """)

    con.commit()
    con.close()

def migration_client_table():
    con = connecter()
    cur = con.cursor()

    # Récupérer les colonnes existantes
    cur.execute("PRAGMA table_info(Client)")
    colonnes = [col[1] for col in cur.fetchall()]

    if "username" not in colonnes:
        cur.execute("ALTER TABLE Client ADD COLUMN username TEXT")

    if "password" not in colonnes:
        cur.execute("ALTER TABLE Client ADD COLUMN password TEXT")

    if "role" not in colonnes:
        cur.execute("ALTER TABLE Client ADD COLUMN role TEXT")

    con.commit()
    con.close()


#  Fonctions DB 
def ajouter_chambre_db(num, type_c, prix):
    con = connecter()
    cur = con.cursor()
    cur.execute("INSERT INTO Chambre VALUES (?,?,?,?)", (num, type_c, prix, "libre"))
    con.commit()
    con.close()

def supprimer_chambre_db(num):
    con = connecter()
    cur = con.cursor()
    cur.execute("DELETE FROM Chambre WHERE num_chambre=?", (num,))
    con.commit()
    con.close()

def lister_chambres_db():
    con = connecter()
    cur = con.cursor()
    cur.execute("SELECT * FROM Chambre")
    rows = cur.fetchall()
    con.close()
    return rows

def lister_chambres_libres_db():
    con = connecter()
    cur = con.cursor()
    cur.execute("""
        SELECT num_chambre, type, prix_nuit, statut
        FROM Chambre
        WHERE statut = 'libre'
    """)
    rows = cur.fetchall()
    con.close()
    return rows


def ajouter_client_db(nom, prenom, telephone, cin="", adresse="", date_naissance=""):
    con = connecter()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO Client(username, password, role, nom, prenom, cin, telephone, adresse, date_naissance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("", "", "user", nom, prenom, cin, telephone, adresse, date_naissance))
    con.commit()
    con.close()

def lister_clients_db():
    con = connecter()
    cur = con.cursor()
    cur.execute("""
        SELECT
            id_client,
            nom,
            prenom,
            telephone,
            cin,
            adresse,
            date_naissance
        FROM Client
    """)
    rows = cur.fetchall()
    con.close()
    return rows

def rechercher_client_db(texte):
    con = connecter()
    cur = con.cursor()
    cur.execute("""
        SELECT
            id_client,
            nom,
            prenom,
            telephone,
            cin,
            adresse,
            date_naissance
        FROM Client
        WHERE nom LIKE ?
            OR cin LIKE ?
    """, (f"%{texte}%", f"%{texte}%"))
    rows = cur.fetchall()
    con.close()
    return rows

def reserver_chambre_db(id_client, num_chambre, d1, d2, statut):
    con = connecter()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO Reservation
        (id_client, num_chambre, date_debut, date_fin, statut)
        VALUES (?, ?, ?, ?, 'en_attente')
    """, (id_client, num_chambre, d1, d2))
    cur.execute(
        "UPDATE Chambre SET statut='demandée' WHERE num_chambre=?",
        (num_chambre,)
    )
    con.commit()
    con.close()

def liberer_chambre_db(num_ch):
    con = connecter()
    cur = con.cursor()
    cur.execute(
        "UPDATE Chambre SET statut='libre' WHERE num_chambre=?",
        (num_ch,)
    )
    con.commit()
    con.close()

def supprimer_reservation_db(id_res):
    con = connecter()
    cur = con.cursor()
    cur.execute("DELETE FROM Reservation WHERE id_res=?", (id_res,))
    con.commit()
    con.close()

def calculer_montant(prix_nuit, d1, d2):
    date_deb = datetime.strptime(d1, "%Y-%m-%d")
    date_fin = datetime.strptime(d2, "%Y-%m-%d")
    nb_nuits = (date_fin - date_deb).days
    return max(nb_nuits, 1) * prix_nuit

def enregistrer_facture_chambre(num_chambre, type_ch, d1, d2, montant):
    con = connecter()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO Facture_Chambre
        (num_chambre, type_chambre, date_debut, date_fin, montant, date_paiement)
        VALUES (?, ?, ?, ?, ?, DATE('now'))
    """, (num_chambre, type_ch, d1, d2, montant))
    con.commit()
    con.close()

def lister_reservations_db():
    con = connecter()
    cur = con.cursor()
    cur.execute("""
        SELECT r.id_res,
               c.nom || ' ' || c.prenom,
               r.num_chambre,
               r.date_debut,
               r.date_fin,
               r.statut
        FROM Reservation r
        JOIN Client c ON c.id_client = r.id_client
        ORDER BY r.date_debut
    """)
    rows = cur.fetchall()
    con.close()
    return rows

def statistiques_db():
    con = connecter()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM Chambre")
    total = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(*) FROM Chambre WHERE statut='libre'"
    )
    libres = cur.fetchone()[0]
    con.close()
    taux = (total - libres) / total * 100 if total else 0
    return total, libres, taux

def creer_compte(username, password, role, nom="", prenom="", telephone=""):
    con = connecter()
    cur = con.cursor()

    cur.execute("SELECT id_client FROM Client WHERE username=?", (username,))
    if cur.fetchone():
        con.close()
        return False

    cur.execute("""
    INSERT INTO Client
    (username, password, role, nom, prenom, cin, telephone, adresse, date_naissance)
    VALUES (?,?,?,?,?,?,?,?,?)""", (username, hash_password(password), role, nom, prenom,
    "",     # cin
    telephone,
    "",     # adresse
    ""      # date_naissance
        ))

    con.commit()
    con.close()
    return True
def verifier_login(username, password):
    con = connecter()
    cur = con.cursor()
    cur.execute("""
        SELECT id_client, role
        FROM Client
        WHERE username=? AND password=?
    """, (username.strip(), hash_password(password.strip())))
    res = cur.fetchone()
    con.close()
    return res
def inscrire_user(username, password, nom, prenom, cin, telephone, adresse, date_naissance):
    con = connecter()
    cur = con.cursor()

    cur.execute(
        "SELECT id_client FROM Client WHERE username=?",
        (username,)
    )
    if cur.fetchone():
        con.close()
        return False, "Nom d'utilisateur déjà utilisé."

    cur.execute("""
        INSERT INTO Client
        (username, password, role, nom, prenom, cin, telephone, adresse, date_naissance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        username,
        hash_password(password),
        "user",
        nom,
        prenom,
        cin,
        telephone,
        adresse,
        date_naissance
        )
    )
    con.commit()
    con.close()
    return True, "Compte créé avec succès."

def calculer_stats():
    con = connecter()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM Reservation")
    nb_res = cur.fetchone()[0]

    cur.execute("SELECT IFNULL(SUM(montant), 0) FROM Facture_Chambre")
    ca_chambres = cur.fetchone()[0]

    con.close()
    return nb_res, ca_chambres

# Interface 
class HotelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestion Hôtel")
        self.geometry("1000x650")
        style = ttk.Style()
        style.theme_use("clam")

        # Emplacement exact pour déclarer les fenêtres secondaires
        self.win_clients = None
        self.win_chambres = None

        # ensuite seulement on crée les onglets et widgets
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_ch = ttk.Frame(self.notebook)
        self.tab_cl = ttk.Frame(self.notebook)
        self.tab_res = ttk.Frame(self.notebook)
        self.tab_stat = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_ch, text="🏨 Chambres")
        self.notebook.add(self.tab_cl, text="👥 Clients")
        self.notebook.add(self.tab_res, text="📅 Réservations")
        self.notebook.add(self.tab_stat, text="📊 Stats")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)


        # widgets
        self.widgets_chambres()
        self.widgets_clients()
        self.widgets_res()
        self.widgets_stats()
    
    def on_tab_changed(self, event):
        tab = event.widget.tab(event.widget.index("current"))["text"]
        if "Stats" in tab:
            self.refresh_stats()

    
    #  Chambres 
    def widgets_chambres(self):
        form = ttk.LabelFrame(
            self.tab_ch,
            text="🛏️  Formulaire Chambre",
            padding=10
        )
        form.pack(fill="x", padx=20, pady=20)

        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Numéro :").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.ent_num = ttk.Entry(form)
        self.ent_num.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form, text="Type :").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.cb_type = ttk.Combobox(
            form, values=("simple", "double", "suite"), state="readonly"
        )
        self.cb_type.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.cb_type.set("simple")  # sélectionne automatiquement "simple" au lancement

        ttk.Label(form, text="Prix / nuit :").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        self.ent_prix = ttk.Entry(form)
        self.ent_prix.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Button(
            btn_frame,
            text="➕ Ajouter",
            style="Primary.TButton",
            command=self.ajouter_chambre
        ).grid(row=0, column=0, padx=10)

        ttk.Button(
            btn_frame,
            text="📋 Consulter",
            style="Primary.TButton",
            command=self.ouvrir_fenetre_chambres
        ).grid(row=0, column=1, padx=10)
        
        self.refresh_chambres()

    def ouvrir_fenetre_chambres(self):
        print("✅ bouton consulter chambres cliqué")
        if self.win_chambres is not None and self.win_chambres.winfo_exists():
            self.win_chambres.lift()
            return

        self.win_chambres = tk.Toplevel(self)
        self.win_chambres.title("📋 Gestion des chambres")
        self.win_chambres.geometry("750x420")

        # Filtre statut
        filtre = ttk.LabelFrame(
            self.win_chambres,
            text="🔍  Filtre des chambres",
            padding=10
        )
        filtre.pack(fill="x", padx=10, pady=10)

        ttk.Button(
            filtre, text="📑 Toutes",
            command=self.afficher_toutes_chambres
        ).pack(side="left", padx=5)

        ttk.Button(
            filtre, text="🟢 Libres",
            command=lambda: self.filtrer_chambres_par_statut("libre")
        ).pack(side="left", padx=5)
        ttk.Button(
            filtre, text="🟠 Demandées",
            command=lambda: self.filtrer_chambres_par_statut("demandée")
        ).pack(side="left", padx=5)

        ttk.Button(
            filtre, text="🔴 Occupées",
            command=lambda: self.filtrer_chambres_par_statut(("occupée", "reservée"))
        ).pack(side="left", padx=5)
        
        # Tableau
        table_frame = ttk.Frame(self.win_chambres)
        table_frame.pack(
            fill="both", expand=True,
            padx=10, pady=10
        )

        self.tree_ch = ttk.Treeview(
            table_frame,
            columns=("num", "type", "prix", "statut"),
            show="headings"
        )
        # 🎨 Couleurs selon statut
        self.tree_ch.tag_configure("libre", background="#d4f7d4")       # vert
        self.tree_ch.tag_configure("demandée", background="#ffe5b4")   # orange
        self.tree_ch.tag_configure("reservée", background="#d0e7ff")   # bleu clair
        self.tree_ch.tag_configure("occupée", background="#f7c6c6")   # rouge

        self.tree_ch.heading("num", text="Numéro")
        self.tree_ch.heading("type", text="Type")
        self.tree_ch.heading("prix", text="Prix / nuit")
        self.tree_ch.heading("statut", text="Statut")

        self.tree_ch.column("num", width=80, anchor="center")
        self.tree_ch.column("type", width=120)
        self.tree_ch.column("prix", width=100, anchor="e")
        self.tree_ch.column("statut", width=100, anchor="center")

        self.tree_ch.pack(fill="both", expand=True)

        # Boutons
        btns = ttk.Frame(self.win_chambres)
        btns.pack(pady=5)

        ttk.Button(
            btns, text="✏️ Modifier",
            command=self.modifier_chambre
        ).grid(row=0, column=0, padx=10)

        ttk.Button(
            btns, text="🗑 Supprimer",
            style="Danger.TButton",
            command=self.supprimer_chambre
        ).grid(row=0, column=1, padx=10)

        ttk.Button(
            btns, text="❌ Fermer",
            command=self.win_chambres.destroy
        ).grid(row=0, column=2, padx=10)

        self.refresh_chambres()

    def ajouter_chambre(self):
        print(">>> AJOUTER_CHAMBRE APPELÉE <<<")
        try:
            # 1️⃣ Récupération des valeurs depuis les widgets
            num_input = self.ent_num.get().strip()
            type_input = self.cb_type.get().strip()
            prix_input = self.ent_prix.get().strip()   # enlever espaces invisibles
            prix_input = prix_input.replace(",", ".")  # convertir virgule en point
            try:
                prix_float = float(prix_input)
            except ValueError:
                messagebox.showerror("Erreur", f"Prix invalide : {repr(prix_input)}")
                return
            # 3️⃣ Vérification du numéro(s)
            if not num_input:
                messagebox.showwarning("Champs vides", "Veuillez remplir le numéro de la chambre !")
                return

            chambres = []  # liste des chambres à ajouter

            lignes = num_input.split("\n")
            for ligne in lignes:
                parts = ligne.split(",")
                if len(parts) == 1:
                    nums = parts[0].split(",")
                    for n in nums:
                        n = n.strip()
                        if not n.isdigit():
                            messagebox.showerror("Erreur", f"Numéro invalide : {n}")
                            return
                        chambres.append((int(n), type_input, prix_float))
                elif len(parts) == 3:
                    n = parts[0].strip()
                    t = parts[1].strip()
                    p = parts[2].strip()
                    if not n.isdigit():
                        messagebox.showerror("Erreur", f"Numéro invalide : {n}")
                        return
                    try:
                        p_float = float(p.replace(",","."))
                    except ValueError:
                        messagebox.showerror("Erreur", f"Prix invalide : {p}")
                        return
                    chambres.append((int(n), t, p_float))
                else:
                    messagebox.showerror("Erreur", f"Ligne invalide : {ligne}")
                    return

            # 4️⃣ Insertion dans la DB
            for num, typ, prix in chambres:
                try:
                    ajouter_chambre_db(num, typ, prix)
                except sqlite3.IntegrityError:
                    messagebox.showwarning("Chambre existante", f"La chambre {num} existe déjà et a été ignorée.")

            # 5️⃣ Nettoyage formulaire
            self.ent_num.delete(0, tk.END)
            self.cb_type.set("simple")  # valeur par défaut
            self.ent_prix.delete(0, tk.END)

            self.refresh_chambres()
            self.charger_chambres_libres_combo()
            messagebox.showinfo("Succès", "Chambres ajoutées avec succès !")

        except Exception as e:
            messagebox.showerror("Erreur", str(e))


    def supprimer_chambre(self):
        if not hasattr(self, "tree_ch"):
            return
        sel = self.tree_ch.selection()
        if not sel:
            messagebox.showwarning("Aucune chambre", "Veuillez sélectionner une chambre à supprimer.")
            return
        num = self.tree_ch.item(sel)["values"][0]

        if not messagebox.askyesno("Confirmation", f"Supprimer la chambre {num} ?"):
            return

        supprimer_chambre_db(num)
        self.refresh_chambres()
        self.charger_chambres_libres_combo()

    def modifier_chambre(self):
        if not hasattr(self, "tree_ch"):
            return

        sel = self.tree_ch.selection()
        if not sel:
            messagebox.showwarning("Aucune chambre", "Veuillez sélectionner une chambre à modifier.")
            return

        num, old_type, old_prix, old_statut = self.tree_ch.item(sel)["values"]

        win_mod = tk.Toplevel(self)
        win_mod.title(f"✏️ Modifier chambre {num}")
        win_mod.geometry("380x230")
        win_mod.resizable(False, False)

        frame = ttk.LabelFrame(win_mod, text="✏️  Modifier Chambre", padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Numéro :").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        en_num_mod = ttk.Entry(frame, state="disabled")
        en_num_mod.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        en_num_mod.insert(0, num)

        ttk.Label(frame, text="Type :").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        cb_type_mod = ttk.Combobox(frame, values=("simple", "double", "suite"), state="readonly")
        cb_type_mod.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        cb_type_mod.set(old_type)

        ttk.Label(frame, text="Prix / nuit :").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        en_prix_mod = ttk.Entry(frame)
        en_prix_mod.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        en_prix_mod.insert(0, old_prix)

        ttk.Label(frame, text="Statut :").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        cb_statut_mod = ttk.Combobox(frame, values=("libre", "occupée", "reservée", "demandée"), state="readonly")
        cb_statut_mod.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        cb_statut_mod.set(old_statut)

        frame.columnconfigure(1, weight=1)

        def enregistrer_chambre():
            new_type = cb_type_mod.get().strip()
            new_prix = en_prix_mod.get().strip()
            new_statut = cb_statut_mod.get().strip()

            if not new_type or not new_prix or not new_statut:
                messagebox.showwarning("Champs vides", "Veuillez remplir tous les champs.")
                return

            try:
                float(new_prix)
            except ValueError:
                messagebox.showwarning("Erreur", "Le prix doit être un nombre.")
                return

            con = connecter()
            cur = con.cursor()
            cur.execute("""
                UPDATE Chambre
                SET type = ?, prix_nuit = ?, statut = ?
                WHERE num_chambre = ?
            """, (new_type, new_prix, new_statut, num))
            con.commit()
            con.close()

            self.refresh_chambres()
            self.charger_chambres_libres_combo()
            win_mod.destroy()
            messagebox.showinfo("Succès", "Chambre modifiée avec succès.")

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="💾 Enregistrer", command=enregistrer_chambre).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="❌ Annuler", command=win_mod.destroy).grid(row=0, column=1, padx=5)

    def afficher_toutes_chambres(self):
        self.refresh_chambres()

    def filtrer_chambres_par_statut(self, statuts):
        if not hasattr(self, "tree_ch"):
            return

        con = connecter()
        cur = con.cursor()

        if isinstance(statuts, tuple):
            placeholders = ",".join("?" * len(statuts))
            cur.execute(
                f"SELECT * FROM Chambre WHERE statut IN ({placeholders})",
                statuts
            )
        else:
            cur.execute(
                "SELECT * FROM Chambre WHERE statut = ?",
                (statuts,)
            )

        rows = cur.fetchall()
        con.close()

        # vider tableau
        for i in self.tree_ch.get_children():
            self.tree_ch.delete(i)

        # 🔁 INSÉRER CHAQUE LIGNE
        for r in rows:
            statut_db = r[3]

            if statut_db == "libre":
                tag = "libre"
            elif statut_db == "demandée":
                tag = "demandée"
            elif statut_db == "reservée":
                tag = "reservée"   # 🔵 BLEU
            elif statut_db == "occupée":
                tag = "occupée"    # 🔴 ROUGE
            else:
                tag = "libre"

            self.tree_ch.insert("", "end", values=r, tags=(tag,))


    def liberer_chambre(self):
        # Utiliser le Treeview existant où les réservations validées sont affichées
        selected = self.tree_future.selection()  # <-- ton Treeview actuel
        if not selected:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une réservation à libérer.")
            return

        today = date.today()
        con = connecter()
        cur = con.cursor()
        try:
            for item in selected:
                r = self.tree_future.item(item, "values")  # récupère la ligne sélectionnée
                id_res = r[0]       # id de la réservation
                num_chambre = r[2]       # numéro de la chambre
                date_fin_str = r[4] # date de fin au format string

                # Conversion de date_fin
                try:
                    date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d").date()
                except Exception:
                    messagebox.showerror("Erreur", f"Format de date invalide pour réservation {id_res}")
                    continue

                # Vérifier si la réservation est terminée
                if date_fin > today:
                    messagebox.showwarning("Impossible", f"La réservation {id_res} n'est pas encore terminée.")
                    continue

                # Libérer la chambre
                cur.execute("UPDATE Chambre SET statut='libre' WHERE num_chambre=?", (num_chambre,))
                # Supprimer la réservation terminée
                cur.execute("DELETE FROM Reservation WHERE id_res=?", (id_res,))

            con.commit()
            messagebox.showinfo("Succès", "Chambre(s) libérée(s) avec succès.")

        except Exception as e:
            messagebox.showerror("Erreur SQL", str(e))
        finally:
            con.close()
            # Rafraîchir le Treeview pour voir les changements
            self.refresh_futures()


    #  Clients 
    def widgets_clients(self):
        form = ttk.LabelFrame(self.tab_cl, text="👥 Formulaire Client", padding=10)
        form.pack(fill="x", padx=20, pady=20)
        form.columnconfigure(1, weight=1)


        # Nom
        ttk.Label(form, text="Nom :").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.en_nom = ttk.Entry(form)
        self.en_nom.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Prénom
        ttk.Label(form, text="Prénom :").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.en_pre = ttk.Entry(form)
        self.en_pre.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Téléphone
        ttk.Label(form, text="Téléphone :").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.en_telephone = ttk.Entry(form)
        self.en_telephone.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # CIN
        ttk.Label(form, text="CIN :").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.en_cin = ttk.Entry(form)
        self.en_cin.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Adresse
        ttk.Label(form, text="Adresse :").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.en_adresse = ttk.Entry(form)
        self.en_adresse.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Date de naissance
        ttk.Label(form, text="Date de naissance (YYYY-MM-DD) :").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.en_date_naissance = ttk.Entry(form)
        self.en_date_naissance.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(form, text="Rechercher (Nom ou CIN) :").grid(
            row=6, column=0, padx=5, pady=5, sticky="e"
        )
        self.en_search = ttk.Entry(form)
        self.en_search.grid(row=6, column=1, padx=5, pady=5, sticky="ew")
        self.en_search.bind("<KeyRelease>", lambda e: self.rechercher_client())
        
        # Boutons
        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=(15,0))
        ttk.Button(btn_frame, text="➕ Ajouter", command=self.ajouter_client, style="Primary.TButton").grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="📋 Consulter", style="Primary.TButton", command=self.ouvrir_fenetre_clients).grid(row=0, column=1, padx=10)
        ttk.Button(btn_frame, text="🔍 Rechercher", command=self.rechercher_client, style="Primary.TButton").grid(row=0, column=2, padx=5)

    def ouvrir_fenetre_clients(self):
        # Vérifie si la fenêtre existe déjà
        if self.win_clients is not None and self.win_clients.winfo_exists():
            self.win_clients.lift()
            return

        # Création de la fenêtre
        self.win_clients = tk.Toplevel(self)
        self.win_clients.title("Liste des clients")
        self.win_clients.geometry("800x400")

        frame = ttk.Frame(self.win_clients, padding=10)
        frame.pack(fill="both", expand=True)

        # Treeview complet
        self.tree_cl = ttk.Treeview(
            frame,
            columns=("id", "nom", "prenom", "telephone", "cin", "adresse", "date_naissance"),
            show="headings")
        self.tree_cl.tag_configure(
            "found",
            background="#E3F2FD")

        for col, width, text in [
            ("id", 50, "ID"),
            ("nom", 100, "Nom"),
            ("prenom", 100, "Prénom"),
            ("telephone", 100, "Téléphone"),
            ("cin", 100, "CIN"),
            ("adresse", 150, "Adresse"),
            ("date_naissance", 100, "Date de naissance")
        ]:
            self.tree_cl.heading(col, text=text)
            self.tree_cl.column(col, width=width)

        self.tree_cl.pack(fill="both", expand=True)
        self.tree_cl.bind("<<TreeviewSelect>>", self.remplir_form_client)

        # Bouton Modifier
        btn_frame = ttk.Frame(self.win_clients, padding=5)
        btn_frame.pack(fill="x")
        ttk.Button(
            btn_frame, text="✏️ Modifier", command=self.modifier_client, style="Primary.TButton"
        ).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑 Supprimer", command=self.supprimer_client).pack(side="left", padx=5)

        def on_close():
            self.tree_cl = None
            self.win_clients.destroy()
            self.win_clients = None
        self.win_clients.protocol("WM_DELETE_WINDOW", on_close)

        # Remplir le Treeview
        self.refresh_clients()

    def remplir_form_client(self, event):
        sel = self.tree_cl.selection()
        if sel:
            data = self.tree_cl.item(sel)["values"]
            self.en_nom.delete(0, tk.END)
            self.en_pre.delete(0, tk.END)
            self.en_telephone.delete(0, tk.END)
            self.en_nom.insert(0, data[1])
            self.en_pre.insert(0, data[2])
            self.en_telephone.insert(0, data[3])

    def ajouter_client(self):
        nom = self.en_nom.get().strip()
        pre = self.en_pre.get().strip()
        telephone = self.en_telephone.get().strip()
        cin = self.en_cin.get().strip()
        adresse = self.en_adresse.get().strip()
        date_naissance = self.en_date_naissance.get().strip()

        if not nom or not pre or not telephone:
            messagebox.showwarning("Champs vides", "Veuillez remplir au moins Nom, Prénom et Téléphone.")
            return
        # Inserer dans DB
        ajouter_client_db(nom, pre, telephone, cin=cin, adresse=adresse, date_naissance=date_naissance)

        if self.tree_cl is not None:
            self.refresh_clients()
        self.charger_clients_combo()


        # Nettoyage des champs
        self.en_nom.delete(0, tk.END)
        self.en_pre.delete(0, tk.END)
        self.en_telephone.delete(0, tk.END)
        self.en_cin.delete(0, tk.END)
        self.en_adresse.delete(0, tk.END)
        self.en_date_naissance.delete(0, tk.END)

        messagebox.showinfo("Succès", "Client ajouté avec succès !")

    def modifier_client(self):
        sel = self.tree_cl.selection()
        if not sel:
            messagebox.showwarning("Veuillez sélectionner un client à modifier.")
            return
        item = self.tree_cl.item(sel[0], "values")
        idc = item[0]
        old_nom = item[1]
        old_pre = item[2]
        old_telephone = item[3]
        old_cin = item[4]
        old_adresse = item[5]
        old_date = item[6]

        win_mod = tk.Toplevel(self)
        win_mod.title("✏️ Modifier le client")
        win_mod.geometry("400x300")
        win_mod.resizable(False, False)
        frame = ttk.Frame(win_mod, padding=10)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Nom :").grid(row=0, column=0, sticky="e")
        en_nom_mod = ttk.Entry(frame); en_nom_mod.grid(row=0, column=1); en_nom_mod.insert(0, old_nom)
        ttk.Label(frame, text="Prénom :").grid(row=1, column=0, sticky="e")
        en_pre_mod = ttk.Entry(frame); en_pre_mod.grid(row=1, column=1); en_pre_mod.insert(0, old_pre)
        ttk.Label(frame, text="Téléphone :").grid(row=2, column=0, sticky="e")
        en_telephone_mod = ttk.Entry(frame); en_telephone_mod.grid(row=2, column=1); en_telephone_mod.insert(0, old_telephone)
        ttk.Label(frame, text="CIN :").grid(row=3, column=0, sticky="e")
        en_cin_mod = ttk.Entry(frame)
        en_cin_mod.grid(row=3, column=1)
        en_cin_mod.insert(0, old_cin)
        ttk.Label(frame, text="Adresse :").grid(row=4, column=0, sticky="e")
        en_adresse_mod = ttk.Entry(frame)
        en_adresse_mod.grid(row=4, column=1)
        en_adresse_mod.insert(0, old_adresse)
        ttk.Label(frame, text="Date de naissance :").grid(row=5, column=0, sticky="e")
        en_date_mod = ttk.Entry(frame)
        en_date_mod.grid(row=5, column=1)
        en_date_mod.insert(0, old_date)

        def enregistrer_modif():
            new_nom = en_nom_mod.get().strip()
            new_pre = en_pre_mod.get().strip()
            new_telephone = en_telephone_mod.get().strip()
            new_cin = en_cin_mod.get().strip()
            new_adresse = en_adresse_mod.get().strip()
            new_date = en_date_mod.get().strip()
            if not new_nom or not new_pre or not new_telephone:
                messagebox.showwarning("Champs vides", "Veuillez remplir tous les champs.")
                return
            con = connecter()
            cur = con.cursor()
            cur.execute("""
                UPDATE Client
                SET nom=?, prenom=?, telephone=?, cin=?, adresse=?, date_naissance=?
                WHERE id_client=?
            """, (new_nom, new_pre, new_telephone, new_cin, new_adresse, new_date, idc))
            con.commit()
            con.close()

            self.refresh_clients()
            self.charger_clients_combo()
            win_mod.destroy()
            messagebox.showinfo("Succès", "Client modifié avec succès.")

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="💾 Enregistrer", command=enregistrer_modif).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="❌ Annuler", command=win_mod.destroy).grid(row=0, column=1, padx=5)

    def supprimer_client(self):
        if not hasattr(self, "tree_cl"):
            return
        sel = self.tree_cl.selection()
        if sel:
            idc = self.tree_cl.item(sel)["values"][0]
            if not messagebox.askyesno("Confirmation", "Supprimer ce client ?"):
                return
            con = connecter()
            cur = con.cursor()
            cur.execute("DELETE FROM Client WHERE id_client=?", (idc,))
            con.commit()
            con.close()
            self.refresh_clients()
            self.charger_clients_combo()

    def rechercher_client(self):
        texte = self.en_search.get().strip()

        # Ouvrir la fenêtre si elle n’est pas ouverte
        if self.win_clients is None or not self.win_clients.winfo_exists():
            self.ouvrir_fenetre_clients()

        if self.tree_cl is None:
            return

        # Nettoyer le tableau
        for i in self.tree_cl.get_children():
            self.tree_cl.delete(i)

        if not texte:
            self.refresh_clients()
            return

        rows = rechercher_client_db(texte)

        if not rows:
            messagebox.showinfo("Recherche", "❌ Aucun client trouvé.")
            return

        for r in rows:
            self.tree_cl.insert("", "end", values=r, tags=("found",))


    def charger_chambres_libres_combo(self):
        self.chambres_libres = lister_chambres_libres_db()  # [('01',), ('03',), ('101',)]
        
        if not self.chambres_libres:
            self.cb_chambre["values"] = []
            self.cb_chambre.set('')
            return

        nums = [str(ch[0]) for ch in self.chambres_libres]  # ou f"{ch[0]:02d}" si INTEGER
        self.cb_chambre["values"] = nums
        self.cb_chambre.current(0)

    def charger_clients_combo(self):
        rows = lister_clients_db()
        self.clients_map = {}
        labels = []
        for r in rows:
            id_client = r[0]
            nom = r[1]
            prenom = r[2]

            label = f"{id_client} - {nom} {prenom}"
            self.clients_map[label] = id_client
            labels.append(label)

        if hasattr(self, "cb_client"):
            self.cb_client["values"] = labels
    #  Réservations
    def creer_reservation(self):
        client_label = self.cb_client.get().strip()
        num_chambre = self.cb_chambre.get().strip()
        d1 = self.en_d1.get().strip()
        d2 = self.en_d2.get().strip()

        if not client_label or not num_chambre or not d1 or not d2:
            messagebox.showwarning("Erreur", "Veuillez remplir tous les champs de réservation.")
            return

        # Récupérer id_client
        if client_label not in self.clients_map:
            messagebox.showwarning("Erreur", "Client invalide.")
            return
        id_client = self.clients_map[client_label]

        # Validation des dates
        try:
            date_deb = datetime.strptime(d1, "%Y-%m-%d").date()
            date_fin = datetime.strptime(d2, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Erreur", "Format de date invalide (AAAA-MM-JJ).")
            return

        if date_fin < date_deb:
            messagebox.showwarning("Erreur", "La date de fin doit être ≥ à la date de début.")
            return

        if date_fin < date.today():
            messagebox.showwarning("Erreur", "Impossible de réserver dans le passé.")
            return

        # Déterminer le statut initial
        statut = "en_attente" if date_deb <= date.today() else "future"

        # Ajouter la réservation (dates ISO propres)
        reserver_chambre_db(
            id_client,
            int(num_chambre),
            date_deb.isoformat(),
            date_fin.isoformat(),
            statut
        )

        # Rafraîchir les vues admin
        self.refresh_chambres()
        self.refresh_demandes()
        self.refresh_reservations()
        self.refresh_futures()
        self.charger_chambres_libres_combo()

        # Reset champs
        self.cb_chambre.set("")
        self.en_d1.delete(0, tk.END)
        self.en_d2.delete(0, tk.END)

        messagebox.showinfo("Succès", "Demande de réservation enregistrée avec succès.")
        
        #  RESERVATION 
    def widgets_res(self):
           #  DEMANDES EN ATTENTE 
        dem_frame = ttk.LabelFrame(self.tab_res, text="🔔 Demandes clients en attente de validation", padding=10)
        dem_frame.pack(fill="both", expand=True, padx=20, pady=5)

        cols_dem = ("ID", "Client", "Chambre", "Début", "Fin")
        self.tree_demandes = ttk.Treeview(dem_frame, columns=cols_dem, show="headings", height=5)
        for col in cols_dem:
            self.tree_demandes.heading(col, text=col)
            self.tree_demandes.column(col, anchor="center", width=120)
        self.tree_demandes.pack(fill="both", expand=True)

        btn_dem = ttk.Frame(dem_frame)
        btn_dem.pack(fill="x", pady=5)
        ttk.Button(btn_dem, text="✅ Accepter", command=lambda: self.valider_reservation_admin(accepter=True)).pack(side="left", padx=5)
        ttk.Button(btn_dem, text="❌ Refuser", command=lambda: self.valider_reservation_admin(accepter=False)).pack(side="left", padx=5)

        #  RESERVATIONS EN COURS 
        hist_frame = ttk.LabelFrame(self.tab_res, text="📋 Réservations en cours (Occupées)", padding=10)
        hist_frame.pack(fill="both", expand=True, padx=20, pady=5)

        cols_hist = ("ID", "Client", "Chambre", "Début", "Fin")
        self.tree_res = ttk.Treeview(hist_frame, columns=cols_hist, show="headings", height=5)
        for c in cols_hist:
            self.tree_res.heading(c, text=c)
            self.tree_res.column(c, width=100, anchor="center")
        self.tree_res.pack(fill="both", expand=True)

        ttk.Button(hist_frame, text="🔓 Libérer la chambre", command=self.liberer_depuis_reservation).pack(pady=5)

        #  FUTURES RÉSERVATIONS 
        future_frame = ttk.LabelFrame(self.tab_res, text="📅 Futures réservations", padding=10)
        future_frame.pack(fill="both", expand=True, padx=20, pady=5)

        cols_future = ("ID", "Client", "Chambre", "Début", "Fin")
        self.tree_future = ttk.Treeview(future_frame, columns=cols_future, show="headings", height=5)
        for c in cols_future:
            self.tree_future.heading(c, text=c)
            self.tree_future.column(c, width=100, anchor="center")
        self.tree_future.pack(fill="both", expand=True)

        # Chargement initial 
        self.refresh_demandes()
        self.refresh_reservations()
        self.refresh_futures()
        self.refresh_chambres()
        self.refresh_stats()

    #  Valider / Refuser réservation 
    def valider_reservation_admin(self, accepter=True):
        sel = self.tree_demandes.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une demande.")
            return

        id_res = self.tree_demandes.item(sel[0])["values"][0]

        con = connecter()
        cur = con.cursor()

        if accepter:
            today = date.today().isoformat()
            cur.execute("SELECT date_debut, num_chambre FROM Reservation WHERE id_res=?", (id_res,))
            d1, num_ch = cur.fetchone()

            if d1 > today:
                new_statut = "future"
                # chambre devient réservée
                cur.execute(
                    "UPDATE Chambre SET statut='reservée' WHERE num_chambre=?",
                    (num_ch,)
                )
            else:
                new_statut = "validee"
                # chambre devient occupée
                cur.execute(
                    "UPDATE Chambre SET statut='occupée' WHERE num_chambre=?",
                    (num_ch,)
                )

            cur.execute("""
                UPDATE Reservation
                SET statut=?
                WHERE id_res=?
            """, (new_statut, id_res))

            #  mettre à jour le statut de la chambre
            cur.execute("""
                UPDATE Chambre
                SET statut=?
                WHERE num_chambre = (
                    SELECT num_chambre FROM Reservation WHERE id_res=?
                )
            """, ("occupée" if new_statut == "validee" else "reservée", id_res))


        else:
            cur.execute("DELETE FROM Reservation WHERE id_res=?", (id_res,))

        con.commit()
        con.close()

        self.refresh_demandes()
        self.refresh_reservations()
        self.refresh_futures()

    def liberer_depuis_reservation(self):
        sel = self.tree_res.selection()
        if not sel:
            messagebox.showwarning("Veuillez sélectionner une réservation.")
            return

        # Récupérer les valeurs sélectionnées
        id_res, nom, num_chambre, d1, d2 = self.tree_res.item(sel[0], "values")
        # Empêcher la libération avant la fin de la réservation
        today = date.today()
        if datetime.strptime(d2, "%Y-%m-%d").date() > today:
            messagebox.showwarning(
                "Action refusée",
                "La réservation n'est pas encore terminée."
            )
            return

        if not messagebox.askyesno(
            "Confirmation",
            f"Libérer la chambre {num_chambre} pour le client {nom} ?"
        ):
            return

        # Récupérer prix et type de la chambre
        con = connecter()
        cur = con.cursor()
        cur.execute(
            "SELECT prix_nuit, type FROM Chambre WHERE num_chambre=?",
            (num_chambre,)
        )
        res = cur.fetchone()
        if not res:
            con.close()
            messagebox.showerror("Erreur", "Chambre introuvable")
            return
        prix_nuit, type_ch = res

        # Calculer le montant de la réservation
        try:
            d_debut = datetime.strptime(d1, "%Y-%m-%d").date()
            d_fin = datetime.strptime(d2, "%Y-%m-%d").date()
            nb_jours = (d_fin - d_debut).days + 1
            montant = nb_jours * prix_nuit
        except Exception:
            montant = 0

        # Enregistrer la facture
        enregistrer_facture_chambre(num_chambre, type_ch, d1, d2, montant)

        # Libérer la chambre et supprimer la réservation
        liberer_chambre_db(num_chambre)
        con = connecter()
        cur = con.cursor()
        cur.execute("""
            UPDATE Reservation
            SET statut='expiree'
            WHERE id_res=?
        """, (id_res,))
        con.commit()
        con.close()
        self.tree_res.delete(sel[0])

        # Actualiser toutes les listes
        self.refresh_chambres()
        self.refresh_reservations()
        self.refresh_futures()
        self.refresh_stats()

        messagebox.showinfo(
            "Facturation",
            f"Chambre libérée avec succès\nMontant : {montant:.2f} DT"
        )

    def setup_tab_demandes(self):
        """Configuration visuelle de l'onglet Demandes"""
        btn_frame = ttk.Frame(self.tab_demandes)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="✅ Accepter", command=lambda: self.valider_reservation_admin(True)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="❌ Refuser", command=lambda: self.valider_reservation_admin(False)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Actualiser", command=self.refresh_demandes).pack(side="left", padx=5)

        # Remplissage initial des demandes
        self.refresh_demandes()

    def refresh_demandes(self):
        if not hasattr(self, "tree_demandes"):
            return

        for i in self.tree_demandes.get_children():
            self.tree_demandes.delete(i)

        con = connecter()
        cur = con.cursor()

        cur.execute("""
            SELECT r.id_res,
                c.nom || ' ' || c.prenom,
                r.num_chambre,
                r.date_debut,
                r.date_fin
            FROM Reservation r
            JOIN Client c ON c.id_client = r.id_client
            WHERE r.statut = 'en_attente'
            ORDER BY r.date_debut
        """)

        rows = cur.fetchall()
        con.close()

        for id_res, client, num_chambre, d1, d2 in rows:
            self.tree_demandes.insert("", "end",
                values=(id_res, client, num_chambre, d1, d2)
            )

    def refresh_reservations(self):
        if not hasattr(self, "tree_res"):
            return

        for i in self.tree_res.get_children():
            self.tree_res.delete(i)

        today = date.today().isoformat()
        con = connecter()
        cur = con.cursor()

        # futures → validées quand la date arrive
        cur.execute("""
            SELECT id_res, num_chambre FROM Reservation
            WHERE statut='future' AND date_debut <= ?
        """, (today,))
        rows = cur.fetchall()

        for id_res, num_ch in rows:
            cur.execute("UPDATE Reservation SET statut='validee' WHERE id_res=?", (id_res,))
            cur.execute("UPDATE Chambre SET statut='occupée' WHERE num_chambre=?", (num_ch,))

        con.commit()

        # Marquer les réservations expirées
        cur.execute("""
            UPDATE Reservation
            SET statut='expiree'
            WHERE statut='validee'
            AND date_fin < ?
        """, (today,))
        con.commit()


        cur.execute("""
            SELECT r.id_res,
                c.nom || ' ' || c.prenom,
                r.num_chambre,
                r.date_debut,
                r.date_fin
            FROM Reservation r
            JOIN Client c ON c.id_client = r.id_client
            WHERE r.statut IN ('validee')
            ORDER BY r.date_debut
        """)

        rows = cur.fetchall()
        con.close()

        for r in rows:
            self.tree_res.insert("", "end", values=r)

    def refresh_futures(self):
        if not hasattr(self, "tree_future"):
            return

        for i in self.tree_future.get_children():
            self.tree_future.delete(i)

        today = date.today().isoformat()
        con = connecter()
        cur = con.cursor()

        cur.execute("""
            SELECT r.id_res,
                c.nom || ' ' || c.prenom,
                r.num_chambre,
                r.date_debut,
                r.date_fin
            FROM Reservation r
            JOIN Client c ON c.id_client = r.id_client
            WHERE r.statut='future'
            AND date_debut > ?
            ORDER BY r.date_debut
        """, (today,))

        rows = cur.fetchall()
        con.close()

        for r in rows:
            self.tree_future.insert("", "end", values=r)


    #  Stats 
    def widgets_stats(self):
        frame = ttk.LabelFrame(
            self.tab_stat,
            text="📊 Statistiques générales",
            padding=15
        )
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.tree_stats = ttk.Treeview(
        frame,
        columns=("label", "valeur", "pourcentage"),
        show="headings",
        height=12
        )

        self.tree_stats.heading("label", text="Indicateur")
        self.tree_stats.heading("valeur", text="Valeur")
        self.tree_stats.heading("pourcentage", text="%")
        self.tree_stats.column("label", width=260)
        self.tree_stats.column("valeur", width=120, anchor="center")
        self.tree_stats.column("pourcentage", width=90, anchor="center")
        self.tree_stats.pack(fill="both", expand=True, pady=10)

        ttk.Button(
            frame,
            text="🔄 Actualiser",
            command=self.refresh_stats
        ).pack(pady=5)

        # Chargement initial
        self.refresh_stats()

    def afficher_statistiques(self):
        con = connecter()
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM Facture_Chambre")
        nb = cur.fetchone()[0]
        if nb == 0:
            self.lbl_stat.config(
                text=" Aucune facture enregistrée.\n Libérez des chambres pour générer des statistiques."
            )
            con.close()
            return
        cur.execute("SELECT SUM(montant) FROM Facture_Chambre")
        total = cur.fetchone()[0]
        cur.execute("""
            SELECT type_chambre, SUM(montant)
            FROM Facture_Chambre
            GROUP BY type_chambre
        """)
        rows = cur.fetchall()
        con.close()
        texte = f"💰 Total : {total:.2f} DT\n\n"
        texte += "📊 Par type de chambre :\n"
        for t, m in rows:
            texte += f"• {t} : {m:.2f} DT\n"

        self.lbl_stat.config(text=texte)

    #  Refresh global 
    def refresh_all(self):
        self.refresh_chambres()
        self.refresh_clients()
        self.refresh_reservations()
        self.charger_clients_combo()
        self.charger_chambres_libres_combo()

    def refresh_chambres(self):
        if not hasattr(self, "tree_ch"):
            return
        if not self.tree_ch.winfo_exists():
            return

        for i in self.tree_ch.get_children():
            self.tree_ch.delete(i)

        chambres = lister_chambres_db()
        for ch in chambres:
            statut = ch[3]
            self.tree_ch.insert("", "end", values=ch, tags=(statut,))

    def refresh_clients(self):
        if self.tree_cl is None:
            return

        for i in self.tree_cl.get_children():
            self.tree_cl.delete(i)

        con = connecter()
        cur = con.cursor()
        cur.execute("""
            SELECT id_client, nom, prenom, telephone, cin, adresse, date_naissance
            FROM Client
        """)
        rows = cur.fetchall()
        con.close()

        for r in rows:
            self.tree_cl.insert("", "end", values=r)

    def refresh_stats(self):
        if not hasattr(self, "tree_stats"):
            return

        # Nettoyer le tableau
        for i in self.tree_stats.get_children():
            self.tree_stats.delete(i)

        con = connecter()
        cur = con.cursor()

        # Réservations:
        cur.execute("SELECT COUNT(*) FROM Reservation")
        total_res = cur.fetchone()[0]

        cur.execute("""SELECT COUNT(*)
            FROM Reservation r
            JOIN Client c ON c.id_client = r.id_client
            WHERE r.statut='en_attente'
        """)
        attente = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Reservation WHERE statut='validee'")
        validees = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Reservation WHERE statut='future'")
        futures = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Reservation WHERE statut='expiree'")
        expiree = cur.fetchone()[0]

        # -------- Chambres --------
        cur.execute("SELECT COUNT(*) FROM Chambre")
        total_ch = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Chambre WHERE statut='libre'")
        libres = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Chambre WHERE statut='demandée'")
        demandees = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Chambre WHERE statut='reservée'")
        reservees = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Chambre WHERE statut='occupée'")
        occupees = cur.fetchone()[0]

        # -------- Chiffre d'affaires --------
        cur.execute("SELECT IFNULL(SUM(montant), 0) FROM Facture_Chambre")
        ca = cur.fetchone()[0]

        con.close()

        # Fonction pour calculer %
        def pct(val, total):
            return f"{(val / total * 100):.1f}%" if total > 0 else "0%"

        # -------- Données PRO --------
        data = [
            ("📌 Total réservations", total_res, "info"),
            ("⏳ Réservations en attente", attente, "warn"),
            ("✅ Réservations validées", validees, "ok"),
            ("📅 Réservations futures", futures, "warn"),
            ("⌛ Réservations expirées", expiree, "danger"),
            ("🏨 Total chambres", total_ch, "info"),
            ("🟢 Chambres libres", libres, "ok"),
            ("🟠 Chambres demandées", demandees, "warn"),
            ("🔵 Chambres réservées", reservees, "info"),
            ("🔴 Chambres occupées", occupees, "danger"),
            ("💰 Chiffre d'affaires (DT)", f"{ca:.2f}", "ok")
        ]

        # Insertion dans le tableau
        for ind, val, tag in data:
            try:
                pourc = f"{(val / total_res) * 100:.1f}%" if total_res and isinstance(val, int) else "-"
            except:
                pourc = "-"

            self.tree_stats.insert(
                "", "end",
                values=(ind, val, pourc),
                tags=(tag,)
            )


def lancer_admin():
    app = HotelApp()
    app.mainloop()
        
def lancer_user(id_client):
    root = tk.Tk()
    root.title("Espace Utilisateur - Consultation")
    root.geometry("800x450")

    ttk.Label(root, text="Bienvenue - Consultation des chambres", font=("Segoe UI", 14, "bold")).pack(pady=10)
    # UNE SEULE FOIS : Création du tableau
    table = ttk.Treeview(root, columns=("num", "type", "prix", "statut"), show="headings")
    table.heading("num", text="Numéro")
    table.heading("type", text="Type")
    table.heading("prix", text="Prix / nuit")
    table.heading("statut", text="Statut")
    table.pack(fill="both", expand=True, padx=20, pady=10)
    # UNE SEULE FOIS : Création du bouton
    # On utilise 'table' qui a été défini juste au-dessus
    btn_reserver = ttk.Button(root, text="📅 Réserver", 
                              command=lambda: reserver_payer_user(id_client, table))
    btn_reserver.pack(pady=10)

    # REMPLISSAGE (Une seule boucle !)
    for r in lister_chambres_db():
        table.insert("", "end", values=r)

    root.mainloop()

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - Gestion Hôtel")
        self.geometry("350x250")
        self.resizable(False, False)
        ttk.Label(
            self,
            text="Connexion",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=15)

        ttk.Label(self, text="Username").pack()
        self.en_user = ttk.Entry(self)
        self.en_user.pack(pady=5)
        ttk.Label(self, text="Mot de passe").pack()
        self.en_pass = ttk.Entry(self, show="*")
        self.en_pass.pack(pady=5)
        ttk.Button(
            self,
            text="Se connecter",
            command=self.login
        ).pack(pady=15)
        ttk.Button(
            self,
            text="Créer un compte",
            command=lambda: SignupWindow(self)
        ).pack()

    def login(self):
        res = verifier_login(
            self.en_user.get(),
            self.en_pass.get()
        )
        if not res:
            messagebox.showerror("Erreur", "Identifiants incorrects")
            return
        id_client, role = res   # ← LIGNE CLÉ
        self.destroy()
        if role == "admin":
            lancer_admin()
        else:
            lancer_user(id_client)

class SignupWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Inscription")
        self.geometry("400x520")
        self.resizable(False, False)

        ttk.Label(self, text="Créer un compte", font=("Segoe UI", 14, "bold")).pack(pady=10)

        self.add_field("Nom")
        self.en_nom = self.entry
        self.add_field("Prénom")
        self.en_prenom = self.entry
        self.add_field("CIN")
        self.en_cin = self.entry
        self.add_field("Téléphone")
        self.en_telephone = self.entry
        self.add_field("Adresse")
        self.en_adresse = self.entry
        self.add_field("Date de naissance (YYYY-MM-DD)")
        self.en_date = self.entry
        self.add_field("Nom d'utilisateur")
        self.en_user = self.entry
        self.add_field("Mot de passe", show="*")
        self.en_pass = self.entry
        ttk.Button(self, text="Créer le compte", command=self.signup).pack(pady=15)

    def add_field(self, label_text, show=None):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(frame, text=label_text).pack(anchor="w")
        self.entry = ttk.Entry(frame, show=show)
        self.entry.pack(fill="x")

    def signup(self): 
        #Vérification champs obligatoires
        username = self.en_user.get().strip()
        password = self.en_pass.get().strip()
        nom = self.en_nom.get().strip()
        prenom = self.en_prenom.get().strip()
        cin = self.en_cin.get().strip()
        telephone = self.en_telephone.get().strip()
        adresse = self.en_adresse.get().strip()
        date_naissance = self.en_date.get().strip()

        # Vérification que tous les champs sont remplis
        if not all([username, password, nom, prenom, cin, telephone, adresse, date_naissance]):
            messagebox.showwarning("Champs obligatoires", "Veuillez remplir tous les champs.")
            return
        # Vérification format date
        try:
            datetime.strptime(date_naissance, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Format incorrect", "La date de naissance doit être YYYY-MM-DD.")
            return
        # Vérification téléphone
        if not telephone.isdigit():
            messagebox.showwarning("Téléphone incorrect", "Le numéro de téléphone doit contenir uniquement des chiffres.")
            return
        # Vérification CIN unique
        con = connecter()
        cur = con.cursor()
        cur.execute("SELECT id_client FROM Client WHERE cin=?", (cin,))
        if cur.fetchone():
            con.close()
            messagebox.showerror("Erreur", "Ce CIN est déjà utilisé.")
            return
        con.close()
        # Création compte via ta fonction inscrire_user
        success, msg = inscrire_user(username, password, nom, prenom, cin, telephone, adresse, date_naissance)

        if success:
            messagebox.showinfo("Succès", msg)
            self.destroy()
        else:
            messagebox.showerror("Erreur", msg)
def reserver_payer_user(id_client, table):
    # 1. On récupère la sélection
    sel = table.selection()
    
    # Sécurité si le clic n'est pas bien détecté
    if not sel:
        item_focus = table.focus()
        if item_focus:
            sel = (item_focus,)
        else:
            messagebox.showwarning("Sélection", "Veuillez cliquer sur une chambre dans la liste.")
            return

    # 2. On récupère les infos de la chambre
    item_id = sel[0]
    valeurs = table.item(item_id)["values"]
    num_chambre, type_ch, prix_nuit, statut = valeurs

    if str(statut).lower() != "libre":
        messagebox.showwarning("Indisponible", "Cette chambre n'est pas libre.")
        return

    # 3. Création de la fenêtre
    win = tk.Toplevel()
    win.title(f"Réservation Chambre {num_chambre}")
    win.geometry("380x550")

    ttk.Label(win, text=f"Chambre {num_chambre} ({type_ch})", font=("Arial", 11, "bold")).pack(pady=10)

    # Champs Dates
    ttk.Label(win, text="Date début (AAAA-MM-JJ)").pack()
    en_d1 = ttk.Entry(win)
    en_d1.insert(0, date.today().isoformat())
    en_d1.pack(pady=2)

    ttk.Label(win, text="Date fin (AAAA-MM-JJ)").pack()
    en_d2 = ttk.Entry(win)
    en_d2.pack(pady=2)


    # --- FONCTION INTERNE 2 : Confirmer ---
    def confirmer():
        d1, d2 = en_d1.get().strip(), en_d2.get().strip()

        if not d1 or not d2:
            messagebox.showerror("Erreur", "Veuillez remplir les dates.")
            return

        # Vérification dates
        try:
            date_deb = datetime.strptime(d1, "%Y-%m-%d").date()
            date_fin = datetime.strptime(d2, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Erreur", "Format de date invalide (AAAA-MM-JJ).")
            return

        if date_fin < date_deb:
            messagebox.showerror("Erreur", "La date de fin doit être ≥ à la date de début.")
            return

        try:
            con = connecter()
            cur = con.cursor()

            # 1️⃣ insérer la demande (en attente)
            cur.execute("""
                INSERT INTO Reservation (id_client, num_chambre, date_debut, date_fin, statut) 
                VALUES (?, ?, ?, ?, 'en_attente')
            """, (id_client, num_chambre, d1, d2))

            # 2️⃣ mettre la chambre en état "demandée"
            cur.execute("""
                UPDATE Chambre SET statut='demandée' WHERE num_chambre=?
            """, (num_chambre,))

            con.commit()
            con.close()

            messagebox.showinfo("Succès", "Demande envoyée à l'admin !")
            win.destroy()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur SQL : {e}")


    # 4. Bouton de validation
    ttk.Button(win, text="Confirmer la demande", command=confirmer).pack(pady=20)
# ------ Main ------
if __name__ == "__main__":
    initialiser_bd()
    migration_client_table()
    con = connecter()
    cur = con.cursor()
    try:
        cur.execute("ALTER TABLE Reservation ADD COLUMN statut TEXT DEFAULT 'en_attente'")
        con.commit()
    except:
        pass # Si la colonne existe déjà, on ne fait rien
    con.close()
    creer_compte(
            "admin",
            "admin123",
            "admin",)   
    login = LoginWindow()
    login.mainloop()

