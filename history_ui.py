import sys
import os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QListWidget, QAbstractItemView,
    QDateTimeEdit, QGroupBox, QRadioButton, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QDateTime, QDate

class IncidentListWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ιστορικό Περιστατικών")
        self.resize(1600, 800)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # ==========================================
        # TOP FILTER SECTION
        # ==========================================
        filter_layout = QHBoxLayout()
        filter_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # --- COLUMN 1: Dates ---
        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Ημ/νία - Ώρα Κλήσης"))
        self.date_from = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_from.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.date_from.setCalendarPopup(True)
        col1.addWidget(QLabel("Από:"))
        col1.addWidget(self.date_from)
        
        self.date_to = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_to.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.date_to.setCalendarPopup(True)
        col1.addWidget(QLabel("Έως:"))
        col1.addWidget(self.date_to)
        
        self.btn_search = QPushButton("🔍 ΑΝΑΖΗΤΗΣΗ")
        self.btn_search.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px;")
        self.btn_search.clicked.connect(self.search_incidents)
        col1.addWidget(self.btn_search)
        col1.addStretch()
        filter_layout.addLayout(col1)

        # --- COLUMN 2: Basic Info ---
        col2_grid = QGridLayout()
        col2_grid.addWidget(QLabel("Καλών Όνομα:"), 0, 0)
        col2_grid.addWidget(QLineEdit(), 0, 1)
        col2_grid.addWidget(QLabel("Τηλέφωνο:"), 1, 0)
        col2_grid.addWidget(QLineEdit(), 1, 1)
        col2_grid.addWidget(QLabel("Κωδ. Κάρτας:"), 2, 0)
        self.filter_card = QLineEdit()
        col2_grid.addWidget(self.filter_card, 2, 1)
        col2_grid.addWidget(QLabel("Νοσοκομείο:"), 3, 0)
        col2_grid.addWidget(QComboBox(), 3, 1)
        
        col2_wrapper = QVBoxLayout()
        col2_wrapper.addLayout(col2_grid)
        col2_wrapper.addStretch()
        filter_layout.addLayout(col2_wrapper)

        # --- COLUMN 3: Patient Info ---
        col3_grid = QGridLayout()
        col3_grid.addWidget(QLabel("Πάσχων Όνομα:"), 0, 0)
        col3_grid.addWidget(QLineEdit(), 0, 1)
        col3_grid.addWidget(QLabel("Επώνυμο:"), 1, 0)
        self.filter_lastname = QLineEdit()
        col3_grid.addWidget(self.filter_lastname, 1, 1)
        col3_grid.addWidget(QLabel("Τηλέφωνο:"), 2, 0)
        col3_grid.addWidget(QLineEdit(), 2, 1)
        col3_grid.addWidget(QLabel("Οδός:"), 3, 0)
        col3_grid.addWidget(QLineEdit(), 3, 1)
        
        col3_wrapper = QVBoxLayout()
        col3_wrapper.addLayout(col3_grid)
        col3_wrapper.addStretch()
        filter_layout.addLayout(col3_wrapper)

        # --- BLUE DROPDOWN LISTS ---
        def create_blue_dropdown(title, items):
            layout = QVBoxLayout()
            layout.addWidget(QLabel(title))
            
            combo = QComboBox()
            # We add "Όλα" (All) as the default first option so the filter isn't forced
            combo.addItems(["Όλα"] + items) 
            
            # Keep the signature EKAB blue styling
            combo.setStyleSheet("""
                QComboBox { 
                    background-color: #0066CC; 
                    color: white; 
                    font-weight: bold; 
                    padding: 4px;
                    border: 1px solid #004C99;
                }
                QComboBox QAbstractItemView { 
                    background-color: #ffffff;
                    color: #333333;
                    selection-background-color: #004C99; 
                }
            """)
            combo.setFixedWidth(150)
            layout.addWidget(combo)
            
            # Return both the layout and the combo box so we can read it later during search
            return layout, combo

        # Create the dropdowns and save them to variables so we can read their values later!
        sector_layout, self.filter_sector = create_blue_dropdown("Τομέας", ["ΑΕΡΟΔΡΟΜΙΟ", "ΘΕΣΣΑΛΟΝΙΚΗ", "ΗΜΑΘΙΑ", "ΚΙΛΚΙΣ", "ΠΕΛΛΑ", "ΠΙΕΡΙΑ"])
        muni_layout, self.filter_muni = create_blue_dropdown("Δήμος", ["ΑΒΔΕΛΛΑΣ", "ΑΒΔΗΡΩΝ", "ΑΓΙΑΣ", "ΘΕΣΣΑΛΟΝΙΚΗΣ", "ΚΑΛΑΜΑΡΙΑΣ"])
        amb_layout, self.filter_amb = create_blue_dropdown("Ασθενοφόρα", ["424-A1", "A.01", "A.02", "A.03", "A.04"])
        symp_layout, self.filter_symp = create_blue_dropdown("Συμπτώματα", ["ERCP", "A.E.E", "ΑΓΓΕΙΑΚΕΣ ΠΑΘΗΣΕΙΣ", "ΑΓΝΩΣΤΗ ΚΑΤΑΣΤΑΣΗ"])
        hist_layout, self.filter_hist = create_blue_dropdown("Ιστορικό", ["12", "(ΠΡΟΣΦΥΓΑΣ)", "ARDS", "BY PASS", "PARKINSON"])
        type_layout, self.filter_type = create_blue_dropdown("Είδος Συμβάντος", ["4", "AEE", "ΑΕΡΟΔΙΑΚΟΜΙΔΗ", "ΑΘΛΗΤΙΚΟ ΑΤΥΧΗΜΑ"])

        # --- NEW: Group the dropdowns into a neat 3x2 Grid! ---
        dropdown_grid = QGridLayout()
        dropdown_grid.setHorizontalSpacing(15) # Add a little breathing room between them
        
        # Row 0 (Top)
        dropdown_grid.addLayout(sector_layout, 0, 0)
        dropdown_grid.addLayout(muni_layout, 0, 1)
        dropdown_grid.addLayout(amb_layout, 0, 2)
        
        # Row 1 (Bottom)
        dropdown_grid.addLayout(symp_layout, 1, 0)
        dropdown_grid.addLayout(hist_layout, 1, 1)
        dropdown_grid.addLayout(type_layout, 1, 2)

        # Wrap the grid in a vertical layout with a stretch at the bottom 
        # so it aligns perfectly with the top of the other columns!
        dropdown_wrapper = QVBoxLayout()
        dropdown_wrapper.addLayout(dropdown_grid)
        dropdown_wrapper.addStretch()

        # Add the whole block to the main top row
        filter_layout.addLayout(dropdown_wrapper)
        
        # ---> MAGIC SPRING: Pushes all the columns tightly to the left! <---
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # ==========================================
        # BOTTOM TABLE SECTION
        # ==========================================
        self.table = QTableWidget()
        headers = [
            "A/A", "Κωδ. Κάρτας", "Ημ/νία Κλήσης", "Επείγον", "Είδος Συμβάντος",
            "Έγκυρο", "Ασθ/ρο", "Όνομα", "Επώνυμο", "Παραλαβή Από", "Οδός",
            "Αριθμός", "Δήμος", "Τομέας", "Προορισμός"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setStyleSheet("::section { background-color: #888888; color: white; font-weight: bold; border: 1px solid #666; }")
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        
        main_layout.addWidget(self.table)

    def search_incidents(self):
        """Iterates through the selected date range and fetches Finalized incidents from all available databases."""
        
        # 1. Get the Start and End dates
        start_date = self.date_from.date()
        end_date = self.date_to.date()
        
        # Safety check: make sure the user didn't accidentally put the start date after the end date
        if start_date > end_date:
            QMessageBox.warning(self, "Λάθος Ημερομηνία", "Η ημερομηνία 'Από' δεν μπορεί να είναι μεταγενέστερη της 'Έως'.")
            return

        # 2. Build the dynamic SQL query ONCE based on the typed/selected filters
        query = """
            SELECT id, card_code, timestamp, emergency, type_of_incident,
                   '', '', patient_name, patient_last_name, '', address, 
                   adress_num, municipality_region, sector, ''
            FROM finalized_incidents
            WHERE 1=1
        """
        params = []
        
        # --- Text Input Filters ---
        if self.filter_card.text().strip():
            query += " AND card_code = ?"
            params.append(self.filter_card.text().strip())
            
        if self.filter_lastname.text().strip():
            query += " AND patient_last_name LIKE ?"
            params.append(f"%{self.filter_lastname.text().strip()}%")

        # --- Dropdown Filters ---
        if self.filter_sector.currentText() != "Όλα":
            query += " AND sector = ?"
            params.append(self.filter_sector.currentText())

        if self.filter_muni.currentText() != "Όλα":
            query += " AND municipality_region = ?"
            params.append(self.filter_muni.currentText())

        if self.filter_type.currentText() != "Όλα":
            query += " AND type_of_incident = ?"
            params.append(self.filter_type.currentText())

        # 3. Loop through every day in the date range and collect the data
        all_rows = []
        current_date = start_date
        
        while current_date <= end_date:
            # Format the date to match your database naming convention
            date_str = current_date.toString("yyyy-MM-dd")
            db_filename = f"incidents_{date_str}.db"
            
            # If a database file exists for this specific day, connect and search it!
            if os.path.exists(db_filename):
                conn = sqlite3.connect(db_filename)
                cursor = conn.cursor()
                try:
                    cursor.execute(query, params)
                    all_rows.extend(cursor.fetchall()) # Add this day's results to the master list
                except sqlite3.OperationalError:
                    # If the database exists but doesn't have a finalized table yet, just skip it
                    pass
                finally:
                    conn.close()
            
            # Move forward exactly one day
            current_date = current_date.addDays(1)

        # 4. Populate the UI Table with the combined results
        self.table.setRowCount(0)
        
        if not all_rows:
            QMessageBox.information(self, "Αποτέλεσμα", "Δεν βρέθηκαν αποτελέσματα για αυτό το χρονικό διάστημα και τα φίλτρα.")
            return
            
        for row_idx, row_data in enumerate(all_rows):
            self.table.insertRow(row_idx)
            for col_idx, text in enumerate(row_data):
                item = QTableWidgetItem(str(text) if text is not None else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = IncidentListWindow()
    window.show()
    sys.exit(app.exec())