import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QGroupBox, QSplitter,QMessageBox,QDialog
)
from PyQt6.QtCore import Qt,QDateTime,QTimer
from PyQt6.QtGui import QColor, QBrush  # <--- ADD THIS LINE

from caller import EKABTopRow
from history_ui import IncidentListWindow
import sqlite3
import os
from datetime import datetime


class UnlockDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("🔒 Σύστημα Κλειδωμένο")
        self.setFixedSize(300, 200)
        
        # This completely removes the "X" close button so they CANNOT bypass it!
        self.setWindowFlags(Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint)
        self.setModal(True) # Blocks interaction with the dashboard behind it
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        lbl = QLabel("Το σύστημα είναι κλειδωμένο.\nΕισάγετε τον κωδικό σας για ξεκλείδωμα.")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-weight: bold; color: #d32f2f;")
        layout.addWidget(lbl)
        
        # 1. Show the username, but lock it so it cannot be edited!
        self.username_input = QLineEdit()
        self.username_input.setText(parent.current_username)
        self.username_input.setReadOnly(True)
        self.username_input.setStyleSheet("background-color: #dddddd; color: #555555;")
        layout.addWidget(self.username_input)
        
        # 2. The password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Κωδικός")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        self.btn_unlock = QPushButton("Ξεκλείδωμα")
        self.btn_unlock.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.btn_unlock.clicked.connect(self.check_unlock)
        layout.addWidget(self.btn_unlock)
        
    def check_unlock(self):
        """Checks if the typed password matches the logged-in user's password."""
        typed_password = self.password_input.text()
        
        # Compare the typed password against the one stored in the parent (DispatcherDashboard)
        if typed_password == self.parent().current_password:
            self.accept() # Success! Closes the lock screen safely
        else:
            QMessageBox.warning(self, "Σφάλμα", "Λάθος κωδικός. Δοκιμάστε ξανά.")
            self.password_input.clear()

class DispatcherDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Τηλεφωνητής - ΕΚΑΒ ΘΕΣΣΑΛΟΝΙΚΗΣ")
        self.resize(1400, 800)
        self.setup_ui()
        
        # ==========================================
        # ---> NEW: AUTO-REFRESH TIMER <---
        # ==========================================
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_all_tables)
        self.refresh_timer.start(5000) # 5000 milliseconds = 5 seconds
        
    def setup_ui(self):
        # Master layout for the entire dashboard
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ==========================================
        # 1. TOP TOOLBAR
        # ==========================================
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # Action Buttons (Left)
        self.btn_list = QPushButton("📄\nΛίστα")
        self.btn_list.setFixedSize(60, 60)
        self.btn_list.clicked.connect(self.open_list_window)
        
        self.btn_new = QPushButton("📝+\nΝέο")
        self.btn_new.setFixedSize(60, 60)
        self.btn_new.clicked.connect(self.open_new_incident_form)

        # ---> NEW: Refresh Button <---
        self.btn_refresh = QPushButton("🔄\nΑνανέωση")
        self.btn_refresh.setFixedSize(70, 60)
        self.btn_refresh.clicked.connect(self.refresh_all_tables)
        
        toolbar_layout.addWidget(self.btn_list)
        toolbar_layout.addWidget(self.btn_new)
        toolbar_layout.addWidget(self.btn_refresh) # Add to the screen
        toolbar_layout.addSpacing(20)


        
        
        toolbar_layout.addWidget(self.btn_list)
        toolbar_layout.addWidget(self.btn_new)
        toolbar_layout.addSpacing(20)
        
        # Quick Filter (Γρήγορο Φίλτρο)
        filter_group = QGroupBox("Γρήγορο Φίλτρο")
        filter_group.setStyleSheet("QGroupBox { background-color: #888888; color: white; font-weight: bold; }")
        filter_layout = QVBoxLayout()
        filter_layout.setContentsMargins(5, 5, 5, 5)
        
        self.filter_input = QLineEdit()
        self.filter_input.setFixedWidth(300)
        filter_layout.addWidget(self.filter_input)
        filter_group.setLayout(filter_layout)
        
        toolbar_layout.addWidget(filter_group)
        
        # Stretch pushes the user info to the far right
        toolbar_layout.addStretch()
        
        # User Info & System Buttons (Right)
        self.user_label = QLabel("Χρήστης: giannekas, Θέση: 99")
        self.user_label.setStyleSheet("font-weight: bold;")
        toolbar_layout.addWidget(self.user_label)
        toolbar_layout.addSpacing(10)
        
        self.btn_lock = QPushButton("🔒")
        self.btn_lock.setFixedSize(50, 50)
        self.btn_lock.clicked.connect(self.lock_system)

        
        self.btn_logout = QPushButton("⏻")
        self.btn_logout.setFixedSize(50, 50)
        self.btn_logout.clicked.connect(self.logout)
        
        toolbar_layout.addWidget(self.btn_lock)
        toolbar_layout.addWidget(self.btn_logout)

        main_layout.addLayout(toolbar_layout)

        # ==========================================
        # 2. TABLES SECTION (Using a Splitter)
        # ==========================================
        # A QSplitter allows the user to drag the border between the top and bottom tables to resize them!
        splitter = QSplitter(Qt.Orientation.Vertical)

