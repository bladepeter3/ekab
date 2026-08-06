import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFormLayout, QMessageBox,
    QComboBox
)
from PyQt6.QtCore import Qt

# --- SQLAlchemy Imports ---
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# --- Dashboard Import ---
from main_ui import DispatcherDashboard

# ==========================================
# 1. MAIN USERS DATABASE SETUP (users.db)
# ==========================================
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False) 
    role = Column(String(50), nullable=False)

engine = create_engine('sqlite:///users.db', echo=False)
Session = sessionmaker(bind=engine)

# ==========================================
# 2. DAILY LOGIN TRACKING DATABASE SETUP
# ==========================================
LogBase = declarative_base()

class LoginRecord(LogBase):
    __tablename__ = 'login_history'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    timestamp = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)
    position = Column(String(50), nullable=True)


# ==========================================
# 3. GUI SETUP
# ==========================================
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Είσοδος Χρήστη - ΕΚΑΒ")
        self.resize(350, 280) # Made taller to fit the new field
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title_label = QLabel("Σύστημα Τηλεφωνητή")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Όνομα χρήστη")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Κωδικός")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.shift_role_combo = QComboBox()
        self.shift_role_combo.addItems(["ΤΗΛΕΦΩΝΗΤΗΣ", "ΑΣΥΡΜΑΤΙΣΤΗΣ"])
        
        # ---> NEW: Position (ΘΕΣΗ) Field <---
        self.position_label = QLabel("Αριθμός Θέσης:")
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("π.χ. 1, 2, 3...")
        
        form_layout.addRow(QLabel("Χρήστης:"), self.username_input)
        form_layout.addRow(QLabel("Κωδικός:"), self.password_input)
        form_layout.addRow(QLabel("Θέση Βάρδιας:"), self.shift_role_combo)
        form_layout.addRow(self.position_label, self.position_input) # Add to layout
        
        main_layout.addLayout(form_layout)

        # Connect the dropdown change to our show/hide function
        self.shift_role_combo.currentTextChanged.connect(self.toggle_position_field)
        
        # Trigger it once immediately to set the correct visual state upon opening
        self.toggle_position_field(self.shift_role_combo.currentText())

        btn_layout = QHBoxLayout()
        
        self.btn_cancel = QPushButton("Ακύρωση")
        self.btn_cancel.clicked.connect(self.close)
        
        self.btn_login = QPushButton("Είσοδος")
        self.btn_login.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_login.clicked.connect(self.check_credentials)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_login)
        
        main_layout.addLayout(btn_layout)

    def toggle_position_field(self, text):
        """Shows or hides the position input based on the selected role."""
        if text == "ΤΗΛΕΦΩΝΗΤΗΣ":
            self.position_label.show()
            self.position_input.show()
        else:
            self.position_label.hide()
            self.position_input.hide()
            self.position_input.clear() # Clear it so it doesn't accidentally get submitted

    def log_user_login(self, name, last_name, role, position): # <--- Add 'position' here
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        exact_time = now.strftime("%H:%M:%S")
        
        db_filename = f"sqlite:///logins_{today_date}.db"
        
        log_engine = create_engine(db_filename, echo=False)
        LogBase.metadata.create_all(log_engine)
        LogSession = sessionmaker(bind=log_engine)
        log_session = LogSession()
        
        try:
            # ---> Pass the position into the new log entry <---
            new_log = LoginRecord(name=name, last_name=last_name, timestamp=exact_time, role=role, position=position)
            log_session.add(new_log)
            log_session.commit()
        except Exception as e:
            print(f"Σφάλμα κατά την καταγραφή: {e}")
        finally:
            log_session.close()

    def check_credentials(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        selected_shift_role = self.shift_role_combo.currentText()
        
        # Grab the Position number (if applicable)
        position_number = self.position_input.text().strip()
        
        # ---> NEW: Validation for Position <---
        if selected_shift_role == "ΤΗΛΕΦΩΝΗΤΗΣ" and not position_number:
            QMessageBox.warning(self, "Σφάλμα", "Επιλέξατε ΤΗΛΕΦΩΝΗΤΗΣ. Παρακαλώ εισάγετε τον Αριθμό Θέσης (π.χ. 1, 2).")
            return
            
        if not username or not password:
            QMessageBox.warning(self, "Σφάλμα", "Παρακαλώ εισάγετε όνομα χρήστη και κωδικό.")
            return

        session = Session()
        
        try:
            user = session.query(User).filter_by(username=username).first()
            
            if user and user.password == password:
                
                if user.role != "ΤΗΛΕΦΩΝΗΤΗΣ & ΑΣΥΡΜΑΤΙΣΤΗΣ" and user.role != selected_shift_role:
                    QMessageBox.warning(self, "Σφάλμα Δικαιωμάτων", f"Ο λογαριασμός σας έχει δικαιώματα μόνο για: {user.role}.\nΔεν μπορείτε να συνδεθείτε ως {selected_shift_role}.")
                    return 

                # 1. Record the login in today's logbook
                self.log_user_login(user.name, user.last_name, selected_shift_role, position_number)
                
                self.dashboard = DispatcherDashboard()
                
                # ---> NEW: Save the position number directly inside the dashboard memory! <---
                self.dashboard.shift_position = position_number
                
                # Update header to show the position if it exists
                header_text = f"Χρήστης: {user.username} ({user.name} {user.last_name}), Θέση: {selected_shift_role}"
                if position_number:
                    header_text += f" (Γραμμή: {position_number})"
                self.dashboard.user_label.setText(header_text)
                
                self.dashboard.show()
                self.close()
                
            else:
                QMessageBox.warning(self, "Σφάλμα", "Λάθος όνομα χρήστη ή κωδικός.\nΠαρακαλώ δοκιμάστε ξανά.")
                self.password_input.clear() 
                self.password_input.setFocus() 
                
        except Exception as e:
            QMessageBox.critical(self, "Σφάλμα", f"Αδυναμία σύνδεσης στη βάση δεδομένων: {str(e)}")
        finally:
            session.close()

# ==========================================
if __name__ == '__main__':
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())