"""
Mini-projet Python POO : Gestion des étudiants
Version simple avec interface Tkinter propre + sauvegarde JSON.

Cette version reste volontairement facile à expliquer :
- une classe Etudiant ;
- une liste d'objets Etudiant ;
- des fonctions reliées aux boutons Tkinter ;
- une sauvegarde et un chargement avec JSON.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox


# Le fichier JSON sera créé dans le même dossier que ce script Python.
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
FICHIER_JSON = os.path.join(DOSSIER_SCRIPT, "etudiants.json")


class Etudiant:
    """Classe qui représente un étudiant."""

    def __init__(self, nom, prenom, age, notes=None):
        self.nom = nom
        self.prenom = prenom
        self.age = age

        if notes is None:
            self.notes = []
        else:
            self.notes = notes

    def ajouter_note(self, note):
        """Ajoute une note à l'étudiant."""
        self.notes.append(note)

    def calculer_moyenne(self):
        """Calcule la moyenne. Retourne None si aucune note n'existe."""
        if len(self.notes) == 0:
            return None
        return sum(self.notes) / len(self.notes)

    def resultat(self):
        """Indique si l'étudiant est admis ou non."""
        moyenne = self.calculer_moyenne()

        if moyenne is None:
            return "Sans note"
        if moyenne >= 10:
            return "Admis"
        return "Non admis"

    def notes_en_texte(self):
        """Transforme la liste des notes en texte lisible."""
        if len(self.notes) == 0:
            return "Aucune"
        return " | ".join(str(note) for note in self.notes)

    def moyenne_en_texte(self):
        """Retourne la moyenne en texte."""
        moyenne = self.calculer_moyenne()

        if moyenne is None:
            return "--"
        return f"{moyenne:.2f}/20"

    def afficher_infos(self):
        """Retourne les informations complètes de l'étudiant."""
        return (
            f"Nom : {self.nom}\n"
            f"Prénom : {self.prenom}\n"
            f"Âge : {self.age}\n"
            f"Notes : {self.notes_en_texte()}\n"
            f"Moyenne : {self.moyenne_en_texte()}\n"
            f"Résultat : {self.resultat()}"
        )

    def vers_dictionnaire(self):
        """Convertit l'objet en dictionnaire pour le JSON."""
        return {
            "nom": self.nom,
            "prenom": self.prenom,
            "age": self.age,
            "notes": self.notes
        }

    @staticmethod
    def depuis_dictionnaire(donnees):
        """Crée un étudiant depuis un dictionnaire JSON."""
        return Etudiant(
            donnees["nom"],
            donnees["prenom"],
            donnees["age"],
            donnees.get("notes", [])
        )


# Liste principale du programme : elle contient des objets Etudiant.
etudiants = []


# -----------------------------
# Fonctions utiles
# -----------------------------


def afficher_message(texte, couleur="#334155"):
    """Affiche un message en bas de l'interface."""
    label_message.config(text=texte, fg=couleur)


def lire_champs():
    """Lit les valeurs saisies par l'utilisateur."""
    nom = entree_nom.get().strip().title()
    prenom = entree_prenom.get().strip().title()
    age = entree_age.get().strip()
    note = entree_note.get().strip().replace(",", ".")
    return nom, prenom, age, note


def trouver_index_etudiant(nom, prenom):
    """Recherche un étudiant par nom et prénom. Retourne son index ou None."""
    for index, etudiant in enumerate(etudiants):
        if etudiant.nom == nom and etudiant.prenom == prenom:
            return index
    return None


def index_selectionne():
    """Retourne l'index de l'étudiant sélectionné dans le tableau."""
    selection = tableau.selection()

    if len(selection) == 0:
        return None

    # Le iid du tableau correspond à l'index dans la liste etudiants.
    return int(selection[0])


def obtenir_index_cible():
    """
    Retourne l'étudiant à utiliser.
    Priorité : étudiant sélectionné dans le tableau.
    Sinon : recherche avec nom + prénom écrits dans les champs.
    """
    index = index_selectionne()

    if index is not None:
        return index

    nom, prenom, _, _ = lire_champs()

    if nom == "" or prenom == "":
        return None

    return trouver_index_etudiant(nom, prenom)


