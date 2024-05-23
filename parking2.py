import tkinter as tk
from tkinter import *
from tkinter import messagebox
from datetime import datetime
import sqlite3

conn = sqlite3.connect('parking.db') 
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS client (
    id INTEGER PRIMARY KEY,
    name TEXT,
    voiture TEXT,
    matricule TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS parking (
    id INTEGER PRIMARY KEY,
    disponible INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,
    parking_id INTEGER,
    heure_entrer TEXT,
    heure_sortie TEXT,
    prix_par_heure REAL,
    prix_paye REAL,
    FOREIGN KEY (parking_id) REFERENCES parking(id)
)
''')

conn.commit() 
conn.close()

class Client:
    def __init__(self, client_id, name, voiture, matricule):
        self.client_id = client_id
        self.name = name
        self.voiture = voiture
        self.matricule = matricule

    def inserer_client(self, conn):
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO client (id, name, voiture, matricule) 
            VALUES (?, ?, ?, ?)
            ''',
            (self.client_id, self.name, self.voiture, self.matricule)
        )
        conn.commit() 

class Reservation:
    def __init__(self, client_id, parking_id, heure_entrer, prix_par_heure):
        self.client_id = client_id
        self.parking_id = parking_id
        self.heure_entrer = heure_entrer
        self.heure_sortie = None 
        self.prix_par_heure = prix_par_heure

    def inserer_reservation(self, conn):
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO reservations (client_id, parking_id, heure_entrer, heure_sortie, prix_par_heure)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (self.client_id, self.parking_id, self.heure_entrer, self.heure_sortie, self.prix_par_heure)
        )
        cursor.execute(
            '''
            UPDATE parking 
            SET disponible = 1  
            WHERE id = ?
            ''',
            (self.parking_id,)
        )
        conn.commit()  

    def quitter_parking(self, conn):
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT heure_entrer 
            FROM reservations 
            WHERE client_id = ? AND parking_id = ? AND heure_sortie IS NULL
            ''',
            (self.client_id, self.parking_id)
        )

        heure_entrer_result = cursor.fetchone()

        if heure_entrer_result is None:
            raise ValueError("Aucune réservation active trouvée pour ce client et cette place de parking.")

        heure_entrer = heure_entrer_result[0]

        heure_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute(
            '''
            UPDATE reservations 
            SET heure_sortie = ?
            WHERE client_id = ? AND parking_id = ?
            ''',
            (heure_actuelle, self.client_id, self.parking_id)
        )

        cursor.execute(
            '''
            UPDATE parking 
            SET disponible = 0  
            WHERE id = ?
            ''',
            (self.parking_id,)
        )
        client_id = self.client_id
        cursor.execute('''
            DELETE FROM client WHERE id =?
                       ''',(client_id,))
       
        heure_entrer_dt = datetime.strptime(heure_entrer, "%Y-%m-%d %H:%M:%S")
        heure_sortie_dt = datetime.strptime(heure_actuelle, "%Y-%m-%d %H:%M:%S")

        duree = (heure_sortie_dt - heure_entrer_dt).total_seconds() / 3600  
        cout_total = duree * self.prix_par_heure  
        cursor.execute(
            '''
            UPDATE reservations 
            SET prix_paye = ?
            WHERE client_id = ? AND parking_id = ?
            ''',
            (cout_total, self.client_id,self.parking_id)
        )

        conn.commit() 

        return cout_total 

def afficher_places_disponibles(conn):
    cursor = conn.cursor()  
    cursor.execute("SELECT * FROM parking WHERE disponible = 0")  
    places_disponibles = cursor.fetchall()
    return places_disponibles 

class ParkingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Parking System")
        self.root.geometry("750x350")
        self.root.configure(bg="lightgray")

        self.conn = sqlite3.connect('parking.db')
        self.cursor = self.conn.cursor()

        self.label = tk.Label(root, text="Voulez-vous réserver ou quitter le parking?", bg="lightgray")
        self.label.pack(side=tk.TOP, pady=30)

        self.reserve_button = tk.Button(root, text="Réserver", command=self.reserve_parking)
        self.reserve_button.pack(side=tk.TOP, pady=7)

        self.checkout_button = tk.Button(root, text="Quitter le parking", command=self.quit_parking)
        self.checkout_button.pack(side=tk.TOP, pady=6)

        self.quit_button = tk.Button(root, text="Quitter", command=self.quit)
        self.quit_button.pack(pady=9)

    def reserve_parking(self):
        reserve_window = tk.Toplevel(self.root)
        reserve_window.title("Réserver une place de parking")
        reserve_window.geometry("600x400")
        reserve_window.configure(bg="lightgray")

        info_frame = tk.Frame(reserve_window, bg="lightgray")
        info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        parking_frame = tk.Frame(reserve_window, bg="lightgray")
        parking_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        tk.Label(info_frame, text="ID du client:", bg="lightgray").grid(row=0, column=0, sticky="w", pady=2)
        tk.Label(info_frame, text="Nom:", bg="lightgray").grid(row=1, column=0, sticky="w", pady=2)
        tk.Label(info_frame, text="Modèle de voiture:", bg="lightgray").grid(row=2, column=0, sticky="w", pady=2)
        tk.Label(info_frame, text="Numéro de matricule:", bg="lightgray").grid(row=3, column=0, sticky="w", pady=2)
        tk.Label(info_frame, text="ID de la place de parking:", bg="lightgray").grid(row=4, column=0, sticky="w", pady=2)

        client_id_entry = tk.Entry(info_frame)
        client_id_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        name_entry = tk.Entry(info_frame)
        name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        car_model_entry = tk.Entry(info_frame)
        car_model_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        plate_number_entry = tk.Entry(info_frame)
        plate_number_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        reservation_entry = tk.Entry(info_frame)
        reservation_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        self.cursor.execute("SELECT id FROM parking WHERE disponible = 0")
        available_spaces = self.cursor.fetchall()

        if available_spaces:
            tk.Label(parking_frame, text="Les ID des places de parking disponibles :", bg="lightgray").grid(row=0, column=0, sticky="w", pady=2)

            for index, space in enumerate(available_spaces):
                row = 1 + (index // 6)
                column = index % 6
                tk.Label(parking_frame, text=space[0], bg="lightgray").grid(row=row, column=column, padx=1, pady=0, sticky="w")
        else:
            tk.Label(parking_frame, text="Aucune place de parking disponible.", bg="lightgray").grid(row=1, column=0, sticky="w", pady=2)

        reserve_button = tk.Button(reserve_window, text="Réserver", command=lambda: self.reserve(client_id_entry.get(), name_entry.get(), car_model_entry.get(), plate_number_entry.get(), reservation_entry.get()), bg="white", fg="black")
        reserve_button.grid(row=2, column=0, pady=10)

    def reserve(self, client_id, name, car_model, plate_number, parking_id):
        try:
            client = (client_id, name, car_model, plate_number)
            self.cursor.execute("INSERT INTO client (id, name, voiture, matricule) VALUES (?, ?, ?, ?)", client)
            self.conn.commit()
            heure_entrer = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prix_par_heure = 5.0  
            reservation = (client_id, parking_id, heure_entrer, None, prix_par_heure)
            self.cursor.execute("INSERT INTO reservations (client_id, parking_id, heure_entrer, heure_sortie, prix_par_heure) VALUES (?, ?, ?, ?, ?)", reservation)
            self.cursor.execute("UPDATE parking SET disponible = 1 WHERE id = ?", (parking_id,))
            self.conn.commit()
            messagebox.showinfo("Confirmation", "Réservation effectuée avec succès!")
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {e}")

    def quit_parking(self):
        quit_window = tk.Toplevel(self.root)
        quit_window.title("Quitter le parking")
        quit_window.geometry("600x400")
        quit_window.configure(bg="lightgray")

        info_frame = tk.Frame(quit_window, bg="lightgray")
        info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        tk.Label(info_frame, text="Entrez votre ID de client:", bg="lightgray").grid(row=0, column=0, sticky="w", pady=2)
        tk.Label(info_frame, text="Entrez l'ID de la place de parking que vous quittez:", bg="lightgray").grid(row=1, column=0, sticky="w", pady=2)

        client_id_entry = tk.Entry(info_frame)
        client_id_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        reservation_entry = tk.Entry(info_frame)
        reservation_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        quitter_button = tk.Button(quit_window, text="Quitter le parking", command=lambda: self.quit_parking_action(client_id_entry.get(), reservation_entry.get()), bg="white", fg="black")
        quitter_button.grid(row=2, column=0, pady=10)

    def quit_parking_action(self, client_id, parking_id):
        try:
            reservation = Reservation(client_id=client_id, parking_id=parking_id, heure_entrer="", prix_par_heure=5.0)
            cout_total = reservation.quitter_parking(self.conn)
            messagebox.showinfo("Quitter", f"Vous avez quitté le parking. Prix à payer: {cout_total:.2f} €")
        except ValueError as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {e}")

    def quit(self):
        self.conn.close()
        self.root.destroy()

def main():  
    conn = sqlite3.connect('parking.db') 
    root = tk.Tk()
    app = ParkingApp(root)
    root.mainloop() 

    while True:
        reponse = input("Voulez-vous réserver ou quitter le parking? (réserver/quitter/fin) ")

        if reponse.lower() == "fin":
            print("Merci! À bientôt!")
            break  

        if reponse.lower() == "reserver":
            client_id = int(input("Entrez votre ID: "))
            nom = input("Entrez votre nom: ")
            voiture = input("Entrez le modèle de votre voiture: ")
            matricule = input("Entrez votre numéro de matricule: ")

            client_obj = Client(client_id=client_id, name=nom, voiture=voiture, matricule=matricule)  

            places_disponibles = afficher_places_disponibles(conn)

            if not places_disponibles:
                print("Aucune place de parking disponible.")
                continue  

            print("Places disponibles:")
            i=0
            for place in places_disponibles:
                print(f" | {place[0]}|", end="")
                i+=1
                if i == 10:
                    print("\n")
                    i = 0
            print()
            parking_id = int(input("Choisissez l'ID de la place de parking: "))
            client_obj.inserer_client(conn)
            
            heure_entrer = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reservation = Reservation(client_id=client_id, parking_id=parking_id, heure_entrer=heure_entrer, prix_par_heure=5.50)
            reservation.inserer_reservation(conn)  
            conn.commit()   

            print("Réservation effectuée avec succès!")

        elif reponse.lower() == "quitter":
            client_id = int(input("Entrez votre ID de client: "))
            parking_id = int(input("Entrez l'ID de la place de parking que vous quittez: "))
            heure_entrer = 0
            reservation = Reservation(client_id=client_id, parking_id=parking_id, heure_entrer=heure_entrer, prix_par_heure=5.0)

            try:
                cout_total = reservation.quitter_parking(conn)
                print(f"Vous avez quitté le parking. Prix à payer: {cout_total:.2f} €")
            except ValueError as e:
                print(f"Erreur: {e}")

    conn.close()  

if __name__ == "__main__":
    main()
