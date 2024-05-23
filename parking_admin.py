import sqlite3
import tkinter as tk
from tkinter import messagebox

conn = sqlite3.connect('parking.db')

def get_clients_presents(conn):
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT client.name, client.voiture, client.matricule, reservations.parking_id
    FROM reservations
    JOIN client ON reservations.client_id = client.id
    WHERE reservations.heure_sortie IS NULL
    ''')  # Seulement les clients encore présents
    return cursor.fetchall()

def calculer_revenus(conn):
    cursor = conn.cursor()
   
    cursor.execute('''
    SELECT SUM(prix_paye)  
    FROM reservations
    ''')
    result = cursor.fetchone() 
    return result[0] if result[0] is not None else 0  

def afficher_places_disponibles(conn):
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, disponible
    FROM parking
    ''')
    return cursor.fetchall()

def authentification(username, password):
    if (username!="admin" or password != "admin"):
        messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect")
        return False
    return True

def afficher_interface_admin():
    fenetre_admin = tk.Toplevel()
    fenetre_admin.title("Interface Admin")
    
    
    def voir_clients_presents():
       clients_presents = get_clients_presents(conn)
       if clients_presents:
        # Création d'une nouvelle fenêtre pour afficher les clients présents
          fenetre_clients = tk.Toplevel()
          fenetre_clients.title("Clients Présents")
        
        # Création d'un widget Listbox pour afficher les clients
          listbox_clients = tk.Listbox(fenetre_clients, width=50, height=10)
          listbox_clients.pack(padx=10, pady=10)
        
        # Ajout des clients à la Listbox
          for client in clients_presents:
            client_info = f"Nom: {client[0]}, Voiture: {client[1]}, Matricule: {client[2]}, Place: {client[3]}"
            listbox_clients.insert(tk.END, client_info)
        
        # Ajout d'une barre de défilement à la Listbox
          scrollbar = tk.Scrollbar(fenetre_clients, orient=tk.VERTICAL)
          scrollbar.config(command=listbox_clients.yview)
          scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
          listbox_clients.config(yscrollcommand=scrollbar.set)
       else:
          messagebox.showinfo("Clients Présents", "Aucun client n'est présent.")
    
    def calculer_revenus_totaux():
        revenus_totals = calculer_revenus(conn)
        messagebox.showinfo("Revenus Totaux", f"Revenus totaux: {revenus_totals} euros")
    
    def voir_disponibilite_places():
        places = afficher_places_disponibles(conn)
        disponibilite_places = "\n".join([f"Place {place[0]}: {'Disponible' if place[1] == 0 else 'Occupée'}" for place in places])
        messagebox.showinfo("Disponibilité des Places", disponibilite_places)
    
    frame = tk.Frame(fenetre_admin)
    frame.pack(padx=10, pady=10)

    btn_clients_presents = tk.Button(frame, text="Voir Clients Présents", command=voir_clients_presents)
    btn_clients_presents.pack(fill=tk.X, padx=5, pady=5)
    
    btn_revenus_totaux = tk.Button(frame, text="Calculer Revenus Totaux", command=calculer_revenus_totaux)
    btn_revenus_totaux.pack(fill=tk.X, padx=5, pady=5)
    
    btn_disponibilite_places = tk.Button(frame, text="Voir Disponibilité Places", command=voir_disponibilite_places)
    btn_disponibilite_places.pack(fill=tk.X, padx=5, pady=5)

def main():
    root = tk.Tk()
    root.title("Parking Application")
    
    def authentification_et_affichage():
        username = entry_username.get()
        password = entry_password.get()
        if authentification(username, password):
            afficher_interface_admin()
        else:
            messagebox.showerror("Erreur d'Authentification", "Nom d'utilisateur ou mot de passe incorrect.")
    
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)
    
    label_username = tk.Label(frame, text="Nom d'utilisateur:")
    label_username.grid(row=0, column=0, padx=5, pady=5)
    entry_username = tk.Entry(frame)
    entry_username.grid(row=0, column=1, padx=5, pady=5)
    
    label_password = tk.Label(frame, text="Mot de passe:")
    label_password.grid(row=1, column=0, padx=5, pady=5)
    entry_password = tk.Entry(frame, show="*")
    entry_password.grid(row=1, column=1, padx=5, pady=5)
    
    btn_login = tk.Button(frame, text="Connexion", command=authentification_et_affichage)
    btn_login.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="we")

    root.mainloop()

if __name__ == "__main__":
    main()