def actualiser_tableau():
    """Met à jour le tableau des étudiants."""
    for ligne in tableau.get_children():
        tableau.delete(ligne)

    for index, etudiant in enumerate(etudiants):
        resultat = etudiant.resultat()

        if resultat == "Admis":
            tag = "admis"
        elif resultat == "Non admis":
            tag = "non_admis"
        else:
            tag = "sans_note"

        tableau.insert(
            "",
            "end",
            iid=str(index),
            values=(
                etudiant.nom,
                etudiant.prenom,
                etudiant.age,
                len(etudiant.notes),
                etudiant.moyenne_en_texte(),
                resultat
            ),
            tags=(tag,)
        )

    actualiser_statistiques()


def actualiser_statistiques():
    """Met à jour les petits chiffres en haut de l'interface."""
    total = len(etudiants)
    nb_admis = 0
    nb_non_admis = 0
    moyennes = []

    for etudiant in etudiants:
        moyenne = etudiant.calculer_moyenne()

        if moyenne is not None:
            moyennes.append(moyenne)

            if moyenne >= 10:
                nb_admis += 1
            else:
                nb_non_admis += 1

    if len(moyennes) == 0:
        moyenne_classe = "--"
    else:
        moyenne_classe = f"{sum(moyennes) / len(moyennes):.2f}/20"

    label_total.config(text=str(total))
    label_moyenne_classe.config(text=moyenne_classe)
    label_admis.config(text=str(nb_admis))
    label_non_admis.config(text=str(nb_non_admis))


def afficher_details(etudiant):
    """Affiche les informations d'un étudiant dans le cadre de détails."""
    zone_details.config(state="normal")
    zone_details.delete("1.0", tk.END)

    if etudiant is not None:
        zone_details.insert(tk.END, etudiant.afficher_infos())

    zone_details.config(state="disabled")


def remplir_champs(etudiant):
    """Remplit automatiquement les champs avec l'étudiant sélectionné."""
    entree_nom.delete(0, tk.END)
    entree_prenom.delete(0, tk.END)
    entree_age.delete(0, tk.END)

    entree_nom.insert(0, etudiant.nom)
    entree_prenom.insert(0, etudiant.prenom)
    entree_age.insert(0, str(etudiant.age))


def vider_champs():
    """Vide les champs de saisie et la zone de détails."""
    entree_nom.delete(0, tk.END)
    entree_prenom.delete(0, tk.END)
    entree_age.delete(0, tk.END)
    entree_note.delete(0, tk.END)
    tableau.selection_remove(tableau.selection())
    afficher_details(None)
    afficher_message("Champs vidés.", "#2563eb")


# -----------------------------
# Actions des boutons
# -----------------------------


def ajouter_etudiant():
    """Ajoute un étudiant dans la liste."""
    nom, prenom, age, _ = lire_champs()

    if nom == "" or prenom == "" or age == "":
        afficher_message("Veuillez remplir le nom, le prénom et l'âge.", "#dc2626")
        return

    if not age.isdigit():
        afficher_message("L'âge doit être un nombre entier.", "#dc2626")
        return

    if trouver_index_etudiant(nom, prenom) is not None:
        afficher_message("Cet étudiant existe déjà.", "#dc2626")
        return

    etudiant = Etudiant(nom, prenom, int(age))
    etudiants.append(etudiant)

    actualiser_tableau()
    afficher_details(etudiant)
    afficher_message(f"Étudiant {nom} {prenom} ajouté avec succès.", "#16a34a")


def rechercher_etudiant():
    """Recherche un étudiant avec le nom et le prénom."""
    nom, prenom, _, _ = lire_champs()

    if nom == "" or prenom == "":
        afficher_message("Entrez le nom et le prénom pour rechercher.", "#dc2626")
        return

    index = trouver_index_etudiant(nom, prenom)

    if index is None:
        afficher_message("Étudiant introuvable.", "#dc2626")
        return

    tableau.selection_set(str(index))
    tableau.focus(str(index))
    tableau.see(str(index))
    afficher_details(etudiants[index])
    afficher_message("Étudiant trouvé.", "#16a34a")


def ajouter_note():
    """Ajoute une note à l'étudiant sélectionné ou recherché."""
    index = obtenir_index_cible()

    if index is None:
        afficher_message("Sélectionnez un étudiant ou entrez son nom et prénom.", "#dc2626")
        return

    _, _, _, note_texte = lire_champs()

    if note_texte == "":
        afficher_message("Entrez une note.", "#dc2626")
        return

    try:
        note = float(note_texte)
    except ValueError:
        afficher_message("La note doit être un nombre.", "#dc2626")
        return

    if note < 0 or note > 20:
        afficher_message("La note doit être comprise entre 0 et 20.", "#dc2626")
        return

    etudiant = etudiants[index]
    etudiant.ajouter_note(note)
    entree_note.delete(0, tk.END)

    actualiser_tableau()
    tableau.selection_set(str(index))
    afficher_details(etudiant)
    afficher_message("Note ajoutée avec succès.", "#16a34a")


