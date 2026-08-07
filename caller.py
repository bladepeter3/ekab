import sys
import webbrowser
import urllib.parse
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QCheckBox, QGridLayout, QRadioButton, QDateTimeEdit, QGroupBox,
    QStackedWidget,QTextEdit,QScrollArea,QCompleter
)
from PyQt6.QtCore import Qt, QDateTime,QObject, QEvent,QTimer,QUrl,QStringListModel
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# --- SQLAlchemy Imports ---
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Date, Time, func
from sqlalchemy.orm import declarative_base, sessionmaker

# ==========================================
# 1. DATABASE SETUP (SQLAlchemy)
# ==========================================

Base = declarative_base()

class TimeFieldFilter(QObject):
    def eventFilter(self, obj, event):
        # Check if the user clicked the mouse on the text box
        if event.type() == QEvent.Type.MouseButtonPress:
            # If the box still shows "00:00" or is empty, insert the current time
            if obj.text() == "00:00" or obj.text() == "":
                current_time = QDateTime.currentDateTime().toString("HH:mm")
                obj.setText(current_time)
                obj.selectAll() # Highlights the text for easy editing
            return True
        return super().eventFilter(obj, event)

class IncidentMixin:
    
    id = Column(Integer, primary_key=True)
    card_code = Column(Integer, default=0)
    datestamp = Column(Date, default=lambda: datetime.now().date())
    timestamp = Column(String(5), default=lambda: datetime.now().strftime("%H:%M"))
    position = Column(Integer, default=0)
    operator_name = Column(String(100))
    emergency = Column(Boolean, default=False)
    from_address_check = Column(Boolean, default=True)
    from_medical_facility_check = Column(Boolean, default=False)
    from_icu_check = Column(Boolean, default=False)
    from_air_sea_check = Column(Boolean, default=False)
    sector=Column(String(20), default="Unknown")
    visible_all_check= Column(Boolean, default=False)
    program_from = Column(String(16), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    filter_by_municipality = Column(Boolean, default=False)
    address = Column(String(250))
    adress_num=Column(String(20))
    floor_num=Column(String(20))
    name_intercom=Column(String(50))
    municipality_region=Column(String(50))
    precision_address=Column(String(250))
    doctor_escort_check=Column(Boolean, default=False)
    patient_last_name = Column(String(100))
    patient_name = Column(String(100))
    patient_age = Column(Integer)
    age_unit = Column(String(10))  
    newborn_check = Column(Boolean, default=False)
    patient_gender = Column(String(10))
    unknown_patient_check = Column(Boolean, default=False)
    insurance = Column(String(100))
    phone_1 = Column(String(20))
    phone_2 = Column(String(20))
    phone_3 = Column(String(20))
    call_from = Column(String(100)) 
    caller_info = Column(String(100))
    loss_of_breath = Column(Boolean, default=False)
    loss_of_sensation = Column(Boolean, default=False)
    loss_of_consciousness = Column(Boolean, default=False)
    hemmorage = Column(Boolean, default=False)
    transportation = Column(String(100))
    type_of_incident = Column(String(100))
    symptoms = Column(String(1000))
    medical_history = Column(String(1000))
    contact_with_doctor = Column(Boolean, default=False)
    priority = Column(String(50))
    notes = Column(String(1000))
    timestamp_card_received = Column(String(5), default=lambda: datetime.now().strftime("%H:%M"))
    radio_operator_name = Column(String(100))
    radio_operator_id = Column(Integer,default=0)
    ambulance_number = Column(String(20))
    ambulance_position = Column(String(100))
    timestamp_dispatch = Column(String(5), default=lambda: datetime.now().strftime("%H:%M"))
    timestamp_arrival_incident = Column(String(5), default=lambda: datetime.now().strftime("%H:%M"))
    timestamp_leaving_incident = Column(String(5), default=lambda: datetime.now().strftime("%H:%M"))
    timestamp_arrival_hospital = Column(String(5), default=lambda: datetime.now().strftime("%H:%M"))
    timestamp_end = Column(String(5), default=lambda: datetime.now().strftime("%H:%M"))
    timestamp_refusal = Column(String(16), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    reason_of_refusal = Column(String(100))
    comment_of_refusal = Column(String(1000))
    name_of_refusal = Column(String(100))
    last_name_of_refusal = Column(String(100))
    destination_type = Column(String(100))
    hospital_name = Column(String(100))
    hospital_specialty = Column(String(100))
    doctor_waiting = Column(String(100))
    other_departments = Column(String(100))
    department_in_charge = Column(String(100))
    siren_check = Column(Boolean, default=False)
    instruction_BLS = Column(Boolean, default=False)
    blood_pressure = Column(Integer)
    heart_rate = Column(Integer)
    spo2 = Column(Integer)
    avpu = Column(String(10))
    sms=Column(String(20))
    condition_from_emt = Column(String(1000))
    approach_from_emt = Column(String(1000))
    notes_from_emt = Column(String(1000))

class SentIncident(IncidentMixin, Base):
    __tablename__ = 'sent_incidents'

class PendingIncident(IncidentMixin, Base):
    __tablename__ = 'pending_incidents'

class FinalizedIncident(IncidentMixin, Base):
    __tablename__ = 'finalized_incidents'

# ==========================================
# 2. GUI SETUP (PyQT6)
# ==========================================

class EKABTopRow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Εισαγωγή Περιστατικού")
        self.resize(1600, 500)
        self.setMinimumSize(1400, 400)
        self.setup_ui()

    def open_google_maps(self):
        """Gathers the address fields and opens Google Maps in the web browser."""
        street = self.street_input.text().strip()
        number = self.number_input.text().strip()
        municipality = self.municipality_combo.currentText().strip()
        
        # Combine fields into a clean search query
        query_parts = [street, number, municipality, "Ελλάδα"]
        full_address = ", ".join([p for p in query_parts if p])
        
        if not full_address or full_address == "Ελλάδα":
            QMessageBox.warning(self, "Προσοχή", "Συμπληρώστε τουλάχιστον την οδό ή τον δήμο για να ανοίξει ο χάρτης.")
            return
            
        # Encode for URL and open Google Maps
        encoded_query = urllib.parse.quote(full_address)
        url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"
        webbrowser.open(url)

    def fetch_address_suggestions(self):
        """Sends a query to fetch real-time address suggestions based on typed text."""
        text = self.street_input.text().strip()
        if len(text) < 3: # Only search if at least 3 characters are typed
            return
            
        # Target Greece/Thessaloniki region
        query = urllib.parse.quote(f"{text}, Θεσσαλονίκη, Ελλάδα")
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1&limit=5"
        
        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.KnownHeaders.UserAgentHeader, "EKABDispatchApp/1.0")
        self.network_manager.get(request)

    def handle_address_suggestions(self, reply: QNetworkReply):
        """Receives suggestions from the map service, extracts streets and municipalities."""
        if reply.error() == QNetworkReply.NetworkError.NoError:
            try:
                data = json.loads(reply.readAll().data().decode('utf-8'))
                suggestions = []
                self.address_municipality_map.clear()
                
                for item in data:
                    display_name = item.get('display_name', '')
                    address_details = item.get('address', {})
                    
                    if display_name:
                        street_name = display_name.split(',')[0].strip()
                        suggestions.append(street_name)
                        
                        # Extract municipality, city, or suburb from the OpenStreetMap response
                        muni = (
                            address_details.get('municipality') or 
                            address_details.get('city') or 
                            address_details.get('town') or 
                            address_details.get('suburb') or ""
                        )
                        
                        # Store it in our map (converted to uppercase to match your combobox items)
                        if muni:
                            self.address_municipality_map[street_name] = muni.upper()
                
                self.completer_model.setStringList(list(set(suggestions)))
                if suggestions:
                    self.street_completer.complete()
            except Exception:
                pass
        reply.deleteLater()

    def on_address_selected(self, street_text):
        """Automatically selects the corresponding municipality when a street is chosen."""
        clean_street = street_text.strip()
        if clean_street in self.address_municipality_map:
            target_muni = self.address_municipality_map[clean_street]
            
            # Search inside your self.municipality_combo to see if the municipality exists there
            match_index = self.municipality_combo.findText(target_muni, Qt.MatchFlag.MatchContains)
            if match_index >= 0:
                self.municipality_combo.setCurrentIndex(match_index)
            else:
                # If it's a municipality not currently in your static list, add it dynamically!
                self.municipality_combo.addItem(target_muni)
                self.municipality_combo.setCurrentText(target_muni)


                
    def setup_ui(self):
# 1. Create the master layout for the window
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0) # No borders around the scroll bar

# 2. Create the Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True) # IMPORTANT: Lets the inner canvas expand!
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        # 3. Create the "Canvas" widget that will hold all your UI elements
        scroll_content = QWidget()
        
        # 4. Master Horizontal Layout to hold Left and Right sides side-by-side
        master_layout = QHBoxLayout(scroll_content)
        master_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        master_layout.setContentsMargins(10, 10, 10, 10)
        master_layout.setSpacing(40) # Slightly increased spacing so they don't touch

        # 5. Left Side Layout (We keep the name 'main_layout' so your existing code works perfectly!)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(12)
        
        # 6. Right Side Layout (This is where our new right-side stuff will go)
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_layout.setSpacing(12)

        # Add both columns to the master horizontal layout
        master_layout.addLayout(main_layout)
        master_layout.addLayout(right_layout)

        # ---> ADD THIS MAGIC SPRING: It absorbs all extra screen space on the right! <---
        master_layout.addStretch()
        
        grid = QGridLayout()
        grid.setSpacing(5) 
        grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # ROW 0
        grid.addWidget(QLabel("ΚΩΔΙΚΟΣ ΚΑΡΤΑΣ"), 0, 0)
        grid.addWidget(QLabel("ΗΜΕΡΟΜΗΝΙΑ"), 0, 1, 1, 2)
        grid.addWidget(QLabel("ΩΡΑ ΚΛΗΣΗΣ"),0,2,1,1)
        grid.addWidget(QLabel("ΘΕΣΗ"), 0, 3)
        grid.addWidget(QLabel("ΤΗΛΕΦΩΝΗΤΗΣ"), 0, 4)
        
        # ROW 1
        self.card_input = QLineEdit()
        self.date_input = QLineEdit()
        self.time_input = QLineEdit()
        self.desk_input = QLineEdit()
        self.operator_input = QLineEdit()
    
        self.card_input.setMaximumWidth(95)
        self.date_input.setMaximumWidth(90)
        self.time_input.setMaximumWidth(75)
        self.desk_input.setMaximumWidth(30)
        self.operator_input.setMaximumWidth(260)
        
        grid.addWidget(self.card_input, 1, 0)
        grid.addWidget(self.date_input, 1, 1) 
        grid.addWidget(self.time_input, 1, 2) 
        grid.addWidget(self.desk_input, 1, 3)
        grid.addWidget(self.operator_input, 1, 4)

        # ---> ADD THIS LINE: Pushes columns 0-4 tightly to the left! <---
        grid.setColumnStretch(5, 1)
        
        main_layout.addLayout(grid)

        # ROW 2
        row2_layout = QHBoxLayout()
        row2_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        
        self.emergency_check = QCheckBox("ΕΠΕΙΓΟΝ")
        
        self.sector_combo = QComboBox()
        self.sector_combo.addItems(["", "ΗΜΑΘΙΑ", "ΘΕΣΣΑΛΟΝΙΚΗ", "ΚΙΛΚΙΣ","ΠΕΛΛΑ","ΠΕΡΙΦΕΡΕΙΑ","ΠΙΕΡΙΑ","ΣΥΝΤΟΝΙΣΤΗΣ","ΧΑΛΚΙΔΙΚΗ","ΧΡΟΝΙΑ","ΧΡΟΝΙΑ ΚΙΛΚΙΣ","ΧΡΟΝΙΑ ΧΑΛΚΙΔΙΚΗΣ"])
        self.sector_combo.setMinimumWidth(100)
        
        self.visible_check = QCheckBox("ΕΜΦΑΝΙΣΗ ΣΕ ΟΛΟΥΣ")
        
        row2_layout.addWidget(self.emergency_check)
        row2_layout.addSpacing(20) 
        row2_layout.addWidget(QLabel("*ΤΟΜΕΑΣ"))
        row2_layout.addWidget(self.sector_combo)
        row2_layout.addSpacing(20)
        row2_layout.addWidget(self.visible_check)
        
        main_layout.addLayout(row2_layout)

        # ROW 3
        row3_layout = QHBoxLayout()
        row3_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row3_layout.setContentsMargins(0, 0, 0, 0)
        
        row3_layout.addWidget(QLabel("ΠΑΡΑΛΑΒΗ ΑΠΟ "))
        
        self.radio_address = QRadioButton("Δ/ΝΣΗ")
        self.radio_address.setChecked(True) 
        self.radio_health = QRadioButton("ΥΓΕΙΟΝ.\nΣΧΗΜ.")
        self.radio_icu = QRadioButton("Μ.Ε.Θ.")
        self.radio_port_air = QRadioButton("ΛΙΜΑΝΙ\nΑΕΡΟΔΡΟΜΙΟ")

        # Connect all 4 buttons!
        self.radio_address.toggled.connect(self.switch_pickup_view)
        self.radio_health.toggled.connect(self.switch_pickup_view)
        self.radio_icu.toggled.connect(self.switch_pickup_view)
        self.radio_port_air.toggled.connect(self.switch_pickup_view)
        
        row3_layout.addWidget(self.radio_address)
        row3_layout.addWidget(self.radio_health)
        row3_layout.addWidget(self.radio_icu)
        row3_layout.addWidget(self.radio_port_air)
        
        row3_layout.addSpacing(1)
        row3_layout.addWidget(QLabel("ΠΡΟΓΡΑΜ."))
        
        self.program_input = QDateTimeEdit()
        self.program_input.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.program_input.setCalendarPopup(True) 
        self.program_input.setFixedWidth(140)
        self.program_input.setMinimumDateTime(QDateTime.currentDateTime())
        self.program_input.setSpecialValueText(" ")
        self.program_input.setDateTime(self.program_input.minimumDateTime())
        
        row3_layout.addWidget(self.program_input)   
        main_layout.addLayout(row3_layout)


        # ==========================================
        # SECTION: DYNAMIC PICKUP DETAILS (Stacked Widget)
        # ==========================================
        self.pickup_stack = QStackedWidget()
        
        # ------------------------------------------
        # --- PAGE 0: Address Group (Δ/ΝΣΗ) ---
        # ------------------------------------------
        address_group = QGroupBox("ΣΤΟΙΧΕΙΑ ΠΑΡΑΛΑΒΗΣ")
        address_group.setAlignment(Qt.AlignmentFlag.AlignLeft)
        address_group.setStyleSheet("QGroupBox { font-weight: bold; color: #333333; }")
        
        addr_grid = QGridLayout()
        addr_grid.setContentsMargins(10, 10, 10, 10)
        addr_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        street_lbl_layout = QHBoxLayout()
        street_lbl_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        street_lbl_layout.setContentsMargins(0, 0, 0, 0)
        street_lbl_layout.addWidget(QLabel("*ΟΔΟΣ"))
        self.filter_muni_check = QCheckBox("ΦΙΛΤΡΑΡΙΣΜΑ ΜΕ ΒΑΣΗ ΤΟΝ ΔΗΜΟ")
        street_lbl_layout.addWidget(self.filter_muni_check)
        street_lbl_layout.addStretch()
        
        addr_grid.addLayout(street_lbl_layout, 0, 0, 1, 2)
        addr_grid.addWidget(QLabel("ΑΡΙΘΜΟΣ"), 0, 2)
        addr_grid.addWidget(QLabel("ΟΡΟΦΟΣ"), 0, 3)
        addr_grid.addWidget(QLabel("ΚΟΥΔΟΥΝΙ"), 0, 4)
        
        self.street_input = QLineEdit()
        self.street_input.setMaximumWidth(250)

        # --- Live Address Search Setup ---
        from PyQt6.QtWidgets import QCompleter
        from PyQt6.QtCore import QStringListModel
        
        self.completer_model = QStringListModel([], self)
        self.street_completer = QCompleter(self.completer_model, self)
        self.street_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.street_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.street_input.setCompleter(self.street_completer)
        
        # Network manager for fetching addresses live
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.handle_address_suggestions)
        
        # Timer to avoid spamming the server on every single keystroke (waits 400ms after typing stops)
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(400)
        self.search_timer.timeout.connect(self.fetch_address_suggestions)
        
        self.street_input.textChanged.connect(self.search_timer.start)

        addr_grid.addWidget(self.street_input, 1, 0)
        self.map_btn_1 = QPushButton("🗺️") 
        self.map_btn_1.setFixedWidth(30)
        self.map_btn_1.clicked.connect(self.open_google_maps)
        addr_grid.addWidget(self.map_btn_1, 1, 1)
        self.number_input = QLineEdit()
        self.number_input.setFixedWidth(50)
        addr_grid.addWidget(self.number_input, 1, 2)
        self.floor_combo = QComboBox()
        self.floor_combo.addItems(["","ΥΠΟΓΕΙΟ", "ΙΣΟΓΕΙΟ","ΗΜΙΟΡΟΦΟΣ", "1ος", "2ος", "3ος", "4ος", "5ος", "6ος"])
        self.floor_combo.setMaximumWidth(100)
        addr_grid.addWidget(self.floor_combo, 1, 3)
        self.bell_input = QLineEdit()
        self.bell_input.setFixedWidth(200)
        addr_grid.addWidget(self.bell_input, 1, 4)
        
        addr_grid.addWidget(QLabel("*ΔΗΜΟΣ/ΠΕΡΙΟΧΗ"), 2, 0, 1, 2)
        addr_grid.addWidget(QLabel("*ΑΚΡΙΒΕΣ ΣΗΜΕΙΟ"), 2, 2, 1, 2)
        addr_grid.addWidget(QLabel("ΣΥΝΟΔΕΙΑ ΓΙΑΤΡΟΥ"), 2, 4)
        
        self.municipality_combo = QComboBox()
        self.municipality_combo.addItems(["", "ΘΕΣΣΑΛΟΝΙΚΗ", "ΚΑΛΑΜΑΡΙΑ", "ΕΥΟΣΜΟΣ"])
        addr_grid.addWidget(self.municipality_combo, 3, 0, 1, 2)
        self.exact_spot_input = QLineEdit()
        addr_grid.addWidget(self.exact_spot_input, 3, 2, 1, 2)
        self.doctor_escort_check_1 = QCheckBox() 
        addr_grid.addWidget(self.doctor_escort_check_1, 3, 4)
        
        address_group.setLayout(addr_grid)
        self.pickup_stack.addWidget(address_group)
        

        # ------------------------------------------
        # --- PAGE 1: Hospital Group (ΥΓΕΙΟΝ. ΣΧΗΜ.) ---
        # ------------------------------------------
        health_group = QGroupBox("ΣΤΟΙΧΕΙΑ ΠΑΡΑΛΑΒΗΣ (ΝΟΣΟΚΟΜΕΙΟ)")
        health_group.setAlignment(Qt.AlignmentFlag.AlignLeft)
        health_group.setStyleSheet("QGroupBox { font-weight: bold; color: #333333; }")
        
        health_grid = QGridLayout()
        health_grid.setContentsMargins(10, 10, 10, 10)
        health_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        health_grid.addWidget(QLabel("*ΥΓΕΙΟΝΟΜΙΚΟΣ ΣΧΗΜΑΤΙΣΜΟΣ"), 0, 0, 1, 2)

        self.health_org_combo = QComboBox()
        self.health_org_combo.addItems(["","251 ΓΕΝΙΚΟ ΝΟΣΟΚΟΜΕΙΟ ΑΕΡΟΠΟΡΙΑΣ", "401 Σ.Ν.Α.","414 Σ.Ν.ΘΩΡΑΚΟΣ ΠΕΝΤΕΛΗΣ", "424 Σ.Ν.Θ."])
        self.health_org_combo.setMaximumWidth(250)
        health_grid.addWidget(self.health_org_combo, 1, 0)
        self.map_btn_2 = QPushButton("🗺️") 
        self.map_btn_2.setFixedWidth(30)
        health_grid.addWidget(self.map_btn_2, 1, 1)
        
        health_grid.addWidget(QLabel("ΚΛΙΝΙΚΗ"), 2, 0, 1, 2)
        health_grid.addWidget(QLabel("ΜΟΝΑΔΑ"), 2, 2, 1, 2)
        health_grid.addWidget(QLabel("ΣΥΝΟΔΕΙΑ\nΓΙΑΤΡΟΥ"), 2, 4)
        
        self.health_sector_combo = QComboBox()
        self.health_sector_combo.addItems(["", "ΝΕΦΡΟΛΟΓΙΚΗ", "ΚΑΡΔΙΟΛΟΓΙΚΗ", "ΝΕΥΡΟΛΟΓΙΚΗ", "ΧΕΙΡΟΥΡΓΙΚΗ"])
        health_grid.addWidget(self.health_sector_combo, 3, 0, 1, 2)
        self.unit_escort_check_1 = QCheckBox() # Renamed
        health_grid.addWidget(self.unit_escort_check_1, 3, 2, 1, 2)
        self.doctor_escort_check_2 = QCheckBox() 
        health_grid.addWidget(self.doctor_escort_check_2, 3, 4)
        
        health_group.setLayout(health_grid)
        self.pickup_stack.addWidget(health_group)

        # ------------------------------------------
        # --- PAGE 2: ICU Group (Μ.Ε.Θ.) ---
        # ------------------------------------------
        icu_group = QGroupBox("ΣΤΟΙΧΕΙΑ ΠΑΡΑΛΑΒΗΣ (Μ.Ε.Θ.)")
        icu_group.setAlignment(Qt.AlignmentFlag.AlignLeft)
        icu_group.setStyleSheet("QGroupBox { font-weight: bold; color: #333333; }")
        
        icu_grid = QGridLayout()
        icu_grid.setContentsMargins(10, 10, 10, 10)
        icu_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        icu_grid.addWidget(QLabel("*ΥΓΕΙΟΝΟΜΙΚΟΣ ΣΧΗΜΑΤΙΣΜΟΣ"), 0, 0, 1, 2)

        self.icu_combo = QComboBox()
        self.icu_combo.addItems(["","251 ΓΕΝΙΚΟ ΝΟΣΟΚΟΜΕΙΟ ΑΕΡΟΠΟΡΙΑΣ", "401 Σ.Ν.Α.","414 Σ.Ν.ΘΩΡΑΚΟΣ ΠΕΝΤΕΛΗΣ", "424 Σ.Ν.Θ."])
        self.icu_combo.setMaximumWidth(250)
        icu_grid.addWidget(self.icu_combo, 1, 0)
        self.map_btn_3 = QPushButton("🗺️") # Renamed
        self.map_btn_3.setFixedWidth(30)
        icu_grid.addWidget(self.map_btn_3, 1, 1)
        
        icu_grid.addWidget(QLabel("ΚΛΙΝΙΚΗ"), 2, 0, 1, 2)
        icu_grid.addWidget(QLabel("ΜΟΝΑΔΑ"), 2, 2, 1, 2)
        icu_grid.addWidget(QLabel("ΣΥΝΟΔΕΙΑ\nΓΙΑΤΡΟΥ"), 2, 4)
        
        self.icu_sector_combo = QLabel("ΜΕΘ") 
        icu_grid.addWidget(self.icu_sector_combo, 3, 0, 1, 2)
        self.unit_escort_check_2 = QCheckBox() # Renamed
        icu_grid.addWidget(self.unit_escort_check_2, 3, 2, 1, 2)
        self.doctor_escort_check_3 = QCheckBox() # Renamed
        icu_grid.addWidget(self.doctor_escort_check_3, 3, 4)
        
        icu_group.setLayout(icu_grid)
        self.pickup_stack.addWidget(icu_group)

        # ------------------------------------------
        # --- PAGE 3: Airport or port Group (ΑΕΡΟΔΡΟΜΙΟ ΛΙΜΑΝΙ) ---
        # ------------------------------------------
        ports_group = QGroupBox("ΣΤΟΙΧΕΙΑ ΠΑΡΑΛΑΒΗΣ (ΑΕΡΟΔΡΟΜΙΟ / ΛΙΜΑΝΙ)")
        ports_group.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ports_group.setStyleSheet("QGroupBox { font-weight: bold; color: #333333; }")
        
        ports_grid = QGridLayout()
        ports_grid.setContentsMargins(10, 10, 10, 10)
        ports_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # --- ROW 0: Labels ---
        ports_grid.addWidget(QLabel("*ΛΙΜΑΝΙ/ΑΕΡΟΔΡΟΜΙΟ"), 0, 0, 1, 2)
        ports_grid.addWidget(QLabel("*ΑΦΙΞΗ ΑΠΟ"), 0, 2, 1, 2)

        # --- ROW 1: Inputs ---
        self.port_org_combo = QComboBox()
        self.port_org_combo.addItems(["","ΛΙΜΑΝΙ ΘΕΣΣΑΛΟΝΙΚΗΣ", "ΑΕΡΟΔΡΟΜΙΟ ΘΕΣΣΑΛΟΝΙΚΗΣ"])
        self.port_org_combo.setMaximumWidth(250)
        ports_grid.addWidget(self.port_org_combo, 1, 0)
        
        self.map_btn_4 = QPushButton("🗺️") 
        self.map_btn_4.setFixedWidth(30)
        ports_grid.addWidget(self.map_btn_4, 1, 1)
        
        self.port_arrival_combo = QComboBox()
        self.port_arrival_combo.addItems(["","ΛΙΜΑΝΙ ΑΘΗΝΑΣ", "ΑΕΡΟΔΡΟΜΙΟ ΑΘΗΝΑΣ"])
        self.port_arrival_combo.setMaximumWidth(250)    
        ports_grid.addWidget(self.port_arrival_combo, 1, 2)

        # --- ROW 2: Labels ---
        ports_grid.addWidget(QLabel("*ΗΜΕΡΟΜΗΝΙΑ ΑΦΙΞΗΣ"), 2, 0, 1, 2)
        ports_grid.addWidget(QLabel("ΑΛΛΑ ΣΤΟΙΧΕΙΑ"), 2, 2, 1, 2)
        
        # ---> HERE IS YOUR DOCTOR ESCORT LABEL <---
        ports_grid.addWidget(QLabel("ΣΥΝΟΔΕΙΑ ΓΙΑΤΡΟΥ"),2,3,alignment=Qt.AlignmentFlag.AlignLeft) 

        # --- ROW 3: Inputs ---
        self.port_date_input = QDateTimeEdit()
        self.port_date_input.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.port_date_input.setCalendarPopup(True) 
        self.port_date_input.setFixedWidth(140)
        self.port_date_input.setMinimumDateTime(QDateTime.currentDateTime())
        self.port_date_input.setSpecialValueText(" ")
        self.port_date_input.setDateTime(self.port_date_input.minimumDateTime())
        ports_grid.addWidget(self.port_date_input, 3, 0)
        
        self.port_other_info_input = QLineEdit()
        self.port_other_info_input.setMaximumWidth(250) 
        ports_grid.addWidget(self.port_other_info_input, 3, 2)

        # ---> HERE IS YOUR DOCTOR ESCORT CHECKBOX <---
        self.doctor_escort_check_4 = QCheckBox() 
        ports_grid.addWidget(self.doctor_escort_check_4, 3, 3, alignment=Qt.AlignmentFlag.AlignLeft)
                
        # -> Add Page 3 to Stack
        ports_group.setLayout(ports_grid)
        self.pickup_stack.addWidget(ports_group)
        
        # ------------------------------------------
        # --- FINALIZE LAYOUT ---
        # ------------------------------------------
        
        # 1. Add the stack WITHOUT the 'AlignLeft' restriction so it can stretch and center!
        main_layout.addWidget(self.pickup_stack)

       # ==========================================
        # SECTION: ΔΗΜΟΓΡΑΦΙΚΑ ΣΤΟΙΧΕΙΑ (Demographics)
        # ==========================================
        demo_group = QGroupBox("ΔΗΜΟΓΡΑΦΙΚΑ ΣΤΟΙΧΕΙΑ")
        demo_group.setAlignment(Qt.AlignmentFlag.AlignLeft)
        demo_group.setStyleSheet("QGroupBox { font-weight: bold; color: #333333; margin-top: 10px; }")
        
        # We will use a Vertical Layout for the box, and put a Grid + Horizontal Layouts inside it
        demo_layout = QVBoxLayout()
        demo_layout.setContentsMargins(10, 10, 10, 10)
        demo_layout.setSpacing(8)

        # --- ROWS 0 & 1: Names, Age, Newborn (Using a Grid) ---
        demo_grid = QGridLayout()
        demo_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        demo_grid.setContentsMargins(0, 0, 0, 0)
        
        # Row 0: Labels
        eponymo_layout = QHBoxLayout()
        eponymo_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        eponymo_layout.setContentsMargins(0, 0, 0, 0)
        eponymo_layout.addWidget(QLabel("ΕΠΩΝΥΜΟ"))
        
        self.contact_btn = QPushButton("📇") # Small icon next to Last Name
        self.contact_btn.setFixedWidth(24)
        eponymo_layout.addWidget(self.contact_btn)
        
        demo_grid.addLayout(eponymo_layout, 0, 0)
        demo_grid.addWidget(QLabel("ΟΝΟΜΑ"), 0, 1)
        demo_grid.addWidget(QLabel("ΗΛΙΚΙΑ"), 0, 2)
        demo_grid.addWidget(QLabel("ΝΕΟΓΝΟ"), 0, 3, alignment=Qt.AlignmentFlag.AlignLeft)

        # Row 1: Inputs
        self.last_name_input = QLineEdit()
        self.last_name_input.setFixedWidth(200)
        demo_grid.addWidget(self.last_name_input, 1, 0)
        
        self.first_name_input = QLineEdit()
        self.first_name_input.setFixedWidth(200)
        demo_grid.addWidget(self.first_name_input, 1, 1)

        # Age layout (Box + Comma + Dropdown)
        age_layout = QHBoxLayout()
        age_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        age_layout.setContentsMargins(0, 0, 0, 0)
        self.age_input = QLineEdit()
        self.age_input.setFixedWidth(40)
        age_layout.addWidget(self.age_input)
        age_layout.addWidget(QLabel(""))
        self.age_unit_combo = QComboBox()
        self.age_unit_combo.addItems(["ΕΤΩΝ", "ΜΗΝΩΝ", "ΗΜΕΡΩΝ"]) # Ετών, Μηνών, Ημερών
        self.age_unit_combo.setFixedWidth(80)
        age_layout.addWidget(self.age_unit_combo)
        
        demo_grid.addLayout(age_layout, 1, 2)
        
        self.newborn_check = QCheckBox()
        demo_grid.addWidget(self.newborn_check, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)

        # --> THIS IS THE MAGIC SPRING: It pushes columns 0, 1, 2, and 3 tightly to the left!
        demo_grid.setColumnStretch(4, 1)

        # Add the grid to the main Demographics layout
        demo_layout.addLayout(demo_grid)

        # --- ROW 2: Unknown & Gender ---
        row2_demo = QHBoxLayout()
        row2_demo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row2_demo.setContentsMargins(0, 5, 0, 0) 
        
        row2_demo.addWidget(QLabel("ΑΓΝΩΣΤΟΣ"))
        self.unknown_patient_check = QCheckBox()
        row2_demo.addWidget(self.unknown_patient_check)
        
        row2_demo.addSpacing(20)
        
        row2_demo.addWidget(QLabel("ΦΥΛΟ"))
        self.radio_male = QRadioButton("ΑΝΔΡΑΣ")
        self.radio_female = QRadioButton("ΓΥΝΑΙΚΑ")
        row2_demo.addWidget(self.radio_male)
        row2_demo.addWidget(self.radio_female)
        
        row2_demo.addStretch()
        demo_layout.addLayout(row2_demo)

        # --- ROW 3: Insurance ---
        row3_demo = QHBoxLayout()
        row3_demo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row3_demo.setContentsMargins(0, 5, 0, 0)
        
        row3_demo.addWidget(QLabel("ΑΣΦΑΛΙΣΤΙΚΟΣ ΦΟΡΕΑΣ"))
        self.insurance_combo = QComboBox()
        self.insurance_combo.addItems(["", "ΕΟΠΥΥ", "ΑΝΑΣΦΑΛΙΣΤΟΣ", "ΙΔΙΩΤΙΚΗ", "ΕΥΡΩΠΑΪΚΗ ΚΑΡΤΑ"])
        self.insurance_combo.setFixedWidth(200)
        row3_demo.addWidget(self.insurance_combo)
        row3_demo.addStretch()
        
        demo_layout.addLayout(row3_demo)
        
        # -> Apply layout to GroupBox and add to main window!
        demo_group.setLayout(demo_layout)
        main_layout.addWidget(demo_group)

        # ==========================================
        # SECTION: ΣΤΟΙΧΕΙΑ ΕΠΙΚΟΙΝΩΝΙΑΣ (Contact Details)
        # ==========================================
        contact_group = QGroupBox("ΣΤΟΙΧΕΙΑ ΕΠΙΚΟΙΝΩΝΙΑΣ")
        contact_group.setAlignment(Qt.AlignmentFlag.AlignLeft)
        contact_group.setStyleSheet("QGroupBox { font-weight: bold; color: #333333; margin-top: 10px; }")
        
        contact_grid = QGridLayout()
        contact_grid.setContentsMargins(10, 10, 10, 10)
        contact_grid.setSpacing(5) # Keeps the rows packed tightly together
        contact_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # --- ROW 0: Top Labels ---
        contact_grid.addWidget(QLabel("ΤΗΛΕΦΩΝΑ"), 0, 0)
        contact_grid.addWidget(QLabel("ΚΛΗΣΗ ΑΠΟ"), 0, 1)

        # --- ROW 1: Phone 1 & Call From Dropdown ---
        self.phone_1_input = QLineEdit()
        self.phone_1_input.setFixedWidth(200)
        contact_grid.addWidget(self.phone_1_input, 1, 0)
        
        self.call_from_combo = QComboBox()
        self.call_from_combo.addItems(["", "ΑΣΘΕΝΗΣ", "ΣΥΓΓΕΝΗΣ", "ΙΑΤΡΟΣ", "ΑΣΤΥΝΟΜΙΑ", "ΠΥΡΟΣΒΕΣΤΙΚΗ", "ΑΛΛΟ"])
        self.call_from_combo.setFixedWidth(250)
        contact_grid.addWidget(self.call_from_combo, 1, 1)

        # --- ROW 2: Phone 2 & Caller Details Label ---
        self.phone_2_input = QLineEdit()
        self.phone_2_input.setFixedWidth(200)
        contact_grid.addWidget(self.phone_2_input, 2, 0)
        
        # Pushed to the bottom of the cell so it hugs the input box below it
        contact_grid.addWidget(QLabel("ΣΤΟΙΧΕΙΑ ΚΑΛΟΥΝΤΑ"), 2, 1, alignment=Qt.AlignmentFlag.AlignBottom) 

        # --- ROW 3: Phone 3 & Caller Details Input ---
        self.phone_3_input = QLineEdit()
        self.phone_3_input.setFixedWidth(200)
        contact_grid.addWidget(self.phone_3_input, 3, 0)
        
        self.caller_info_input = QLineEdit()
        self.caller_info_input.setFixedWidth(250)
        contact_grid.addWidget(self.caller_info_input, 3, 1)
        
        # -> Apply grid to GroupBox and add to main window
        contact_group.setLayout(contact_grid)
        main_layout.addWidget(contact_group)
        
        # ==========================================
        # SECTION: ΣΤΟΙΧΕΙΑ ΣΥΜΒΑΝΤΟΣ (Incident Details)
        # ==========================================
        incident_group = QGroupBox("ΣΤΟΙΧΕΙΑ ΣΥΜΒΑΝΤΟΣ")
        incident_group.setAlignment(Qt.AlignmentFlag.AlignLeft)
        incident_group.setStyleSheet("QGroupBox { font-weight: bold; color: #333333; margin-top: 10px; }")
        
        incident_grid = QGridLayout()
        incident_grid.setContentsMargins(10, 10, 10, 10)
        incident_grid.setSpacing(10)
        incident_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # --- ROW 0: Checkboxes (Left) & Transport Label (Right) ---
        
        # We use a grid or individual placements inside the main incident_grid columns 
        # so they pack tightly like a table row:
        self.breath_check = QCheckBox("ΑΠΩΛΕΙΑ\nΑΝΑΠΝΟΗΣ")
        self.senses_check = QCheckBox("ΑΠΩΛΕΙΑ\nΑΙΣΘΗΣΕΩΝ")
        self.consciousness_check = QCheckBox("ΑΠΩΛΕΙΑ\nΣΥΝΕΙΔΗΣΗΣ")
        self.bleeding_check = QCheckBox("ΕΧΕΙ\nΑΙΜΟΡΡΑΓΙΑ")

        # Place each checkbox in its own sub-column right next to each other
        chk_grid = QHBoxLayout()
        chk_grid.setContentsMargins(0, 0, 0, 0)
        chk_grid.setSpacing(2)  # Tight horizontal spacing
        
        chk_grid.addWidget(self.breath_check)
        chk_grid.addWidget(self.senses_check)
        chk_grid.addWidget(self.consciousness_check)
        chk_grid.addWidget(self.bleeding_check)
        chk_grid.addStretch()  # Pulls them all to the far left so they don't stretch apart

