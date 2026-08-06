import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt,QDateTime
from PyQt6.QtGui import QColor, QBrush  # <--- ADD THIS LINE

from caller import EKABTopRow

class DispatcherDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Τηλεφωνητής - ΕΚΑΒ ΘΕΣΣΑΛΟΝΙΚΗΣ")
        self.resize(1400, 800)
        self.setup_ui()
        
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
        # Using placeholder text/emojis for the icons in the image
        self.btn_list = QPushButton("📄\nΛίστα")
        self.btn_list.setFixedSize(60, 60)
        
        self.btn_new = QPushButton("📝+\nΝέο")
        self.btn_new.setFixedSize(60, 60)

        self.btn_new.clicked.connect(self.open_new_incident_form)

        
        
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
        
        self.btn_logout = QPushButton("⏻")
        self.btn_logout.setFixedSize(50, 50)
        
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
        
        splitter.addWidget(bottom_widget)
        
        # Set the top table to take up more space initially (e.g., 70% top, 30% bottom)
        splitter.setSizes([700, 300])

        main_layout.addWidget(splitter)

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
        """Opens the New Incident form and stamps current time and position."""
        # 1. Create the window
        self.incident_window = EKABTopRow()
        
        # 2. Get exact current date and time
        now = QDateTime.currentDateTime()
        current_date = now.toString("dd/MM/yyyy")
        current_time = now.toString("HH:mm")
        
        # 3. Inject Date and Time
        self.incident_window.date_input.setText(current_date)
        self.incident_window.time_input.setText(current_time)
        
        # 4. Inject the Position Number (if they logged in as ΤΗΛΕΦΩΝΗΤΗΣ)
        if hasattr(self, 'shift_position') and self.shift_position:
            self.incident_window.desk_input.setText(self.shift_position)
            
        # 5. Show the window
        self.incident_window.show()


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