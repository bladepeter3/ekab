import sqlite3
import os
from datetime import datetime

def read_daily_logbook():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Σημερινή ημερομηνία: {today}")
    
    user_input = input("Εισάγετε ημερομηνία (Μορφή: YYYY-MM-DD) ή πατήστε Enter για τη σημερινή: ").strip()
    target_date = user_input if user_input else today
    
    db_filename = f"logins_{target_date}.db"
    
    if not os.path.exists(db_filename):
        print(f"\n❌ Δεν βρέθηκε αρχείο καταγραφής για την ημερομηνία {target_date}.")
        print(f"Αναζητήθηκε το αρχείο: {db_filename}")
        return

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    
    try:
        # ---> Now selecting the 'position' column as well <---
        cursor.execute("SELECT id, name, last_name, timestamp, role, position FROM login_history")
        rows = cursor.fetchall()
        
        print(f"\n=== ΚΑΤΑΓΡΑΦΕΣ ΕΙΣΟΔΟΥ ΓΙΑ {target_date} ===")
        
        if not rows:
            print("Το αρχείο υπάρχει, αλλά δεν βρέθηκαν συνδέσεις.")
        else:
            for row in rows:
                log_id = row[0]
                name = row[1]
                last_name = row[2]
                time = row[3]
                role = row[4]
                position = row[5] # Extracting the position
                
                # Format the position so it looks nice, or leave it empty for radio operators
                pos_display = f"Γραμμή: {position}" if position else " " * 10
                
                print(f"ID: {log_id: <3} | Ώρα: {time} | Θέση: {role: <14} | {pos_display: <10} | Χρήστης: {name} {last_name}")
            
            print("-" * 75)
            print(f"Σύνολο συνδέσεων: {len(rows)}")
            
    except sqlite3.OperationalError as e:
        print(f"\n❌ Σφάλμα ανάγνωσης της βάσης δεδομένων: {e}")
        print("Σημείωση: Αν χρησιμοποιείτε παλιό αρχείο καταγραφής, ίσως δεν περιέχει τη στήλη 'position'.")
    finally:
        conn.close()

if __name__ == '__main__':
    read_daily_logbook()