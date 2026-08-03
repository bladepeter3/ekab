import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QCheckBox,QGridLayout
)
from PyQt6.QtCore import Qt

# --- SQLAlchemy Imports ---
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Date, Time
from sqlalchemy.orm import declarative_base, sessionmaker

# ==========================================
# 1. DATABASE SETUP (SQLAlchemy)
# ==========================================

# Create a base class for our models
Base = declarative_base()

# Define the Call Record Model
class DispatchCall(Base):
    __tablename__ = 'dispatch_calls'
    
    id = Column(Integer, primary_key=True)
    card_code = Column(Integer, default=0)
    datestamp = Column(Date, default=datetime.now().date)
    # or just for seconds too timestamp = Column(Time, default=datetime.now().time)
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
    age_unit = Column(String(10))  # e.g., "years", "months"
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
    ###########################################################
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
    sms=Column(String(20))#blood sugar
    condition_from_emt = Column(String(1000))
    approach_from_emt = Column(String(1000))
    notes_from_emt = Column(String(1000))

# Create the local SQLite file and build the table
engine = create_engine('sqlite:///emt_modern.db', echo=False)
Base.metadata.create_all(engine)

# Create a "Session". We use this later to open a temporary tunnel to the database.
Session = sessionmaker(bind=engine)



# ==========================================
# 2. GUI SETUP (PyQT6)
# ==========================================


class EKABTopRow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Εισαγωγή Περιστατικού")
        self.resize(1500, 1000) # Just a small window for this test
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # A Grid Layout is perfect here because we can tell labels exactly 
        # which columns to sit above.
        grid = QGridLayout()
        grid.setSpacing(5) # Keeps the boxes tightly packed like the image
        
        # ==========================================
        # ROW 0: The Labels
        # ==========================================
        grid.addWidget(QLabel("ΚΩΔΙΚΟΣ ΚΑΡΤΑΣ"), 0, 0)
        
        # Here we tell the Date/Time label to sit at Row 0, Column 1, 
        # and span across 1 row and 2 columns.
        grid.addWidget(QLabel("ΗΜ/ΝΙΑ & ΩΡΑ ΚΛΗΣΗΣ"), 0, 1, 1, 2) 
        
        grid.addWidget(QLabel("ΘΕΣΗ"), 0, 3)
        grid.addWidget(QLabel("ΤΗΛΕΦΩΝΗΤΗΣ"), 0, 4)
        
        # ==========================================
        # ROW 1: The Input Boxes (The first 5 fields)
        # ==========================================
        self.card_input = QLineEdit()
        self.date_input = QLineEdit("09/11/2019")
        self.time_input = QLineEdit("14:50")
        self.desk_input = QLineEdit("99")
        self.operator_input = QLineEdit("ΓΙΑΝΝΕΚΑΣ ΓΕΩΡΓΙΟΣ")
        
        # Optional: We can force some boxes to be narrow to match the image
        self.date_input.setFixedWidth(80)
        self.time_input.setFixedWidth(50)
        self.desk_input.setFixedWidth(40)
        
        # Add the inputs to Row 1
        grid.addWidget(self.card_input, 1, 0)
        grid.addWidget(self.date_input, 1, 1) # Column 1 (Under left side of the label)
        grid.addWidget(self.time_input, 1, 2) # Column 2 (Under right side of the label)
        grid.addWidget(self.desk_input, 1, 3)
        grid.addWidget(self.operator_input, 1, 4)
        
        # Add the grid to the main window and push it to the top
        main_layout.addLayout(grid)
        main_layout.addStretch()
        self.setLayout(main_layout)

# ==========================================
# EXECUTE THE APP
# ==========================================
if __name__ == '__main__':
    # Using the trick to prevent crashes if running in certain IDEs
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    window = EKABTopRow()
    window.show()
    sys.exit(app.exec())
