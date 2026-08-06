import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFormLayout, 
    QMessageBox, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt

# --- SQLAlchemy Imports ---
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# ==========================================
# 1. STANDALONE DATABASE SETUP (users.db)
# ==========================================
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False) 
    
    # ---> NEW COLUMN: Role (ΤΗΛΕΦΩΝΗΤΗΣ / ΑΣΥΡΜΑΤΙΣΤΗΣ) <---
    role = Column(String(50), nullable=False)

# Connect to the standalone database file
engine = create_engine('sqlite:///users.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# ==========================================
# 2. GUI SETUP
# ==========================================
class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Εγγραφή Νέου Χρήστη")
        self.resize(400, 400) # Made slightly taller to fit the new field
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # Title Label
        title_label = QLabel("Δημιουργία Λογαριασμού")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Form Layout for Inputs
        form_layout = QFormLayout()
        
        # Name and Last Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Όνομα")
        
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Επώνυμο")
        
        # ---> NEW: Role Dropdown <---
        self.role_combo = QComboBox()
        self.role_combo.addItems(["ΤΗΛΕΦΩΝΗΤΗΣ", "ΑΣΥΡΜΑΤΙΣΤΗΣ","ΤΗΛΕΦΩΝΗΤΗΣ & ΑΣΥΡΜΑΤΙΣΤΗΣ"])  # Added a combined role option
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Επιθυμητό όνομα χρήστη")
        
        # Passwords
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow(QLabel("Όνομα:"), self.name_input)
        form_layout.addRow(QLabel("Επώνυμο:"), self.last_name_input)
        
        # Add the new dropdown to the form
        form_layout.addRow(QLabel("Θέση:"), self.role_combo)
        
        form_layout.addRow(QLabel("Username:"), self.username_input)
        form_layout.addRow(QLabel("Κωδικός:"), self.password_input)
        form_layout.addRow(QLabel("Επιβεβαίωση:"), self.confirm_password_input)
        
        main_layout.addLayout(form_layout)

        # Show Password Checkbox
        self.show_password_check = QCheckBox("Εμφάνιση Κωδικών")
        self.show_password_check.toggled.connect(self.toggle_password_visibility)
        main_layout.addWidget(self.show_password_check, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addStretch()

        # Buttons Layout
        btn_layout = QHBoxLayout()
        
        self.btn_cancel = QPushButton("Ακύρωση")
        self.btn_cancel.clicked.connect(self.close) 
        
        self.btn_create = QPushButton("Δημιουργία")
        self.btn_create.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 6px;")
        self.btn_create.clicked.connect(self.register_user)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_create)
        
        main_layout.addLayout(btn_layout)

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def register_user(self):
        # 1. Get text from inputs
        name = self.name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        role = self.role_combo.currentText() # Grab the selected role
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # 2. Basic Validation (Empty fields)
        if not all([name, last_name, username, password, confirm_password]):
            QMessageBox.warning(self, "Σφάλμα", "Παρακαλώ συμπληρώστε όλα τα πεδία.")
            return
            
        # 3. Password Match Validation
        if password != confirm_password:
            QMessageBox.warning(self, "Σφάλμα", "Οι κωδικοί δεν ταιριάζουν!")
            self.password_input.clear()
            self.confirm_password_input.clear()
            return
            
        # 4. Database Interaction
        session = Session()
        
        # Check if the username already exists
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            QMessageBox.warning(self, "Σφάλμα", f"Το όνομα χρήστη '{username}' χρησιμοποιείται ήδη. Επιλέξτε άλλο.")
            session.close()
            return
            
        # Create and add the new user, now including their role!
        new_user = User(
            name=name,
            last_name=last_name,
            username=username,
            password=password,
            role=role 
        )
        
        try:
            session.add(new_user)
            session.commit()
            QMessageBox.information(self, "Επιτυχία", "Ο λογαριασμός δημιουργήθηκε με επιτυχία!")
            self.close() 
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Σφάλμα", f"Προέκυψε σφάλμα κατά την αποθήκευση: {str(e)}")
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
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec())