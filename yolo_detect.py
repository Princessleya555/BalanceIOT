"""
Caisse Fruits & Légumes avec Caméra
Installer : pip install opencv-python Pillow
"""
#teste modification
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import threading, os, random
import json
from PIL import Image,ImageTk

try:
    from ultralytics import YOLO
    import cv2
    from PIL import Image, ImageTk
    CAM_OK = True
except ImportError:
    CAM_OK = False

# 1 --- Produits : nom -> (prix_euro_par_kg, teinte_min, teinte_max) -------------
#Fichier produits.json

with open("produits.json","r",encoding="utf-8") as f:
    produits = json.load(f)

#--- Détection produit-------------------------------------------------------------
model = YOLO("runs/classify/train/weights/best.pt")


# --- Détection couleur --------------------------------------------------------
def detecter(frame):
    results = model(frame)
    classes = []
    print(results[0].probs)
    for p in results[0].probs.top5:
        classe = results[0].names[p]
        classes.append(classe)
        print(classe)

    return classes

# --- Variables globales -------------------------------------------------------
panier      = []          # liste de dict {nom, prix, quantite, total}
suggestions = []          # 2 noms détectés par la caméra
frame_cam   = None        # dernière image de la caméra
cap         = None        # objet VideoCapture OpenCV
actif       = True        # flag pour stopper le thread caméra

#2/ --- Interface ----------------------------------------------------------------
root = tk.Tk()
root.title("Caisse Caméra — Fruits & Légumes")
root.configure(bg="#1a2e1a")
root.geometry("860x560")

#3/ Titre
tk.Label(root, text="CAISSE CAMÉRA — Fruits & Légumes",
         font=("Courier", 15, "bold"), bg="#1a2e1a", fg="#6ddc4a").pack(pady=6)
tk.Frame(root, height=2, bg="#6ddc4a").pack(fill="x", padx=16)

corps = tk.Frame(root, bg="#1a2e1a")
corps.pack(fill="both", expand=True, padx=16, pady=8)

#4/ ---- Colonne gauche : caméra + choix ----------------------------------------
gauche = tk.Frame(corps, bg="#1e3a1e")
gauche.pack(side="left", fill="both", expand=True, padx=(0, 6))

lbl_cam = tk.Label(gauche, bg="#000000", text="Démarrage caméra...",
                   fg="#6ddc4a", font=("Courier", 10), width=42, height=13)
lbl_cam.pack(pady=6)

tk.Label(gauche, text="Choisissez le produit détecté :",
         font=("Courier", 10), bg="#1e3a1e", fg="#aaaaaa").pack()


zone_produit = tk.Frame(gauche)
zone_produit.pack()

def produit_selectionne(produit):
    q = float(qty_var.get().replace(",", "."))
    nom  = produit["nom"]
    prix = produit["prix"]
    for x in panier:
        if x["nom"] == nom:
            x["qte"]   = round(x["qte"] + q, 3)
            x["total"] = round(x["qte"] * prix, 2)
            maj_panier(); return
    panier.append({"nom": nom, "prix": prix, "qte": q, "total": round(prix*q, 2)})
    maj_panier()


