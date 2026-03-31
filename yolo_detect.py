"""
Caisse Fruits & Légumes avec Caméra
Installer : pip install opencv-python Pillow
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import threading, os, random

try:
    import cv2
    from PIL import Image, ImageTk
    CAM_OK = True
except ImportError:
    CAM_OK = False

# --- Produits : nom -> (prix_euro_par_kg, teinte_min, teinte_max) -------------
PRODUITS = {
    "Pomme":     (2.50,  0,  15),
    "Tomate":    (2.40,  0,  12),
    "Orange":    (1.80, 10,  25),
    "Citron":    (3.20, 22,  35),
    "Banane":    (1.60, 22,  32),
    "Brocoli":   (2.80, 45,  85),
    "Aubergine": (2.60,120, 160),
    "Carotte":   (1.20, 10,  20),
    "Fraise":    (6.00,  0,  10),
    "Avocat":    (5.00, 50,  90),
}

# --- Détection couleur --------------------------------------------------------
def detecter(frame):
    h, w = frame.shape[:2]
    roi   = frame[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)]
    hsv   = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    masq  = cv2.inRange(hsv, (0, 40, 40), (180, 255, 255))
    if cv2.countNonZero(masq) < 300:
        return random.sample(list(PRODUITS), 2)
    teinte = float(cv2.mean(hsv[:,:,0], mask=masq)[0])
    def score(n):
        _, hmin, hmax = PRODUITS[n]
        return 100 if hmin <= teinte <= hmax else max(0, 100 - min(abs(teinte-hmin), abs(teinte-hmax))*3)
    return sorted(PRODUITS, key=score, reverse=True)[:2]

# --- Variables globales -------------------------------------------------------
panier      = []          # liste de dict {nom, prix, quantite, total}
suggestions = []          # 2 noms détectés par la caméra
frame_cam   = None        # dernière image de la caméra
cap         = None        # objet VideoCapture OpenCV
actif       = True        # flag pour stopper le thread caméra

# --- Interface ----------------------------------------------------------------
root = tk.Tk()
root.title("Caisse Caméra — Fruits & Légumes")
root.configure(bg="#1a2e1a")
root.geometry("860x560")

# Titre
tk.Label(root, text="CAISSE CAMÉRA — Fruits & Légumes",
         font=("Courier", 15, "bold"), bg="#1a2e1a", fg="#6ddc4a").pack(pady=6)
tk.Frame(root, height=2, bg="#6ddc4a").pack(fill="x", padx=16)

corps = tk.Frame(root, bg="#1a2e1a")
corps.pack(fill="both", expand=True, padx=16, pady=8)

# ---- Colonne gauche : caméra + choix ----------------------------------------
gauche = tk.Frame(corps, bg="#1e3a1e")
gauche.pack(side="left", fill="both", expand=True, padx=(0, 6))

lbl_cam = tk.Label(gauche, bg="#000000", text="Démarrage caméra...",
                   fg="#6ddc4a", font=("Courier", 10), width=42, height=13)
lbl_cam.pack(pady=6)

tk.Label(gauche, text="Choisissez le produit détecté :",
         font=("Courier", 10), bg="#1e3a1e", fg="#aaaaaa").pack()

btn1 = tk.Button(gauche, text="---", font=("Courier", 12, "bold"),
                 bg="#2f4a2f", fg="#ddf0cc", bd=0, cursor="hand2", pady=10)
btn1.pack(fill="x", padx=8, pady=(6, 2))
lbl_prix1 = tk.Label(gauche, text="", font=("Courier", 9),
                     bg="#1e3a1e", fg="#6ddc4a")
lbl_prix1.pack()

btn2 = tk.Button(gauche, text="---", font=("Courier", 12, "bold"),
                 bg="#2f4a2f", fg="#ddf0cc", bd=0, cursor="hand2", pady=10)
btn2.pack(fill="x", padx=8, pady=(4, 2))
lbl_prix2 = tk.Label(gauche, text="", font=("Courier", 9),
                     bg="#1e3a1e", fg="#6ddc4a")
lbl_prix2.pack()

tk.Label(gauche, text="Quantité (kg) :", font=("Courier", 10),
         bg="#1e3a1e", fg="#aaaaaa").pack(pady=(10, 2))
qty_var = tk.StringVar(value="1.000")
tk.Entry(gauche, textvariable=qty_var, width=10, justify="center",
         bg="#2f4a2f", fg="#f0c040", font=("Courier", 13, "bold"),
         bd=0).pack(ipady=4)

# ---- Colonne droite : panier -------------------------------------------------
droite = tk.Frame(corps, bg="#1e3a1e")
droite.pack(side="right", fill="both", expand=True, padx=(6, 0))

tk.Label(droite, text="PANIER", font=("Courier", 12, "bold"),
         bg="#1e3a1e", fg="#f0c040", pady=4).pack()

txt_panier = tk.Text(droite, font=("Courier", 10), bg="#2f4a2f",
                     fg="#ddf0cc", bd=0, state="disabled", padx=6, pady=4)
txt_panier.pack(fill="both", expand=True, padx=8)

lbl_total = tk.Label(droite, text="TOTAL : 0.00 EUR",
                     font=("Courier", 15, "bold"), bg="#2f4a2f", fg="#f0c040")
lbl_total.pack(fill="x", padx=8, pady=6)

# --- Fonctions ----------------------------------------------------------------
choix_actuel = tk.IntVar(value=-1)   # 0 = btn1, 1 = btn2, -1 = rien

def selectionner(num):
    choix_actuel.set(num)
    btn1.configure(bg="#6ddc4a" if num==0 else "#2f4a2f",
                   fg="#1a2e1a" if num==0 else "#ddf0cc")
    btn2.configure(bg="#6ddc4a" if num==1 else "#2f4a2f",
                   fg="#1a2e1a" if num==1 else "#ddf0cc")

btn1.configure(command=lambda: selectionner(0))
btn2.configure(command=lambda: selectionner(1))

def maj_suggestions(liste):
    global suggestions
    suggestions = liste
    choix_actuel.set(-1)
    btn1.configure(text=liste[0], bg="#2f4a2f", fg="#ddf0cc")
    btn2.configure(text=liste[1], bg="#2f4a2f", fg="#ddf0cc")
    lbl_prix1.configure(text=f"{PRODUITS[liste[0]][0]:.2f} EUR/kg")
    lbl_prix2.configure(text=f"{PRODUITS[liste[1]][0]:.2f} EUR/kg")

def maj_panier():
    txt_panier.configure(state="normal")
    txt_panier.delete("1.0", "end")
    for x in panier:
        txt_panier.insert("end",
            f"{x['nom']:<14} {x['qte']:>5.3f}kg  {x['prix']:.2f}EUR/kg  = {x['total']:.2f}EUR\n")
    txt_panier.configure(state="disabled")
    total = sum(x["total"] for x in panier)
    lbl_total.configure(text=f"TOTAL : {total:.2f} EUR")

def ajouter():
    idx = choix_actuel.get()
    if idx < 0:
        messagebox.showwarning("", "Sélectionnez un produit d'abord.")
        return
    try:
        q = float(qty_var.get().replace(",", "."))
        assert q > 0
    except:
        messagebox.showwarning("", "Quantité invalide.")
        return
    nom  = suggestions[idx]
    prix = PRODUITS[nom][0]
    for x in panier:
        if x["nom"] == nom:
            x["qte"]   = round(x["qte"] + q, 3)
            x["total"] = round(x["qte"] * prix, 2)
            maj_panier(); return
    panier.append({"nom": nom, "prix": prix, "qte": q, "total": round(prix*q, 2)})
    maj_panier()
    selectionner(-1)

def vider():
    panier.clear()
    maj_panier()

def imprimer():
    if not panier:
        messagebox.showinfo("", "Le panier est vide.")
        return
    now  = datetime.now()
    sep  = "=" * 44
    txt  = "\n".join([sep, "      MARCHE FRAIS — CAISSE CAMERA",
                      f"   {now.strftime('%d/%m/%Y  %H:%M:%S')}", sep] +
                     [f"{x['nom']:<14} {x['qte']:>5.3f}kg  {x['prix']:.2f}  = {x['total']:.2f}EUR"
                      for x in panier] +
                     ["-"*44, f"TOTAL : {sum(x['total'] for x in panier):.2f} EUR",
                      sep, "   Merci et à bientôt !", sep])
    win = tk.Toplevel(root)
    win.title("Ticket"); win.configure(bg="#1a2e1a"); win.geometry("460x420")
    tw  = tk.Text(win, font=("Courier", 10), bg="white", fg="#111",
                  bd=0, padx=10, pady=10)
    tw.insert("1.0", txt); tw.configure(state="disabled")
    tw.pack(fill="both", expand=True, padx=16, pady=8)
    def sauver():
        f = os.path.join(os.path.expanduser("~"), f"ticket_{now.strftime('%Y%m%d_%H%M%S')}.txt")
        open(f, "w", encoding="utf-8").write(txt)
        messagebox.showinfo("Sauvegardé", f"Fichier :\n{f}")
    bf = tk.Frame(win, bg="#1a2e1a"); bf.pack(pady=6)
    tk.Button(bf, text="Sauvegarder", command=sauver, bg="#6ddc4a", fg="#1a2e1a",
              font=("Courier", 11, "bold"), bd=0, cursor="hand2", padx=10, pady=5).pack(side="left", padx=6)
    tk.Button(bf, text="Fermer", command=win.destroy, bg="#e05050", fg="white",
              font=("Courier", 11, "bold"), bd=0, cursor="hand2", padx=10, pady=5).pack(side="left", padx=6)

# Boutons d'action
bf_act = tk.Frame(droite, bg="#1e3a1e"); bf_act.pack(fill="x", padx=8, pady=4)
tk.Button(bf_act, text="Ajouter",  command=ajouter,  bg="#6ddc4a", fg="#1a2e1a",
          font=("Courier", 11, "bold"), bd=0, cursor="hand2", pady=5).pack(side="left", expand=True, fill="x", padx=2)
tk.Button(bf_act, text="Vider",    command=vider,    bg="#e05050", fg="white",
          font=("Courier", 11, "bold"), bd=0, cursor="hand2", pady=5).pack(side="left", expand=True, fill="x", padx=2)
tk.Button(bf_act, text="Ticket",   command=imprimer, bg="#f0c040", fg="#1a2e1a",
          font=("Courier", 11, "bold"), bd=0, cursor="hand2", pady=5).pack(side="left", expand=True, fill="x", padx=2)

# --- Caméra -------------------------------------------------------------------
def boucle_camera():
    global frame_cam
    import time
    while actif:
        ok, f = cap.read()
        if ok:
            frame_cam = f.copy()
            h, w = f.shape[:2]
            cv2.rectangle(f, (int(w*0.2), int(h*0.2)), (int(w*0.8), int(h*0.8)), (109,220,74), 2)
            img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).resize((390, 280)))
            try: root.after(0, lambda i=img: [lbl_cam.configure(image=i, text="", width=0, height=0), setattr(lbl_cam,"image",i)])
            except: pass
        time.sleep(0.033)

def analyser():
    if frame_cam is not None:
        maj_suggestions(detecter(frame_cam))
    root.after(2000, analyser)

def mode_demo():
    maj_suggestions(random.sample(list(PRODUITS), 2))
    root.after(4000, mode_demo)

if CAM_OK:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        threading.Thread(target=boucle_camera, daemon=True).start()
        root.after(2000, analyser)
    else:
        lbl_cam.configure(text="Aucune caméra détectée\n(mode démo actif)")
        mode_demo()
else:
    lbl_cam.configure(text="opencv-python non installé\npip install opencv-python Pillow")
    mode_demo()

# Initialiser les boutons
maj_suggestions(random.sample(list(PRODUITS), 2))

def fermer():
    global actif
    actif = False
    if cap: cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", fermer)
root.mainloop()