def afficher_moyenne():
    """Affiche la moyenne de l'étudiant choisi."""
    index = obtenir_index_cible()

    if index is None:
        afficher_message("Sélectionnez un étudiant.", "#dc2626")
        return

    etudiant = etudiants[index]
    moyenne = etudiant.calculer_moyenne()
    afficher_details(etudiant)

    if moyenne is None:
        afficher_message("Cet étudiant n'a pas encore de note.", "#dc2626")
    else:
        afficher_message(f"Moyenne : {moyenne:.2f}/20", "#2563eb")


def voir_resultat():
    """Affiche le résultat de l'étudiant choisi."""
    index = obtenir_index_cible()

    if index is None:
        afficher_message("Sélectionnez un étudiant.", "#dc2626")
        return

    etudiant = etudiants[index]
    afficher_details(etudiant)
    afficher_message(f"Résultat : {etudiant.resultat()}", "#2563eb")


def supprimer_etudiant():
    """Supprime l'étudiant choisi."""
    index = obtenir_index_cible()

    if index is None:
        afficher_message("Sélectionnez un étudiant à supprimer.", "#dc2626")
        return

    etudiant = etudiants[index]
    reponse = messagebox.askyesno(
        "Confirmation",
        f"Voulez-vous vraiment supprimer {etudiant.nom} {etudiant.prenom} ?"
    )

    if reponse:
        etudiants.pop(index)
        actualiser_tableau()
        afficher_details(None)
        afficher_message("Étudiant supprimé.", "#16a34a")


def sauvegarder_json():
    """Sauvegarde les étudiants dans un fichier JSON."""
    donnees = []

    for etudiant in etudiants:
        donnees.append(etudiant.vers_dictionnaire())

    with open(FICHIER_JSON, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, indent=4, ensure_ascii=False)

    afficher_message("Données sauvegardées dans etudiants.json.", "#16a34a")


def charger_json():
    """Charge les étudiants depuis le fichier JSON."""
    if not os.path.exists(FICHIER_JSON):
        afficher_message("Aucun fichier etudiants.json trouvé.", "#dc2626")
        return

    try:
        with open(FICHIER_JSON, "r", encoding="utf-8") as fichier:
            donnees = json.load(fichier)
    except json.JSONDecodeError:
        afficher_message("Le fichier JSON est incorrect.", "#dc2626")
        return

    etudiants.clear()

    for item in donnees:
        etudiants.append(Etudiant.depuis_dictionnaire(item))

    actualiser_tableau()
    afficher_details(None)
    afficher_message("Données chargées avec succès.", "#16a34a")


def action_selection_tableau(event):
    """Action lancée quand l'utilisateur clique sur une ligne du tableau."""
    index = index_selectionne()

    if index is not None:
        etudiant = etudiants[index]
        remplir_champs(etudiant)
        afficher_details(etudiant)


# -----------------------------
# Interface Tkinter
# -----------------------------

# =====================================================================
# PALETTE DE COULEURS — thème "violet & corail", moderne et coloré
# =====================================================================

COULEUR_FOND = "#f4f1fb"          # lavande très clair (fond général)
COULEUR_CARTE = "#ffffff"         # blanc (fond des cartes)
COULEUR_BLEU = "#4338ca"          # indigo profond (boutons "sérieux")
COULEUR_BLEU_2 = "#3b82f6"        # bleu vif
COULEUR_VIOLET = "#7c3aed"        # violet vif (accent principal)
COULEUR_VIOLET_FONCE = "#4c1d95"  # violet foncé (header)
COULEUR_ROSE = "#ec4899"          # rose/fuchsia (accent secondaire)
COULEUR_VERT = "#16a34a"          # vert succès
COULEUR_ORANGE = "#f59e0b"        # orange chaleureux
COULEUR_ROUGE = "#ef4444"         # rouge alerte
COULEUR_GRIS = "#6b7280"          # gris neutre
COULEUR_TEXTE = "#1e1b2e"         # texte principal (presque noir violet)


