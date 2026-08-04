import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QCheckBox, QGridLayout, QRadioButton, QDateTimeEdit, QGroupBox,
    QStackedWidget
)
from PyQt6.QtCore import Qt, QDateTime

# --- SQLAlchemy Imports ---
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Date, Time
from sqlalchemy.orm import declarative_base, sessionmaker

# ==========================================
# 1. DATABASE SETUP (SQLAlchemy)
# ==========================================

Base = declarative_base()

class DispatchCall(Base):
    __tablename__ = 'dispatch_calls'
    
    id = Column(Integer, primary_key=True)
    card_code = Column(Integer, default=0)
    datestamp = Column(Date, default=lambda: datetime.now().date())
    timestamp = Column(String(5), default=lambda: datetime.now().strftime("%H:%M"))
    position = Column(Integer, default=0)
    emergency = Column(Boolean, default=False)
    from_address_check = Column(Boolean, default=True)
    from_medical_facility_check = Column(Boolean, default=False)
    from_icu_check = Column(Boolean, default=False)
    from_air_sea_check = Column(Boolean, default=False)
    sector=Column(String(20), default="Unknown")
    visible_all_check= Column(Boolean, default=False)
    program_from = Column(String(16), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    filter_by_municipality = Column(Boolean, default=False)
    address = Column(String(250), nullable=False)
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

engine = create_engine('sqlite:///emt_modern.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

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
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)
        
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
        self.card_input = QLineEdit("10")
        self.date_input = QLineEdit("09/11/2019")
        self.time_input = QLineEdit("14:50")
        self.desk_input = QLineEdit("99")
        self.operator_input = QLineEdit("ΓΙΑΝΝΕΚΑΣ ΓΕΩΡΓΙΟΣ")
    
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
        addr_grid.addWidget(self.street_input, 1, 0)
        self.map_btn_1 = QPushButton("🗺️") 
        self.map_btn_1.setFixedWidth(30)
        addr_grid.addWidget(self.map_btn_1, 1, 1)
        self.number_input = QLineEdit()
        self.number_input.setFixedWidth(50)
        addr_grid.addWidget(self.number_input, 1, 2)
        self.floor_combo = QComboBox()
        self.floor_combo.addItems(["","ΥΠΟΓΕΙΟ", "ΙΣΟΓΕΙΟ","ΗΜΙΟΡΟΦΟΣ", "1ος", "2ος", "3ος", "4ος", "5ος", "6ος"])
        self.floor_combo.setMaximumWidth(250)
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

        # END OF SETUP_UI
        main_layout.addStretch()
        self.setLayout(main_layout)

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