# --- Top Table: Τρέχοντα Περιστατικά ---
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_current = QLabel("Τρέχοντα Περιστατικά")
        lbl_current.setStyleSheet("background-color: #666666; color: white; padding: 3px; font-weight: bold;")
        top_layout.addWidget(lbl_current)
        
        self.current_table = QTableWidget()
        self.setup_current_table()
        self.current_table.cellDoubleClicked.connect(self.open_current_incident)
        
        # ---> ADD THIS LINE HERE <---
        #self.populate_dummy_data()
        
        top_layout.addWidget(self.current_table)
        
        splitter.addWidget(top_widget)

        # --- Bottom Table: Περιστατικά σε αναμονή ---
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_pending = QLabel("Περιστατικά σε αναμονή στοιχείων")
        lbl_pending.setStyleSheet("background-color: #666666; color: white; padding: 3px; font-weight: bold;")
        bottom_layout.addWidget(lbl_pending)
        
        self.pending_table = QTableWidget()
        self.setup_pending_table()
        bottom_layout.addWidget(self.pending_table)
        self.pending_table.cellDoubleClicked.connect(self.open_pending_incident)
        
        splitter.addWidget(bottom_widget)
        
        # Set the top table to take up more space initially (e.g., 70% top, 30% bottom)
        splitter.setSizes([700, 300])

        main_layout.addWidget(splitter)

        # Automatically load all incidents on startup
        self.refresh_all_tables()

    def setup_current_table(self):
        """Configures the columns and style for the Current Incidents table."""
        headers = [
            "A/A", "Κωδ. Κάρτας", "Επείγον", "Ανταπόκριση", "Κατάσταση", 
            "Ημ/Ώρα Κλήσης", "Ασθενοφόρο", "Είδος Συμβάντος", "Δήμος", 
            "Διεύθυνση", "Αριθμός", "Νοσοκομείο", "Επώνυμο Πάσχοντος", 
            "Όνομα Πάσχοντος", "Σημειώσεις"
        ]
        self.current_table.setColumnCount(len(headers))
        self.current_table.setHorizontalHeaderLabels(headers)
        
        # Styling the table headers to match the dark grey in the image
        self.current_table.horizontalHeader().setStyleSheet(
            "::section { background-color: #666666; color: white; font-weight: bold; border: 1px solid #444444; }"
        )
        # Make the table stretch to fill empty horizontal space, but allow column resizing
        self.current_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.current_table.horizontalHeader().setStretchLastSection(True)
        self.current_table.verticalHeader().setVisible(False) # Hide default row numbers
        self.current_table.setAlternatingRowColors(True)

    def setup_pending_table(self):
        """Configures the columns and style for the Pending Incidents table."""
        headers = [
            "A/A", "Κωδ. Κάρτας", "Ημ/Ώρα", "Είδος Συμβάντος", "Διεύθυνση", 
            "Δήμος", "Αριθμός", "Επώνυμο Πάσχοντος", "Όνομα Πάσχοντος", 
            "Σημειώσεις", "Τηλέφωνα", "Αιτιολογία", "Αφετηρία"
        ]
        self.pending_table.setColumnCount(len(headers))
        self.pending_table.setHorizontalHeaderLabels(headers)
        
        self.pending_table.horizontalHeader().setStyleSheet(
            "::section { background-color: #666666; color: white; font-weight: bold; border: 1px solid #444444; }"
        )
        self.pending_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.pending_table.horizontalHeader().setStretchLastSection(True)
        self.pending_table.verticalHeader().setVisible(False)

    def populate_dummy_data(self):
        """Fills the top table with sample data and applies color coding."""
        
        # Sample data mimicking the image. The last item in each list is the hex color for the row.
        data = [
            # A/A, Κωδ, Επείγον, Ανταπ., Κατάσταση, Ημ/Ώρα, Ασθ., Είδος, Δήμος, Διεύθυνση, Αριθμός, Νοσ., Επώνυμο, Όνομα, Σημειώσεις, Row Color
            ["1", "022792", "ΝΑΙ", "Κανονική", "Ανοιχτή", "14/01/2021 06:58", "", "ΨΥΧΙΑΤΡΙΚΟ", "ΘΕΣΣΑΛΟΝΙΚΗΣ", "ΝΑΤΣΙΝΑ ΘΕΟΔ.", "21", "", "ΓΚΙΟΥΡΤΖΙΕΦ", "ΦΕΡΔΙΝΑΝΤ", "Η ΜΗΤΕΡΑ ΤΟΥ ΑΝΑΦΕΡΕΙ...", "#FFFFFF"],
            ["3", "022790", "ΝΑΙ", "Επείγουσα", "Ανοιχτή", "14/01/2021 06:42", "A.10", "ΚΑΡΔΙΟΛΟΓΙΚΟ", "ΘΕΣΣΑΛΟΝΙΚΗΣ", "ΑΕΤΟΡΑΧΗΣ", "16", "", "ΚΑΡΑΝΙΚΑ", "ΑΛΕΞΑΝΔΡΑ", "ΑΝΑΜΟΝΗ ΘΕΡΜΟΜΕΤΡΗΣΗΣ", "#FFFFFF"],
            ["4", "022789", "ΝΑΙ", "Υπερεπείγουσα", "Διαβιβασμένη", "14/01/2021 06:13", "A.01", "ΕΓΚΑΥΜΑ", "ΝΕΑΠΟΛΗΣ", "ΔΙΟΜΗΔΗ ΚΟΜΝΗΝΟΥ", "4", "", "ΓΕΩΡΓΙΑΔΗΣ", "ΣΤΕΡΓΙΟΣ", "ΙΑΤΡΟΣ ΚΑΡΔΙΟΛΟΓΟΣ ΣΤΟ ΣΗΜΕΙΟ", "#4DA6FF"],
            ["5", "022788", "ΟΧΙ", "", "Ενημερωμένη", "14/01/2021 06:03", "", "", "ΚΑΛΑΜΑΡΙΑΣ", "ΑΓΙΟΥ ΝΙΚΟΛΑΟΥ", "39", "", "ΦΙΣΕΚΗΣ", "ΧΡΗΣΤΟΣ", "ΕΠΙΘΥΜΟΥΝ ΝΑ ΕΙΝΑΙ ΛΙΓΟ ΝΩΡΙΤΕΡΑ", "#FFFF99"],
            ["11", "022696", "ΟΧΙ", "", "Νέα", "13/01/2021 15:10", "", "", "ΛΑΡΙΣΑΣ", "ΚΙΡΚΗΣ", "21", "", "ΤΣΙΒΟΓΛΟΥ", "ΒΑΣΙΛΕΙΟΣ", "ΜΕ Χ1 / ΣΥΝΟΔΕΙΑ ΜΗΤΕΡΑΣ", "#ADD8E6"],
        ]
        
        self.current_table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            row_color = QColor(row_data[15]) # Get the hex color we defined at the end of the list
            
            # Loop through the 15 data columns
            for col_idx in range(15):
                text = row_data[col_idx]
                item = QTableWidgetItem(text)
                
                # Center the text
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # 1. Set the default background color for the whole row
                item.setBackground(QBrush(row_color))
                
                # 2. Special Color Overrides for the "Ανταπόκριση" column (Index 3)
                if col_idx == 3:
                    if text == "Κανονική":
                        item.setBackground(QBrush(QColor("#8FBC8F"))) # Green
                    elif text == "Επείγουσα":
                        item.setBackground(QBrush(QColor("#F4A460"))) # Orange
                    elif text == "Υπερεπείγουσα":
                        item.setBackground(QBrush(QColor("#1E90FF"))) # Bright Blue
                        
                self.current_table.setItem(row_idx, col_idx, item)

    def open_new_incident_form(self):
        """Opens the form, stamps time/position/operator, and creates the DB placeholder."""
        self.incident_window = EKABTopRow()
        
        now = QDateTime.currentDateTime()
        self.incident_window.date_input.setText(now.toString("dd/MM/yyyy"))
        self.incident_window.time_input.setText(now.toString("HH:mm"))
        
        # Inject Position
        if hasattr(self, 'shift_position') and self.shift_position:
            self.incident_window.desk_input.setText(self.shift_position)
            
        # Inject Operator Username
        if hasattr(self, 'current_username') and self.current_username:
            self.incident_window.operator_input.setText(self.current_username)
            
        # ---> Trigger the initial save to instantly generate the Card Code <---
        self.incident_window.initialize_empty_incident()
        
        self.incident_window.show()

    def open_pending_incident(self, row, column):
        """Triggered when double-clicking a row in the pending table."""
        item = self.pending_table.item(row, 0) # 0 is the A/A (ID) column
        if item and item.text():
            self.open_existing_incident_form(item.text(), is_pending=True)

    def open_current_incident(self, row, column):
        """Triggered when double-clicking a row in the current table."""
        item = self.current_table.item(row, 0)
        if item and item.text():
            self.open_existing_incident_form(item.text(), is_pending=False)

    def open_existing_incident_form(self, incident_id, is_pending):
        """Opens the caller window and loads the existing data."""
        self.incident_window = EKABTopRow()
        
        # Inject Operator Username (We don't inject the time because it's an old record)
        if hasattr(self, 'current_username') and self.current_username:
            self.incident_window.operator_input.setText(self.current_username)
            
        # Call the new load function to pull data from the DB!
        self.incident_window.load_incident(incident_id, is_pending)
        self.incident_window.show()

    def open_list_window(self):
        """Opens the Finalized Incidents History window."""
        self.list_window = IncidentListWindow()
        self.list_window.show()

    def lock_system(self):
        """Pops up the lock screen overlay."""
        dialog = UnlockDialog(self)
        dialog.exec() # .exec() freezes the main dashboard until the dialog is successfully closed


    def logout(self):
        """Asks for confirmation, then logs the user out and returns to the login screen."""
        reply = QMessageBox.question(
            self, 
            "Αποσύνδεση", 
            "Είστε σίγουροι ότι θέλετε να αποσυνδεθείτε;",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            from log_in_ui import LoginWindow
            
            # Using 'global' prevents Python from deleting the login window when the dashboard closes!
            global active_login_window
            active_login_window = LoginWindow()
            active_login_window.show()
            
            # Now it is safe to close the dashboard
            self.close()
    def load_pending_incidents(self):
        """Loads pending incidents from today's database into the bottom table."""
        today_date = datetime.now().strftime("%Y-%m-%d")
        db_filename = f"incidents_{today_date}.db"
        
        # If the file doesn't exist yet, there are no incidents to load
        if not os.path.exists(db_filename):
            return 
            
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        
        try:
            # Select the columns from the database that match our table headers
            cursor.execute("""
                SELECT id, card_code, timestamp, type_of_incident, address, 
                       municipality_region, adress_num, patient_last_name, 
                       patient_name, symptoms, phone_1, sector 
                FROM pending_incidents
            """)
            rows = cursor.fetchall()
            
            # Clear existing rows so we don't duplicate them on refresh
            self.pending_table.setRowCount(0) 
            
            for row_idx, row_data in enumerate(rows):
                self.pending_table.insertRow(row_idx)
                
                # Map SQLite row exactly to Table headers:
                # ["A/A", "Κωδ. Κάρτας", "Ημ/Ώρα", "Είδος Συμβάντος", "Διεύθυνση", "Δήμος", "Αριθμός", "Επώνυμο", "Όνομα", "Σημειώσεις", "Τηλέφωνα", "Αιτιολογία", "Αφετηρία"]
                table_data = [
                    str(row_data[0]),                                  # A/A (id)
                    str(row_data[1] if row_data[1] else ""),           # Κωδ. Κάρτας
                    str(row_data[2] if row_data[2] else ""),           # Ημ/Ώρα
                    str(row_data[3] if row_data[3] else ""),           # Είδος Συμβάντος
                    str(row_data[4] if row_data[4] else ""),           # Διεύθυνση
                    str(row_data[5] if row_data[5] else ""),           # Δήμος
                    str(row_data[6] if row_data[6] else ""),           # Αριθμός
                    str(row_data[7] if row_data[7] else ""),           # Επώνυμο
                    str(row_data[8] if row_data[8] else ""),           # Όνομα
                    str(row_data[9] if row_data[9] else ""),           # Σημειώσεις (symptoms)
                    str(row_data[10] if row_data[10] else ""),         # Τηλέφωνα
                    "",                                                # Αιτιολογία (Placeholder for now)
                    str(row_data[11] if row_data[11] else "")          # Αφετηρία (sector)
                ]
                
                # Insert each piece of data into the respective column
                for col_idx, text in enumerate(table_data):
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.pending_table.setItem(row_idx, col_idx, item)
                    
        except sqlite3.OperationalError:
            # If the database exists but the table isn't created yet, quietly pass
            pass
        finally:
            conn.close()

    def refresh_all_tables(self):
        """Fetches fresh data for both pending and current tables simultaneously."""
        self.load_pending_incidents()
        self.load_current_incidents()

    def load_current_incidents(self):
        """Loads sent incidents from today's database into the top table."""
        today_date = datetime.now().strftime("%Y-%m-%d")
        db_filename = f"incidents_{today_date}.db"
        
        if not os.path.exists(db_filename):
            return 
            
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        
        try:
            # We select the columns matching the top table headers
            cursor.execute("""
                SELECT id, card_code, emergency, priority, timestamp, 
                       ambulance_number, type_of_incident, municipality_region, 
                       address, adress_num, hospital_name, patient_last_name, 
                       patient_name, symptoms 
                FROM sent_incidents
            """)
            rows = cursor.fetchall()
            
            self.current_table.setRowCount(0) 
            
            for row_idx, row_data in enumerate(rows):
                self.current_table.insertRow(row_idx)
                
                # Format the "Emergency" boolean into NAI/OXI
                is_emergency = "ΝΑΙ" if row_data[2] else "ΟΧΙ"
                
                # Map SQLite row exactly to the top Table headers:
                table_data = [
                    str(row_data[0]),                                  # A/A
                    str(row_data[1] if row_data[1] else ""),           # Κωδ. Κάρτας
                    is_emergency,                                      # Επείγον
                    str(row_data[3] if row_data[3] else ""),           # Ανταπόκριση
                    "Ενεργό",                                          # Κατάσταση (Default label for sent)
                    str(row_data[4] if row_data[4] else ""),           # Ημ/Ώρα
                    str(row_data[5] if row_data[5] else ""),           # Ασθενοφόρο
                    str(row_data[6] if row_data[6] else ""),           # Είδος Συμβάντος
                    str(row_data[7] if row_data[7] else ""),           # Δήμος
                    str(row_data[8] if row_data[8] else ""),           # Διεύθυνση
                    str(row_data[9] if row_data[9] else ""),           # Αριθμός
                    str(row_data[10] if row_data[10] else ""),         # Νοσοκομείο
                    str(row_data[11] if row_data[11] else ""),         # Επώνυμο
                    str(row_data[12] if row_data[12] else ""),         # Όνομα
                    str(row_data[13] if row_data[13] else "")          # Σημειώσεις
                ]
                
                for col_idx, text in enumerate(table_data):
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Apply color coding to the "Ανταπόκριση" column just like the original dummy data!
                    if col_idx == 3:
                        if text == "ΚΑΝΟΝΙΚΗ":
                            item.setBackground(QBrush(QColor("#8FBC8F")))
                        elif text == "ΕΠΕΙΓΟΥΣΑ":
                            item.setBackground(QBrush(QColor("#F4A460")))
                        elif text == "ΥΠΕΡΕΠΕΙΓ.":
                            item.setBackground(QBrush(QColor("#1E90FF")))
                            
                    self.current_table.setItem(row_idx, col_idx, item)
                    
        except sqlite3.OperationalError:
            pass
        finally:
            conn.close()

# ==========================================
# EXECUTE THE APP
# ==========================================
if __name__ == '__main__':
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    window = DispatcherDashboard()
    window.show()
    sys.exit(app.exec())