# Note: Added '1, 2' at the end here so the checkboxes span across both columns!
        incident_grid.addLayout(chk_grid, 0, 0, 1, 2) 

        # --- ROW 1: Incident Type (Left) & Transport Label (Right) ---
        incident_grid.addWidget(QLabel("*ΕΙΔΟΣ ΣΥΜΒΑΝΤΟΣ"), 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        incident_grid.addWidget(QLabel("ΤΡΟΠΟΣ ΜΕΤΑΦΟΡΑΣ"), 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # --- ROW 2: Dropdown and Input Box ---
        self.incident_type_combo = QComboBox()
        self.incident_type_combo.addItems(["", "ΑΣΘΕΝΕΙΑ", "ΤΡΟΧΑΙΟ", "ΕΡΓΑΤΙΚΟ ΑΤΥΧΗΜΑ", "ΑΛΛΟ ΑΤΥΧΗΜΑ"])
        self.incident_type_combo.setFixedWidth(220)
        incident_grid.addWidget(self.incident_type_combo, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        self.transport_input = QLineEdit()
        self.transport_input.setMinimumHeight(30)
        self.transport_input.setFixedWidth(300)
        incident_grid.addWidget(self.transport_input, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        # --- ROW 3: Symptoms & History Labels (Changed from 2 to 3) ---
        incident_grid.addWidget(QLabel("ΣΥΜΠΤΩΜΑΤΑ"), 3, 0)
        incident_grid.addWidget(QLabel("ΙΣΤΟΡΙΚΟ"), 3, 1)

        # --- ROW 4: Symptoms & History Multi-line Text Boxes (Changed from 3 to 4) ---
        self.symptoms_input = QTextEdit()
        self.symptoms_input.setMaximumHeight(60)
        incident_grid.addWidget(self.symptoms_input, 4, 0)

        self.history_input = QTextEdit()
        self.history_input.setMaximumHeight(60)
        incident_grid.addWidget(self.history_input, 4, 1)

        incident_grid.setColumnStretch(2, 1) 

        # -> Apply grid to GroupBox and add to main layout
        incident_group.setLayout(incident_grid)
        main_layout.addWidget(incident_group)

# ==========================================
        # SECTION: BOTTOM LEFT (Doctor, Response, Notes)
        # ==========================================
        
        # --- ROW 1: Doctor & Cancel En Route ---
        doc_layout = QHBoxLayout()
        doc_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        doc_layout.addWidget(QLabel("ΙΑΤΡΟΣ ΚΕΝΤΡΟΥ"))
        self.center_doctor_input = QLineEdit()
        self.center_doctor_input.setFixedWidth(200)
        doc_layout.addWidget(self.center_doctor_input)
        
        doc_layout.addSpacing(15)
        
        self.cancel_en_route_check = QCheckBox("ΑΚΥΡΟ ΚΑΘ' ΟΔΟΝ")
        doc_layout.addWidget(self.cancel_en_route_check)
        
        self.cancel_reason_input = QLineEdit()
        self.cancel_reason_input.setFixedWidth(180)
        doc_layout.addWidget(self.cancel_reason_input)
        
        doc_layout.addStretch()
        main_layout.addLayout(doc_layout)

        # --- ROW 2: Response (Colored) & Validity ---
        response_layout = QHBoxLayout()
        response_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # 2a. Antapokrisi (Response) Column
        response_col = QVBoxLayout()
        response_col.setContentsMargins(0, 0, 0, 0)
        response_col.addWidget(QLabel("ΑΝΤΑΠΟΚΡΙΣΗ"))
        
        radios_layout = QHBoxLayout()
        radios_layout.setSpacing(5)
        
        # Adding the specific background colors using CSS
        self.resp_normal = QRadioButton("ΚΑΝΟΝΙΚΗ")
        self.resp_normal.setStyleSheet("background-color: #8FBC8F; padding: 3px; border-radius: 4px; font-weight: bold;") # Green
        
        self.resp_urgent = QRadioButton("ΕΠΕΙΓΟΥΣΑ")
        self.resp_urgent.setStyleSheet("background-color: #F4A460; padding: 3px; border-radius: 4px; font-weight: bold;") # Orange
        
        self.resp_inter = QRadioButton("ΔΙΑΝΟΣΟΚ.")
        self.resp_inter.setStyleSheet("background-color: #9370DB; padding: 3px; border-radius: 4px; font-weight: bold;") # Purple
        
        self.resp_super = QRadioButton("ΥΠΕΡΕΠΕΙΓ.")
        self.resp_super.setStyleSheet("background-color: #FA8072; padding: 3px; border-radius: 4px; font-weight: bold;") # Red
        
        radios_layout.addWidget(self.resp_normal)
        radios_layout.addWidget(self.resp_urgent)
        radios_layout.addWidget(self.resp_inter)
        radios_layout.addWidget(self.resp_super)
        
        response_col.addLayout(radios_layout)
        response_layout.addLayout(response_col)
        
        response_layout.addSpacing(30)
        
        # 2b. Egkyro (Valid) Column
        valid_col = QVBoxLayout()
        valid_col.setContentsMargins(0, 0, 0, 0)
        valid_col.addWidget(QLabel("ΕΓΚΥΡΟ"))
        
        valid_radios_layout = QHBoxLayout()
        self.valid_yes = QRadioButton("Ναι")
        self.valid_no = QRadioButton("Όχι")
        valid_radios_layout.addWidget(self.valid_yes)
        valid_radios_layout.addWidget(self.valid_no)
        
        valid_col.addLayout(valid_radios_layout)
        response_layout.addLayout(valid_col)
        
        response_layout.addStretch()
        main_layout.addLayout(response_layout)

        # --- ROW 3: Notes ---
        notes_layout = QVBoxLayout()
        notes_layout.setContentsMargins(0, 5, 0, 0)
        notes_layout.addWidget(QLabel("ΣΗΜΕΙΩΣΕΙΣ"))
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        self.notes_input.setFixedWidth(450)
        notes_layout.addWidget(self.notes_input)
        
        main_layout.addLayout(notes_layout)


        # ==========================================
        # SECTION: RIGHT SIDE - ΠΑΡΑΛΑΒΗ ΔΙΑΒΙΒΑΣΤΗΣ
        # ==========================================
        
        # 1. The Label on top
        right_layout.addWidget(QLabel("ΠΑΡΑΛΑΒΗ ΔΙΑΒΙΒΑΣΤΗΣ"))
        
        # 2. The row with the time, text box, and buttons
        dispatch_row = QHBoxLayout()
        dispatch_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Time input (shows 00:00)
        self.dispatch_time = QLineEdit("00:00")
        self.dispatch_time.setFixedWidth(50)
        self.dispatch_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dispatch_row.addWidget(self.dispatch_time)
        
        # Wide text input
        self.dispatch_name = QLineEdit()
        self.dispatch_name.setFixedWidth(250) 
        dispatch_row.addWidget(self.dispatch_name)
        
        # Icon Buttons (Using text/emojis as placeholders for the document icons)
        self.btn_doc1 = QPushButton("📄")
        self.btn_doc1.setFixedWidth(30)
        dispatch_row.addWidget(self.btn_doc1)
        
        self.btn_doc2 = QPushButton("📋")
        self.btn_doc2.setFixedWidth(30)
        dispatch_row.addWidget(self.btn_doc2)
        
        dispatch_row.addStretch()
        right_layout.addLayout(dispatch_row)


        # ==========================================
        # SECTION: AMBULANCE TAB (Νέο Ασθενοφόρο)
        # ==========================================
        
        # 1. Create the Tab Widget
        self.ambulance_tabs = QTabWidget()
        
        # Create the main page (widget) for this tab
        amb_tab = QWidget()
        amb_layout = QVBoxLayout(amb_tab)
        amb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # --- ROW 1: Ambulance Code & Position ---
        code_pos_layout = QHBoxLayout()
        
        # Left: Ambulance Code
        code_layout = QVBoxLayout()
        code_label = QLabel("ΚΩΔ. ΑΣΘΕΝΟΦΟΡΟΥ")
        code_label.setStyleSheet("color: #A0A0A0;") # Light grey text to match image
        code_layout.addWidget(code_label)
        
        self.amb_code_combo = QComboBox()
        self.amb_code_combo.setFixedWidth(200)
        code_layout.addWidget(self.amb_code_combo)
        
        # Right: Position
        pos_layout = QVBoxLayout()
        pos_label = QLabel("ΘΕΣΗ")
        pos_label.setStyleSheet("color: #A0A0A0;")
        pos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pos_layout.addWidget(pos_label)
        
        self.amb_pos_input = QLineEdit()
        self.amb_pos_input.setFixedWidth(100)
        pos_layout.addWidget(self.amb_pos_input)
        
        code_pos_layout.addLayout(code_layout)
        code_pos_layout.addLayout(pos_layout)
        code_pos_layout.addStretch()
        
        amb_layout.addLayout(code_pos_layout)
        amb_layout.addSpacing(10)

        # --- ROW 2: The Timing Grid (00:00) ---
        timing_grid = QGridLayout()
        timing_grid.setSpacing(8)
        
        # Helper styles to match the image
        grey_label_style = "color: #A0A0A0; font-size: 10px;"
        time_input_style = "font-size: 14px; font-weight: bold; background-color: #E8E8E8; border: 1px solid #000;"

        # Column 0 & 1: ΔΙΑΒΙΒΑΣΗ
        lbl_diavivasi = QLabel("ΔΙΑΒΙΒΑΣΗ")
        lbl_diavivasi.setStyleSheet(grey_label_style)
        timing_grid.addWidget(lbl_diavivasi, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.time_diavivasi = QLineEdit("00:00")
        self.time_diavivasi.setStyleSheet(time_input_style)
        self.time_diavivasi.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_diavivasi.setFixedSize(80, 30)
        timing_grid.addWidget(self.time_diavivasi, 0, 1)

        # Column 2 & 3: ΑΦΙΞΗ ΣΤΟΝ ΠΡΟΟΡΙΣΜΟ
        lbl_afixi_pro = QLabel("ΑΦΙΞΗ ΣΤΟΝ\nΠΡΟΟΡΙΣΜΟ")
        lbl_afixi_pro.setStyleSheet(grey_label_style)
        timing_grid.addWidget(lbl_afixi_pro, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.time_afixi_pro = QLineEdit("00:00")
        self.time_afixi_pro.setStyleSheet(time_input_style)
        self.time_afixi_pro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_afixi_pro.setFixedSize(80, 30)
        timing_grid.addWidget(self.time_afixi_pro, 0, 3)

        # Column 0 & 1 (Row 2): ΑΦΙΞΗ ΣΤΟ ΣΥΜΒΑΝ
        lbl_afixi_sym = QLabel("ΑΦΙΞΗ ΣΤΟ\nΣΥΜΒΑΝ")
        lbl_afixi_sym.setStyleSheet(grey_label_style)
        timing_grid.addWidget(lbl_afixi_sym, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.time_afixi_sym = QLineEdit("00:00")
        self.time_afixi_sym.setStyleSheet(time_input_style)
        self.time_afixi_sym.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_afixi_sym.setFixedSize(80, 30)
        timing_grid.addWidget(self.time_afixi_sym, 1, 1)

        # Column 2 & 3 (Row 2): ΤΕΛΟΣ
        lbl_telos = QLabel("ΤΕΛΟΣ")
        lbl_telos.setStyleSheet(grey_label_style)
        timing_grid.addWidget(lbl_telos, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.time_telos = QLineEdit("00:00")
        self.time_telos.setStyleSheet(time_input_style)
        self.time_telos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_telos.setFixedSize(80, 30)
        timing_grid.addWidget(self.time_telos, 1, 3)

        # Column 0 & 1 (Row 3): ΑΝΑΧΩΡΗΣΗ ΑΠΟ ΣΥΜΒΑΝ
        lbl_anaxorisi = QLabel("ΑΝΑΧΩΡΗΣΗ\nΑΠΟ ΣΥΜΒΑΝ")
        lbl_anaxorisi.setStyleSheet(grey_label_style)
        timing_grid.addWidget(lbl_anaxorisi, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.time_anaxorisi = QLineEdit("00:00")
        self.time_anaxorisi.setStyleSheet(time_input_style)
        self.time_anaxorisi.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_anaxorisi.setFixedSize(80, 30)
        timing_grid.addWidget(self.time_anaxorisi, 2, 1)

# Column 2 & 3 (Row 3): ΗΜ/ΝΙΑ ΑΚΥΡΩΣΗΣ
        lbl_akyrosi = QLabel("ΗΜ/ΝΙΑ\nΑΚΥΡΩΣΗΣ")
        lbl_akyrosi.setStyleSheet(grey_label_style)
        timing_grid.addWidget(lbl_akyrosi, 2, 2, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Swapped to a QDateTimeEdit with a calendar popup
        self.time_akyrosi = QDateTimeEdit()
        self.time_akyrosi.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.time_akyrosi.setCalendarPopup(True)
        self.time_akyrosi.setFixedWidth(150) # Made slightly wider to fit the dropdown arrow
        self.time_akyrosi.setMinimumDateTime(QDateTime.currentDateTime()) # Defaults to current date/time
        timing_grid.addWidget(self.time_akyrosi, 2, 3)

        amb_layout.addLayout(timing_grid)

        # ==========================================
        # SECTION: CANCELLATION DETAILS
        # ==========================================
        
        # --- Reasons for Cancellation ---
        cancel_reasons_layout = QHBoxLayout()
        lbl_cancel_reason = QLabel("*ΛΟΓΟΙ ΑΚΥΡΩΣΗΣ")
        lbl_cancel_reason.setStyleSheet("color: #A0A0A0;") # Light grey
        cancel_reasons_layout.addWidget(lbl_cancel_reason)
        
        self.cancel_reasons_combo = QComboBox()
        cancel_reasons_layout.addWidget(self.cancel_reasons_combo)
        amb_layout.addLayout(cancel_reasons_layout)

        # --- Cancellation Comments ---
        cancel_comments_layout = QHBoxLayout()
        lbl_cancel_comments = QLabel("*ΣΧΟΛΙΑ ΑΚΥΡΩΣΗΣ")
        lbl_cancel_comments.setStyleSheet("color: #A0A0A0;")
        cancel_comments_layout.addWidget(lbl_cancel_comments)
        
        self.cancel_comments_input = QLineEdit()
        cancel_comments_layout.addWidget(self.cancel_comments_input)
        amb_layout.addLayout(cancel_comments_layout)

        # --- Name and Surname ---
        name_surname_layout = QHBoxLayout()
        lbl_name = QLabel("ΟΝΟΜΑ")
        lbl_name.setStyleSheet("color: #A0A0A0;")
        name_surname_layout.addWidget(lbl_name)
        
        self.cancel_name_input = QLineEdit()
        name_surname_layout.addWidget(self.cancel_name_input)
        
        lbl_surname = QLabel("ΕΠΩΝΥΜΟ")
        lbl_surname.setStyleSheet("color: #A0A0A0;")
        name_surname_layout.addWidget(lbl_surname)
        
        self.cancel_surname_input = QLineEdit()
        name_surname_layout.addWidget(self.cancel_surname_input)
        amb_layout.addLayout(name_surname_layout)

        # ==========================================
        # SECTION: DESTINATION & HOSPITAL (Red Text)
        # ==========================================
        
        # --- Destination Radio Buttons ---
        dest_layout = QHBoxLayout()
        lbl_destination = QLabel("ΠΡΟΟΡΙΣΜΟΣ")
        lbl_destination.setStyleSheet("color: #D32F2F; font-weight: bold;") # Distinct Red
        dest_layout.addWidget(lbl_destination)

        self.dest_hosp = QRadioButton("ΝΟΣ/ΜΕΙΟ")
        self.dest_address = QRadioButton("Δ/ΝΣΗ")
        self.dest_port = QRadioButton("ΛΙΜΑΝΙ ΑΕΡΟΔΡ.") 
        self.dest_region = QRadioButton("ΠΕΡΙΦΕΡΕΙΑ")

        dest_layout.addWidget(self.dest_hosp)
        dest_layout.addWidget(self.dest_address)
        dest_layout.addWidget(self.dest_port)
        dest_layout.addWidget(self.dest_region)
        dest_layout.addStretch()
        amb_layout.addLayout(dest_layout)

        # --- Hospital ---
        hosp_layout = QHBoxLayout()
        lbl_hospital = QLabel("*ΝΟΣΟΚΟΜΕΙΟ")
        lbl_hospital.setStyleSheet("color: #D32F2F; font-weight: bold;")
        hosp_layout.addWidget(lbl_hospital)
        
        self.hospital_combo = QComboBox()
        hosp_layout.addWidget(self.hospital_combo)
        amb_layout.addLayout(hosp_layout)

        # --- Clinic ---
        clinic_layout = QHBoxLayout()
        lbl_clinic = QLabel("ΚΛΙΝΙΚΗ")
        lbl_clinic.setStyleSheet("color: #D32F2F;")
        clinic_layout.addWidget(lbl_clinic)
        
        self.clinic_combo = QComboBox()
        clinic_layout.addWidget(self.clinic_combo)
        amb_layout.addLayout(clinic_layout)


# --- Reception Doctor ---
        doc_recv_layout = QHBoxLayout()
        lbl_doc_recv = QLabel("ΙΑΤΡΟΣ ΥΠΟΔΟΧΗΣ")
        lbl_doc_recv.setStyleSheet("color: #D32F2F;")
        doc_recv_layout.addWidget(lbl_doc_recv)
        
        self.recv_doctor_input = QLineEdit()
        doc_recv_layout.addWidget(self.recv_doctor_input)
        amb_layout.addLayout(doc_recv_layout)

        # --- Crew Involvement & Sirens ---
        emploki_layout = QHBoxLayout()
        lbl_emploki = QLabel("ΕΜΠΛΟΚΗ ΦΟΡΕΩΝ")
        lbl_emploki.setStyleSheet("color: #D32F2F;")
        emploki_layout.addWidget(lbl_emploki)
        
        self.emploki_combo = QComboBox()
        emploki_layout.addWidget(self.emploki_combo)
        
        self.siren_check = QCheckBox("ΧΡΗΣΗ ΣΕΙΡΗΝΑΣ")
        self.siren_check.setStyleSheet("color: #D32F2F;")
        emploki_layout.addWidget(self.siren_check)
        amb_layout.addLayout(emploki_layout)

        # --- Directives & First Aid ---
        entoles_layout = QHBoxLayout()
        lbl_entoles = QLabel("ΕΝΤΟΛΕΣ\nΣΥΝΤΟΝΙΣΜΟΣ")
        lbl_entoles.setStyleSheet("color: #D32F2F;")
        entoles_layout.addWidget(lbl_entoles)
        
        self.entoles_combo = QComboBox()
        entoles_layout.addWidget(self.entoles_combo)
        
        self.first_aid_check = QCheckBox("ΟΔΗΓΙΕΣ Ε/Κ\nΑ' ΒΟΗΘΕΙΕΣ")
        self.first_aid_check.setStyleSheet("color: #D32F2F;")
        entoles_layout.addWidget(self.first_aid_check)
        amb_layout.addLayout(entoles_layout)

        # --- Vital Signs (BP, HR, SpO2, AVPU, SMS) ---
        vitals_layout = QHBoxLayout()
        vitals = ["BP", "HR", "SpO2", "AVPU", "SMS"]
        self.vital_inputs = {}
        
        for v in vitals:
            v_col = QVBoxLayout()
            v_lbl = QLabel(v)
            v_lbl.setStyleSheet("color: #D32F2F; font-weight: bold;")
            v_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v_col.addWidget(v_lbl)
            
            v_input = QLineEdit()
            v_input.setFixedSize(40, 25)
            v_col.addWidget(v_input)
            
            self.vital_inputs[v] = v_input
            vitals_layout.addLayout(v_col)
            
        vitals_layout.addStretch()
        amb_layout.addLayout(vitals_layout)

        # --- Assessment & Crew Actions (Nested Tabs) ---
        self.inner_tabs = QTabWidget()
        
        # Assessment Tab
        ektimisi_tab = QWidget()
        ekt_layout = QVBoxLayout(ektimisi_tab)
        ekt_layout.setContentsMargins(0, 0, 0, 0)
        self.ektimisi_input = QTextEdit()
        self.ektimisi_input.setMaximumHeight(500)
        ekt_layout.addWidget(self.ektimisi_input)
        self.inner_tabs.addTab(ektimisi_tab, "ΕΚΤΙΜΗΣΗ")

        # Actions Tab
        energeies_tab = QWidget()
        en_layout = QVBoxLayout(energeies_tab)
        en_layout.setContentsMargins(0, 0, 0, 0)
        self.energeies_input = QTextEdit()
        self.energeies_input.setMaximumHeight(500)
        en_layout.addWidget(self.energeies_input)
        self.inner_tabs.addTab(energeies_tab, "ΕΝΕΡΓΕΙΕΣ ΠΛΗΡΩΜΑΤΟΣ")

        amb_layout.addWidget(self.inner_tabs)

        # --- Observations / Notes ---
        lbl_paratiriseis = QLabel("ΠΑΡΑΤΗΡΗΣΕΙΣ")
        lbl_paratiriseis.setStyleSheet("color: #A0A0A0;")
        amb_layout.addWidget(lbl_paratiriseis)
        
        self.right_notes_input = QTextEdit()
        self.right_notes_input.setMaximumHeight(50)
        amb_layout.addWidget(self.right_notes_input)

        # ==========================================
        # FINALIZE TABS & ADD BOTTOM ACTION BUTTONS
        # ==========================================
        
        # 1. Add the completed tab page to the Tab Widget
        self.ambulance_tabs.addTab(amb_tab, "📄 Νέο Ασθενοφόρο") 
        
        # 2. Add the entire Tab Widget to the right layout
        right_layout.addWidget(self.ambulance_tabs)

        # 3. Add the Submit / Standby / Terminate Buttons at the very bottom right
        action_btn_layout = QHBoxLayout()
        action_btn_layout.addStretch() # Pushes buttons all the way to the right
        
        # ---> NEW: Terminate Button <---
        self.btn_terminate = QPushButton("ΤΕΡΜΑΤΙΣΜΟΣ")
        self.btn_terminate.setFixedSize(110, 35)
        self.btn_terminate.setStyleSheet("background-color: #D32F2F; color: white; font-weight: bold;")
        self.btn_terminate.clicked.connect(self.terminate_incident)
        
        self.btn_standby = QPushButton("Σε Αναμονή")
        self.btn_standby.setFixedSize(100, 35)
        self.btn_standby.clicked.connect(self.save_as_pending)
        
        self.btn_send = QPushButton("ΑΠΟΣΤΟΛΗ")
        self.btn_send.setFixedSize(100, 35)
        self.btn_send.clicked.connect(self.save_as_sent)
        
        # Add them to the layout in order
        action_btn_layout.addWidget(self.btn_terminate)
        action_btn_layout.addWidget(self.btn_standby)
        action_btn_layout.addWidget(self.btn_send)
        
        right_layout.addLayout(action_btn_layout)


        # Instantiate the click filter
        self.time_filter = TimeFieldFilter()
        
        # Gather all your timing QLineEdits into a list
        time_fields = [
            self.dispatch_time,
            self.time_diavivasi,
            self.time_afixi_pro,
            self.time_afixi_sym,
            self.time_telos,
            self.time_anaxorisi
        ]
        
        # Apply the filter to every timing box automatically
        for field in time_fields:
            field.installEventFilter(self.time_filter)

        # ==========================================
        # INTERACTIVITY: Cancellation Toggles
        # ==========================================

        # 1. LEFT SIDE: Cancel En Route
        self.cancel_reason_input.setEnabled(False)

        def toggle_left_cancel(checked):
            self.cancel_reason_input.setEnabled(checked)
            if not checked:
                self.cancel_reason_input.clear() # Clears text if unchecked

        self.cancel_en_route_check.toggled.connect(toggle_left_cancel)

        # 2. RIGHT SIDE: Disable cancellation fields by default
        self.cancel_reasons_combo.setEnabled(False)
        self.cancel_comments_input.setEnabled(False)
        self.cancel_name_input.setEnabled(False)
        self.cancel_surname_input.setEnabled(False)

        # Make the ΗΜ/ΝΙΑ ΑΚΥΡΩΣΗΣ box start "blank"
        self.time_akyrosi.setMinimumDateTime(QDateTime(2000, 1, 1, 0, 0)) # A safe past date
        self.time_akyrosi.setSpecialValueText(" ") # Displays as empty when at the minimum date
        self.time_akyrosi.setDateTime(self.time_akyrosi.minimumDateTime())

        # 3. Function to unlock fields when time is stamped
        def unlock_right_cancel(new_datetime):
            # If a real date is selected (not the blank year 2000), enable fields!
            if new_datetime.date().year() > 2000:
                self.cancel_reasons_combo.setEnabled(True)
                self.cancel_comments_input.setEnabled(True)
                self.cancel_name_input.setEnabled(True)
                self.cancel_surname_input.setEnabled(True)
            else:
                self.cancel_reasons_combo.setEnabled(False)
                self.cancel_comments_input.setEnabled(False)
                self.cancel_name_input.setEnabled(False)
                self.cancel_surname_input.setEnabled(False)

        # Connect the date/time box to the unlock function
        self.time_akyrosi.dateTimeChanged.connect(unlock_right_cancel)

        # 4. Filter to instantly stamp the CURRENT time when clicked!
        class AkyrosiClickFilter(QObject):
            def eventFilter(self, obj, event):
                # If the user clicks or tabs into the empty box, fill it with NOW
                if event.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.FocusIn):
                    if obj.dateTime() == obj.minimumDateTime():
                        obj.setDateTime(QDateTime.currentDateTime())
                return super().eventFilter(obj, event)

        self.akyrosi_click_filter = AkyrosiClickFilter()
        self.time_akyrosi.installEventFilter(self.akyrosi_click_filter)




        # ==========================================
        # FINALIZE SCROLL AREA & WINDOW LAYOUT
        # ==========================================
        main_layout.addStretch() # Pushes everything to the top of the canvas
        
        # Put the canvas inside the Scroll Area
        scroll_area.setWidget(scroll_content)
        
        # Add the Scroll Area to the main window
        window_layout.addWidget(scroll_area)
        
        # NOTE: We no longer need self.setLayout() because window_layout(self) handled it!


    def switch_pickup_view(self):
        """Changes the visible layout based on the selected radio button."""
        if self.radio_address.isChecked():
            self.pickup_stack.setCurrentIndex(0) 
        elif self.radio_health.isChecked():
            self.pickup_stack.setCurrentIndex(1) 
        elif self.radio_icu.isChecked():
            self.pickup_stack.setCurrentIndex(2) 
        elif self.radio_port_air.isChecked():
            self.pickup_stack.setCurrentIndex(3) 

    def gather_form_data(self):
        """Scrapes all data from the UI elements and returns it as a dictionary."""
        
        # 1. Figure out which Priority (ΑΝΤΑΠΟΚΡΙΣΗ) radio button is checked
        priority_level = ""
        if hasattr(self, 'resp_normal') and self.resp_normal.isChecked():
            priority_level = "ΚΑΝΟΝΙΚΗ"
        elif hasattr(self, 'resp_urgent') and self.resp_urgent.isChecked():
            priority_level = "ΕΠΕΙΓΟΥΣΑ"
        elif hasattr(self, 'resp_super') and self.resp_super.isChecked():
            priority_level = "ΥΠΕΡΕΠΕΙΓ."
        elif hasattr(self, 'resp_inter') and self.resp_inter.isChecked():
            priority_level = "ΔΙΑΝΟΣΟΚ."

        # 2. Gather all the data into a dictionary matching the database columns
        data = {
            "card_code": self.card_input.text() if hasattr(self, 'card_input') else "",
            "timestamp": self.time_input.text() if hasattr(self, 'time_input') else "",
            "position": self.desk_input.text() if hasattr(self, 'desk_input') else "",
            "operator_name": self.operator_input.text() if hasattr(self, 'operator_input') else "",
            
            # Left Column Additions
            "emergency": self.emergency_check.isChecked() if hasattr(self, 'emergency_check') else False,
            "priority": priority_level,
            "phone_1": self.phone_1_input.text() if hasattr(self, 'phone_1_input') else "",
            "hospital_name": self.hospital_combo.currentText() if hasattr(self, 'hospital_combo') else "",
            "ambulance_number": self.amb_code_combo.currentText() if hasattr(self, 'amb_code_combo') else "",
            
            # Comboboxes
            "sector": self.sector_combo.currentText() if hasattr(self, 'sector_combo') else "",
            "municipality_region": self.municipality_combo.currentText() if hasattr(self, 'municipality_combo') else "",
            "type_of_incident": self.incident_type_combo.currentText() if hasattr(self, 'incident_type_combo') else "",
            
            # Right Column Text Fields
            "address": self.street_input.text() if hasattr(self, 'street_input') else "",
            "adress_num": self.number_input.text() if hasattr(self, 'number_input') else "",
            "patient_last_name": self.last_name_input.text() if hasattr(self, 'last_name_input') else "",
            "patient_name": self.first_name_input.text() if hasattr(self, 'first_name_input') else "",
            
            # Symptom Checkboxes
            "loss_of_breath": self.breath_check.isChecked() if hasattr(self, 'breath_check') else False,
            "loss_of_sensation": self.senses_check.isChecked() if hasattr(self, 'senses_check') else False,
            "loss_of_consciousness": self.consciousness_check.isChecked() if hasattr(self, 'consciousness_check') else False,
            "hemmorage": self.bleeding_check.isChecked() if hasattr(self, 'bleeding_check') else False,

            # Ambulance Timestamps
            "timestamp_dispatch": self.time_diavivasi.text() if hasattr(self, 'time_diavivasi') else "",
            "timestamp_arrival_incident": self.time_afixi_sym.text() if hasattr(self, 'time_afixi_sym') else "",
            "timestamp_leaving_incident": self.time_anaxorisi.text() if hasattr(self, 'time_anaxorisi') else "",
            "timestamp_arrival_hospital": self.time_afixi_pro.text() if hasattr(self, 'time_afixi_pro') else "",
            "timestamp_end": self.time_telos.text() if hasattr(self, 'time_telos') else "",
        }
        
        # Safely handle the Age (must be a number for the database)
        if hasattr(self, 'age_input') and self.age_input.text().isdigit():
            data["patient_age"] = int(self.age_input.text())
            
        # Safely handle Vital Signs dictionary
        if hasattr(self, 'vital_inputs'):
            if self.vital_inputs.get("BP") and self.vital_inputs["BP"].text().isdigit():
                data["blood_pressure"] = int(self.vital_inputs["BP"].text())
            if self.vital_inputs.get("HR") and self.vital_inputs["HR"].text().isdigit():
                data["heart_rate"] = int(self.vital_inputs["HR"].text())
            if self.vital_inputs.get("SpO2") and self.vital_inputs["SpO2"].text().isdigit():
                data["spo2"] = int(self.vital_inputs["SpO2"].text())
            if self.vital_inputs.get("AVPU"):
                data["avpu"] = self.vital_inputs["AVPU"].text()
            if self.vital_inputs.get("SMS"):
                data["sms"] = self.vital_inputs["SMS"].text()

        # Safely handle Symptoms (QTextEdit)
        if hasattr(self, 'symptoms_input'):
            data["symptoms"] = self.symptoms_input.toPlainText()
                
        return data

    def initialize_empty_incident(self):
        """Creates the initial blank entry in the DB and generates the Card Code."""
        session = self.get_daily_session()
        
        # 1. Calculate the next Card Code (finds the highest code in both tables and adds 1)
        max_pending = session.query(func.max(PendingIncident.card_code)).scalar() or 0
        max_sent = session.query(func.max(SentIncident.card_code)).scalar() or 0
        new_card_code = max(max_pending, max_sent) + 1
        
        # 2. Set it in the UI
        self.card_input.setText(str(new_card_code))
        
        # 3. Save the blank record immediately to the pending table
        pos_val = int(self.desk_input.text()) if self.desk_input.text() else 0
        
        new_incident = PendingIncident(
            card_code=new_card_code,
            timestamp=self.time_input.text(),
            position=pos_val,
            operator_name=self.operator_input.text()
        )
        
        session.add(new_incident)
        session.commit()
        
        # 4. Save the database ID so we can update it later instead of creating duplicates!
        self.current_pending_id = new_incident.id
        session.close()

    def get_daily_session(self):
        """Dynamically creates or connects to today's incident database."""
        today_date = datetime.now().strftime("%Y-%m-%d")
        db_filename = f"sqlite:///incidents_{today_date}.db"
        from sqlalchemy import create_engine
        engine = create_engine(db_filename, echo=False)
        Base.metadata.create_all(engine)
        DailySession = sessionmaker(bind=engine)
        return DailySession()


    def load_incident(self, incident_id, is_pending):
        """Loads an existing incident from the database and fills the UI."""
        session = self.get_daily_session()
        
        try:
            # 1. Fetch the correct record based on the table clicked
            if is_pending:
                incident = session.query(PendingIncident).filter_by(id=int(incident_id)).first()
                self.current_pending_id = incident.id
                self.is_editing_sent = False 
            else:
                incident = session.query(SentIncident).filter_by(id=int(incident_id)).first()
                self.current_sent_id = incident.id
                self.is_editing_sent = True 
                
            if not incident:
                QMessageBox.warning(self, "Σφάλμα", "Το περιστατικό δεν βρέθηκε στη βάση.")
                return

            # 2. Populate the Top row
            if hasattr(self, 'card_input'): self.card_input.setText(str(incident.card_code) if incident.card_code else "")
            if hasattr(self, 'time_input') and incident.timestamp: self.time_input.setText(incident.timestamp)
            if hasattr(self, 'desk_input') and incident.position: self.desk_input.setText(str(incident.position))
            
            # 3. Populate Left Side (Checkboxes & Radio Buttons)
            if hasattr(self, 'emergency_check'): self.emergency_check.setChecked(bool(incident.emergency))
            
            if incident.priority == "ΚΑΝΟΝΙΚΗ" and hasattr(self, 'resp_normal'):
                self.resp_normal.setChecked(True)
            elif incident.priority == "ΕΠΕΙΓΟΥΣΑ" and hasattr(self, 'resp_urgent'):
                self.resp_urgent.setChecked(True)
            elif incident.priority == "ΥΠΕΡΕΠΕΙΓ." and hasattr(self, 'resp_super'):
                self.resp_super.setChecked(True)
            elif incident.priority == "ΔΙΑΝΟΣΟΚ." and hasattr(self, 'resp_inter'):
                self.resp_inter.setChecked(True)

            # 4. Populate Symptom Checkboxes
            if hasattr(self, 'breath_check'): self.breath_check.setChecked(bool(incident.loss_of_breath))
            if hasattr(self, 'senses_check'): self.senses_check.setChecked(bool(incident.loss_of_sensation))
            if hasattr(self, 'consciousness_check'): self.consciousness_check.setChecked(bool(incident.loss_of_consciousness))
            if hasattr(self, 'bleeding_check'): self.bleeding_check.setChecked(bool(incident.hemmorage))

            # 5. Populate Ambulance Timestamps
            if hasattr(self, 'time_diavivasi') and incident.timestamp_dispatch: self.time_diavivasi.setText(incident.timestamp_dispatch)
            if hasattr(self, 'time_afixi_sym') and incident.timestamp_arrival_incident: self.time_afixi_sym.setText(incident.timestamp_arrival_incident)
            if hasattr(self, 'time_anaxorisi') and incident.timestamp_leaving_incident: self.time_anaxorisi.setText(incident.timestamp_leaving_incident)
            if hasattr(self, 'time_afixi_pro') and incident.timestamp_arrival_hospital: self.time_afixi_pro.setText(incident.timestamp_arrival_hospital)
            if hasattr(self, 'time_telos') and incident.timestamp_end: self.time_telos.setText(incident.timestamp_end)

            # 6. Populate Vitals
            if hasattr(self, 'vital_inputs'):
                if self.vital_inputs.get("BP") and incident.blood_pressure: self.vital_inputs["BP"].setText(str(incident.blood_pressure))
                if self.vital_inputs.get("HR") and incident.heart_rate: self.vital_inputs["HR"].setText(str(incident.heart_rate))
                if self.vital_inputs.get("SpO2") and incident.spo2: self.vital_inputs["SpO2"].setText(str(incident.spo2))
                if self.vital_inputs.get("AVPU") and incident.avpu: self.vital_inputs["AVPU"].setText(incident.avpu)
                if self.vital_inputs.get("SMS") and incident.sms: self.vital_inputs["SMS"].setText(incident.sms)

            # 7. Populate Text & Combos
            if hasattr(self, 'phone_1_input') and incident.phone_1: self.phone_1_input.setText(incident.phone_1)
            
            if hasattr(self, 'amb_code_combo') and incident.ambulance_number: 
                if self.amb_code_combo.findText(incident.ambulance_number) == -1:
                    self.amb_code_combo.addItem(incident.ambulance_number)
                self.amb_code_combo.setCurrentText(incident.ambulance_number)
                
            if hasattr(self, 'hospital_combo') and incident.hospital_name: 
                if self.hospital_combo.findText(incident.hospital_name) == -1:
                    self.hospital_combo.addItem(incident.hospital_name)
                self.hospital_combo.setCurrentText(incident.hospital_name)
            
            if hasattr(self, 'sector_combo') and incident.sector: self.sector_combo.setCurrentText(incident.sector)
            if hasattr(self, 'municipality_combo') and incident.municipality_region: self.municipality_combo.setCurrentText(incident.municipality_region)
            if hasattr(self, 'incident_type_combo') and incident.type_of_incident: self.incident_type_combo.setCurrentText(incident.type_of_incident)
            
            if hasattr(self, 'street_input') and incident.address: self.street_input.setText(incident.address)
            if hasattr(self, 'number_input') and incident.adress_num: self.number_input.setText(incident.adress_num)
            if hasattr(self, 'last_name_input') and incident.patient_last_name: self.last_name_input.setText(incident.patient_last_name)
            if hasattr(self, 'first_name_input') and incident.patient_name: self.first_name_input.setText(incident.patient_name)
            if hasattr(self, 'age_input') and incident.patient_age: self.age_input.setText(str(incident.patient_age))
            
            if hasattr(self, 'symptoms_input') and incident.symptoms: 
                self.symptoms_input.setPlainText(incident.symptoms)

        except Exception as e:
            QMessageBox.critical(self, "Σφάλμα", f"Αδυναμία φόρτωσης: {str(e)}")
        finally:
            session.close()



    def validate_for_send(self):
        """Checks that all required fields on the left side are filled before sending."""
        errors = []
        
        if not self.sector_combo.currentText().strip():
            errors.append("Το πεδίο *ΤΟΜΕΑΣ είναι υποχρεωτικό.")
            
        if not self.incident_type_combo.currentText().strip():
            errors.append("Το πεδίο *ΕΙΔΟΣ ΣΥΜΒΑΝΤΟΣ είναι υποχρεωτικό.")
            
        # Check dynamic pickup fields based on what is selected
        idx = self.pickup_stack.currentIndex()
        if idx == 0: # Δ/ΝΣΗ
            if not self.street_input.text().strip(): errors.append("Το πεδίο *ΟΔΟΣ είναι υποχρεωτικό.")
            if not self.municipality_combo.currentText().strip(): errors.append("Το πεδίο *ΔΗΜΟΣ/ΠΕΡΙΟΧΗ είναι υποχρεωτικό.")
            if not self.exact_spot_input.text().strip(): errors.append("Το πεδίο *ΑΚΡΙΒΕΣ ΣΗΜΕΙΟ είναι υποχρεωτικό.")
        elif idx == 1: # ΥΓΕΙΟΝ. ΣΧΗΜ.
            if not self.health_org_combo.currentText().strip(): errors.append("Το πεδίο *ΥΓΕΙΟΝΟΜΙΚΟΣ ΣΧΗΜΑΤΙΣΜΟΣ είναι υποχρεωτικό.")
        elif idx == 2: # Μ.Ε.Θ.
            if not self.icu_combo.currentText().strip(): errors.append("Το πεδίο *ΥΓΕΙΟΝΟΜΙΚΟΣ ΣΧΗΜΑΤΙΣΜΟΣ είναι υποχρεωτικό.")
        elif idx == 3: # ΛΙΜΑΝΙ/ΑΕΡΟΔΡΟΜΙΟ
            if not self.port_org_combo.currentText().strip(): errors.append("Το πεδίο *ΛΙΜΑΝΙ/ΑΕΡΟΔΡΟΜΙΟ είναι υποχρεωτικό.")
            if not self.port_arrival_combo.currentText().strip(): errors.append("Το πεδίο *ΑΦΙΞΗ ΑΠΟ είναι υποχρεωτικό.")
            
        # Check that at least one phone number is provided
        phone_filled = any([
            self.phone_1_input.text().strip(), 
            self.phone_2_input.text().strip(), 
            self.phone_3_input.text().strip()
        ])
        if not phone_filled:
            errors.append("Πρέπει να συμπληρωθεί τουλάχιστον ένα ΤΗΛΕΦΩΝΟ.")
            
        # If there are errors, stop the process and warn the user
        if errors:
            QMessageBox.warning(self, "Ελλιπή Στοιχεία", "\n".join(errors))
            return False
            
        return True

    def save_as_pending(self):
        """Updates the existing record with whatever is written so far."""
        session = self.get_daily_session()
        try:
            data = self.gather_form_data()
            
            # Prevent a sent incident from being reverted to pending by mistake
            if hasattr(self, 'is_editing_sent') and self.is_editing_sent:
                QMessageBox.warning(self, "Προσοχή", "Το περιστατικό έχει ήδη αποσταλεί. Πατήστε 'ΑΠΟΣΤΟΛΗ' για να αποθηκεύσετε τις αλλαγές.")
                return

            if hasattr(self, 'current_pending_id'):
                incident = session.query(PendingIncident).filter_by(id=self.current_pending_id).first()
                if incident:
                    for key, value in data.items():
                        setattr(incident, key, value)
                    session.commit()
                    QMessageBox.information(self, "Επιτυχία", "Το περιστατικό ενημερώθηκε σε αναμονή!")
                    self.close() 
        except Exception as e:
            QMessageBox.critical(self, "Σφάλμα", f"Αδυναμία αποθήκευσης: {str(e)}")
        finally:
            session.close()

    def save_as_sent(self):
        """Validates and saves. Updates if already sent, moves it if pending."""
        if not self.validate_for_send():
            return 
            
        session = self.get_daily_session()
        try:
            data = self.gather_form_data()
            
            # If we opened a Running/Sent incident, just update it
            if hasattr(self, 'is_editing_sent') and self.is_editing_sent:
                incident = session.query(SentIncident).filter_by(id=self.current_sent_id).first()
                if incident:
                    for key, value in data.items():
                        setattr(incident, key, value)
            
            # If we opened a Pending incident (or it's brand new), move it to Sent
            else:
                new_sent_incident = SentIncident(**data)
                session.add(new_sent_incident)
                
                if hasattr(self, 'current_pending_id'):
                    old_pending = session.query(PendingIncident).filter_by(id=self.current_pending_id).first()
                    if old_pending:
                        session.delete(old_pending)
                
            session.commit()
            QMessageBox.information(self, "Επιτυχία", "Το περιστατικό αποθηκεύτηκε/απεστάλη επιτυχώς!")
            self.close() 
        except Exception as e:
            QMessageBox.critical(self, "Σφάλμα", f"Αδυναμία αποθήκευσης: {str(e)}")
        finally:
            session.close()

    def terminate_incident(self):
        """Moves the incident to the Finalized table, then removes it from active tables."""
        reply = QMessageBox.question(
            self, 
            "Τερματισμός Περιστατικού", 
            "Είστε σίγουροι ότι θέλετε να κλείσετε οριστικά αυτό το περιστατικό;\n\nΘα μεταφερθεί στο Ιστορικό.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = self.get_daily_session()
            try:
                # 1. Gather current data and create a Finalized record
                data = self.gather_form_data()
                final_incident = FinalizedIncident(**data)
                session.add(final_incident)

                # 2. Delete from Pending (if it exists there)
                if hasattr(self, 'current_pending_id'):
                    pending = session.query(PendingIncident).filter_by(id=self.current_pending_id).first()
                    if pending:
                        session.delete(pending)
                        
                # 3. Delete from Sent (if it exists there)
                if hasattr(self, 'current_sent_id'):
                    sent = session.query(SentIncident).filter_by(id=self.current_sent_id).first()
                    if sent:
                        session.delete(sent)
                        
                session.commit()
                QMessageBox.information(self, "Τερματισμός", "Το περιστατικό μεταφέρθηκε στο ιστορικό επιτυχώς.")
                self.close() 
                
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα", f"Αδυναμία τερματισμού: {str(e)}")
            finally:
                session.close()


# ==========================================
# EXECUTE THE APP
# ==========================================
if __name__ == '__main__':
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    window = EKABTopRow()
    window.show()
    sys.exit(app.exec())