def maj_suggestions(liste):
    for widget in zone_produit.winfo_children():
        widget.destroy()

    for i, produit in enumerate(produits):
        if(produit['nom']==liste[0] ):
            img = Image.open(produit["image"])
            img = img.resize((50,50))
            img_tk = ImageTk.PhotoImage(img)
            texte = f"{produit['nom']}\n{produit['prix']} €/Kg\n"
            btn = tk.Button(zone_produit, image=img_tk,text=texte,width=90,height=90,compound="top", bg="white")
            btn.image = img_tk
            btn.configure(command=lambda p = produit: produit_selectionne(p))
            btn.grid(row=i//3,column=i%3, padx=5, pady=5)
 



tk.Label(gauche, text="Quantité (kg) :", font=("Courier", 10),
         bg="#1e3a1e", fg="#aaaaaa").pack(pady=(10, 2))
qty_var = tk.StringVar(value="1.000")
tk.Entry(gauche, textvariable=qty_var, width=10, justify="center",
         bg="#2f4a2f", fg="#f0c040", font=("Courier", 13, "bold"),
         bd=0).pack(ipady=4)

#5/ ---- Colonne droite : panier -------------------------------------------------
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

#6/ --- Fonctions ----------------------------------------------------------------



def maj_panier():
    txt_panier.configure(state="normal")
    txt_panier.delete("1.0", "end")
    for x in panier:
        txt_panier.insert("end",
            f"{x['nom']:<14} {x['qte']:>5.3f}kg  {x['prix']:.2f}EUR/kg  = {x['total']:.2f}EUR\n")
    txt_panier.configure(state="disabled")
    total = sum(x["total"] for x in panier)
    lbl_total.configure(text=f"TOTAL : {total:.2f} EUR")

def vider():
    panier.clear()
    maj_panier()

def imprimer():
    if not panier:
        messagebox.showinfo("", "Le panier est vide.")
        return
    
    now  = datetime.now()
    sep  = "=" * 44 +"\n"
    '''
    txt  = "\n".join([sep, "      MARCHE FRAIS — CAISSE CAMERA",
                      f"   {now.strftime('%d/%m/%Y  %H:%M:%S')}", sep] +
                     [f"{x['nom']:<14} {x['qte']:>5.3f}kg  {x['prix']:.2f}  = {x['total']:.2f}EUR"
                      for x in panier] +
                     ["-"*44, f"TOTAL : {sum(x['total'] for x in panier):.2f} EUR",
                      sep, "   Merci et à bientôt !", sep])
    '''
    txt  = sep
    txt  = txt + "      MARCHE FRAIS — CAISSE CAMERA\n" + sep
    txt = txt + f"   {now.strftime('%d/%m/%Y  %H:%M:%S')}" + "\n"
    total = 0
    for x in panier :
        txt  = txt + f"{x['nom']:<14} {x['qte']:>5.3f}kg  {x['prix']:.2f}  = {x['total']:.2f}EUR" +"\n"
        total = total + x['total']
    
    txt = txt + "-"*44 +"\n" + f"TOTAL : {total:.2f} EUR\n"
    txt = txt +  sep + "   Merci et à bientôt !\n" + sep


    win = tk.Toplevel(root)
    win.title("Ticket")
    win.configure(bg="#1a2e1a")
    win.geometry("460x420")

    tw  = tk.Text(win, font=("Courier", 10), bg="white", fg="#111",bd=0, padx=10, pady=10)
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

#7/ Boutons d'action
bf_act = tk.Frame(droite, bg="#1e3a1e")
bf_act.pack(fill="x", padx=8, pady=4)

tk.Button(bf_act, text="Vider",    command=vider,    bg="#e05050", fg="white",
          font=("Courier", 11, "bold"), bd=0, cursor="hand2", pady=5).pack(side="left", expand=True, fill="x", padx=2)
tk.Button(bf_act, text="Ticket",   command=imprimer, bg="#f0c040", fg="#1a2e1a",
          font=("Courier", 11, "bold"), bd=0, cursor="hand2", pady=5).pack(side="left", expand=True, fill="x", padx=2)

#8/ --- Caméra -------------------------------------------------------------------
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
            try: 
                root.after(0, lambda i=img: [lbl_cam.configure(image=i, text="", width=0, height=0), setattr(lbl_cam,"image",i)])
            except: pass
        time.sleep(0.033)
        
def analyser():
    if frame_cam is not None:
        maj_suggestions(detecter(frame_cam))
    root.after(2000, analyser)


if CAM_OK:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        threading.Thread(target=boucle_camera, daemon=True).start()
        root.after(2000, analyser)
    else:
        lbl_cam.configure(text="Aucune caméra détectée\n(mode démo actif)")
        
else:
    lbl_cam.configure(text="opencv-python non installé\npip install opencv-python Pillow")
    

#9/ Initialiser les boutons
#maj_suggestions(random.sample(list(PRODUITS), 2))

def fermer():
    global actif
    actif = False
    if cap: cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", fermer)
root.mainloop()