def eclaircir_couleur(couleur_hex, facteur=0.18):
    """Éclaircit une couleur hexadécimale (pour l'effet de survol des boutons)."""
    couleur_hex = couleur_hex.lstrip("#")
    r, g, b = (int(couleur_hex[i:i + 2], 16) for i in (0, 2, 4))
    r = min(255, int(r + (255 - r) * facteur))
    g = min(255, int(g + (255 - g) * facteur))
    b = min(255, int(b + (255 - b) * facteur))
    return f"#{r:02x}{g:02x}{b:02x}"


fenetre = tk.Tk()
fenetre.title("✨ Gestion des étudiants - Projet Python POO")
fenetre.geometry("1080x700")
fenetre.minsize(980, 640)
fenetre.config(bg=COULEUR_FOND)

# Style global pour le tableau.
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Treeview",
    font=("Segoe UI", 10),
    rowheight=30,
    background="#ffffff",
    fieldbackground="#ffffff",
    borderwidth=0
)
style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 10, "bold"),
    background=COULEUR_VIOLET,
    foreground="white",
    relief="flat",
    padding=6
)
style.map(
    "Treeview.Heading",
    background=[("active", COULEUR_VIOLET_FONCE)]
)
style.map(
    "Treeview",
    background=[("selected", COULEUR_VIOLET)],
    foreground=[("selected", "white")]
)
style.configure("Vertical.TScrollbar", background=COULEUR_VIOLET, troughcolor=COULEUR_FOND, arrowsize=12)

# ---------------------------------------------------------------
# Header en dégradé (violet -> rose) dessiné sur un Canvas.
# ---------------------------------------------------------------

hauteur_header = 95
entete = tk.Canvas(fenetre, height=hauteur_header, highlightthickness=0, bg=COULEUR_FOND)
entete.pack(fill="x")


def dessiner_degrade(canvas, couleur_debut, couleur_fin):
    """Dessine un dégradé horizontal en remplissant le canvas de fines bandes verticales."""
    canvas.update_idletasks()
    largeur = max(canvas.winfo_width(), 1080)

    c1 = couleur_debut.lstrip("#")
    c2 = couleur_fin.lstrip("#")
    r1, g1, b1 = (int(c1[i:i + 2], 16) for i in (0, 2, 4))
    r2, g2, b2 = (int(c2[i:i + 2], 16) for i in (0, 2, 4))

    canvas.delete("degrade")
    pas = 4
    for x in range(0, largeur, pas):
        proportion = x / largeur
        r = int(r1 + (r2 - r1) * proportion)
        g = int(g1 + (g2 - g1) * proportion)
        b = int(b1 + (b2 - b1) * proportion)
        couleur = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_rectangle(x, 0, x + pas, hauteur_header, fill=couleur, outline=couleur, tags="degrade")

    canvas.create_text(
        30, 32, anchor="w", text="🎓  Gestion des étudiants",
        fill="white", font=("Segoe UI", 22, "bold"), tags="degrade"
    )
    canvas.create_text(
        30, 66, anchor="w", text="Projet Python POO  •  interface Tkinter  •  sauvegarde JSON",
        fill="#ede9fe", font=("Segoe UI", 11), tags="degrade"
    )


def redessiner_header(event=None):
    dessiner_degrade(entete, COULEUR_VIOLET_FONCE, COULEUR_ROSE)


entete.bind("<Configure>", redessiner_header)

# Zone principale.
conteneur = tk.Frame(fenetre, bg=COULEUR_FOND)
conteneur.pack(fill="both", expand=True, padx=18, pady=18)


def creer_carte(parent, couleur_accent, **pack_options):
    """Crée une 'carte' blanche avec un fin liseré de couleur en haut, pour un look moderne."""
    enveloppe = tk.Frame(parent, bg=COULEUR_FOND)
    enveloppe.pack(**pack_options)

    liseret = tk.Frame(enveloppe, bg=couleur_accent, height=4)
    liseret.pack(fill="x", side="top")

    carte = tk.Frame(enveloppe, bg=COULEUR_CARTE, padx=18, pady=18,
                      highlightbackground="#e5e0f7", highlightthickness=1)
    carte.pack(fill="both", expand=True)

    return carte


# Colonne gauche : formulaire.
carte_formulaire = creer_carte(conteneur, COULEUR_VIOLET, side="left", fill="y", padx=(0, 15))

label_formulaire = tk.Label(
    carte_formulaire,
    text="📝  Formulaire",
    bg=COULEUR_CARTE,
    fg=COULEUR_VIOLET_FONCE,
    font=("Segoe UI", 15, "bold")
)
label_formulaire.pack(anchor="w", pady=(0, 14))


def creer_label(parent, texte):
    label = tk.Label(parent, text=texte, bg=COULEUR_CARTE, fg=COULEUR_TEXTE, font=("Segoe UI", 10, "bold"))
    label.pack(anchor="w", pady=(6, 3))
    return label


def creer_entree(parent):
    entree = tk.Entry(
        parent, width=31, font=("Segoe UI", 11), relief="flat",
        bg="#f5f3ff", fg=COULEUR_TEXTE,
        highlightthickness=1.5, highlightbackground="#ddd6fe", highlightcolor=COULEUR_VIOLET,
        insertbackground=COULEUR_VIOLET
    )
    entree.pack(anchor="w", ipady=6)
    return entree


creer_label(carte_formulaire, "👤  Nom")
entree_nom = creer_entree(carte_formulaire)

creer_label(carte_formulaire, "👤  Prénom")
entree_prenom = creer_entree(carte_formulaire)

creer_label(carte_formulaire, "🎂  Âge")
entree_age = creer_entree(carte_formulaire)

creer_label(carte_formulaire, "📊  Note à ajouter")
entree_note = creer_entree(carte_formulaire)

label_astuce = tk.Label(
    carte_formulaire,
    text="💡 Astuce : cliquez sur une ligne du tableau\npour remplir le formulaire automatiquement.",
    bg=COULEUR_CARTE,
    fg=COULEUR_GRIS,
    justify="left",
    font=("Segoe UI", 9, "italic")
)
label_astuce.pack(anchor="w", pady=(12, 10))

# Boutons en grille simple.
cadre_boutons = tk.Frame(carte_formulaire, bg=COULEUR_CARTE)
cadre_boutons.pack(fill="x", pady=(5, 0))


def creer_bouton(parent, texte, commande, couleur, ligne, colonne):
    couleur_survol = eclaircir_couleur(couleur)

    bouton = tk.Button(
        parent,
        text=texte,
        command=commande,
        bg=couleur,
        fg="white",
        activebackground=couleur_survol,
        activeforeground="white",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2",
        width=15,
        pady=7,
        bd=0
    )
    bouton.grid(row=ligne, column=colonne, padx=4, pady=4, sticky="ew")

    bouton.bind("<Enter>", lambda e, b=bouton, c=couleur_survol: b.config(bg=c))
    bouton.bind("<Leave>", lambda e, b=bouton, c=couleur: b.config(bg=c))

    return bouton


creer_bouton(cadre_boutons, "➕ Ajouter", ajouter_etudiant, COULEUR_VERT, 0, 0)
creer_bouton(cadre_boutons, "🔍 Rechercher", rechercher_etudiant, COULEUR_BLEU_2, 0, 1)
creer_bouton(cadre_boutons, "✏️ Ajouter note", ajouter_note, COULEUR_VIOLET, 1, 0)
creer_bouton(cadre_boutons, "📈 Moyenne", afficher_moyenne, COULEUR_ORANGE, 1, 1)
creer_bouton(cadre_boutons, "🏆 Résultat", voir_resultat, COULEUR_ROSE, 2, 0)
creer_bouton(cadre_boutons, "🗑️ Supprimer", supprimer_etudiant, COULEUR_ROUGE, 2, 1)
creer_bouton(cadre_boutons, "💾 Sauvegarder", sauvegarder_json, COULEUR_VIOLET_FONCE, 3, 0)
creer_bouton(cadre_boutons, "📂 Charger", charger_json, COULEUR_BLEU, 3, 1)
creer_bouton(cadre_boutons, "🧹 Vider", vider_champs, COULEUR_GRIS, 4, 0)

cadre_boutons.columnconfigure(0, weight=1)
cadre_boutons.columnconfigure(1, weight=1)

# Colonne droite : statistiques, tableau, détails.
zone_droite = tk.Frame(conteneur, bg=COULEUR_FOND)
zone_droite.pack(side="right", fill="both", expand=True)

# Cartes statistiques.
cadre_stats = tk.Frame(zone_droite, bg=COULEUR_FOND)
cadre_stats.pack(fill="x", pady=(0, 12))


def creer_carte_stat(parent, titre, icone, couleur_accent):
    enveloppe = tk.Frame(parent, bg=COULEUR_FOND)
    enveloppe.pack(side="left", fill="x", expand=True, padx=5)

    liseret = tk.Frame(enveloppe, bg=couleur_accent, height=4)
    liseret.pack(fill="x")

    carte = tk.Frame(enveloppe, bg=COULEUR_CARTE, padx=14, pady=12,
                      highlightbackground="#e5e0f7", highlightthickness=1)
    carte.pack(fill="both", expand=True)

    label_titre_stat = tk.Label(
        carte, text=f"{icone}  {titre}", bg=COULEUR_CARTE, fg=COULEUR_GRIS,
        font=("Segoe UI", 9, "bold")
    )
    label_titre_stat.pack(anchor="w")

    label_valeur = tk.Label(carte, text="0", bg=COULEUR_CARTE, fg=couleur_accent, font=("Segoe UI", 19, "bold"))
    label_valeur.pack(anchor="w")

    return label_valeur


label_total = creer_carte_stat(cadre_stats, "TOTAL", "👥", COULEUR_VIOLET)
label_moyenne_classe = creer_carte_stat(cadre_stats, "MOYENNE CLASSE", "📊", COULEUR_BLEU_2)
label_admis = creer_carte_stat(cadre_stats, "ADMIS", "✅", COULEUR_VERT)
label_non_admis = creer_carte_stat(cadre_stats, "NON ADMIS", "❌", COULEUR_ROUGE)

# Tableau.
carte_tableau = creer_carte(zone_droite, COULEUR_BLEU_2, fill="both", expand=True)

label_tableau = tk.Label(
    carte_tableau,
    text="📋  Liste des étudiants",
    bg=COULEUR_CARTE,
    fg=COULEUR_VIOLET_FONCE,
    font=("Segoe UI", 15, "bold")
)
label_tableau.pack(anchor="w", pady=(0, 10))

cadre_arbre = tk.Frame(carte_tableau, bg=COULEUR_CARTE)
cadre_arbre.pack(fill="both", expand=True)

colonnes = ("nom", "prenom", "age", "notes", "moyenne", "resultat")
tableau = ttk.Treeview(cadre_arbre, columns=colonnes, show="headings", height=10)

tableau.heading("nom", text="Nom")
tableau.heading("prenom", text="Prénom")
tableau.heading("age", text="Âge")
tableau.heading("notes", text="Nb notes")
tableau.heading("moyenne", text="Moyenne")
tableau.heading("resultat", text="Résultat")

tableau.column("nom", width=130)
tableau.column("prenom", width=130)
tableau.column("age", width=70, anchor="center")
tableau.column("notes", width=90, anchor="center")
tableau.column("moyenne", width=110, anchor="center")
tableau.column("resultat", width=110, anchor="center")

tableau.tag_configure("admis", background="#dcfce7", foreground="#166534")
tableau.tag_configure("non_admis", background="#fee2e2", foreground="#991b1b")
tableau.tag_configure("sans_note", background="#f3f0fb", foreground=COULEUR_TEXTE)

scrollbar_y = ttk.Scrollbar(cadre_arbre, orient="vertical", command=tableau.yview)
tableau.configure(yscrollcommand=scrollbar_y.set)

tableau.pack(side="left", fill="both", expand=True)
scrollbar_y.pack(side="right", fill="y")

tableau.bind("<<TreeviewSelect>>", action_selection_tableau)

# Détails.
carte_details = creer_carte(zone_droite, COULEUR_ROSE, fill="x", pady=(12, 0))

label_details = tk.Label(
    carte_details,
    text="🪪  Détails de l'étudiant",
    bg=COULEUR_CARTE,
    fg=COULEUR_VIOLET_FONCE,
    font=("Segoe UI", 13, "bold")
)
label_details.pack(anchor="w", pady=(0, 8))

zone_details = tk.Text(
    carte_details,
    height=6,
    bg="#f5f3ff",
    fg=COULEUR_TEXTE,
    font=("Segoe UI", 10),
    relief="flat",
    highlightbackground="#ddd6fe",
    highlightthickness=1,
    padx=10,
    pady=8
)
zone_details.pack(fill="x")
zone_details.config(state="disabled")

# Message en bas (liseré coloré + texte lisible sur fond clair).
cadre_message = tk.Frame(fenetre, bg=COULEUR_FOND)
cadre_message.pack(fill="x", side="bottom")

liseret_message = tk.Frame(cadre_message, bg=COULEUR_VIOLET, height=3)
liseret_message.pack(fill="x", side="top")

label_message = tk.Label(
    cadre_message,
    text="👋 Bienvenue. Commencez par ajouter un étudiant.",
    bg=COULEUR_FOND,
    fg=COULEUR_TEXTE,
    font=("Segoe UI", 11, "bold"),
    pady=10
)
label_message.pack(fill="x")

# Initialisation.
actualiser_tableau()
fenetre.mainloop()
