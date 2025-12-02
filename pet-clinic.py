import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, 
                            QVBoxLayout, QHBoxLayout, QWidget, QStackedWidget, QToolBar, QAction, 
                            QSizePolicy, QGraphicsDropShadowEffect, QMessageBox, QTableWidget,
                            QTableWidgetItem, QHeaderView, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("eul-logo.png"))
        self.setWindowTitle("Pet Clinic System")
        self.setGeometry(100, 100, 1000, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.stacked_widget = QStackedWidget()
        # self.setCentralWidget(self.stacked_widget)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.stacked_widget)

        self.init_db()
        self.create_pages()
        self.create_navigation_menu()

        self.stacked_widget.setCurrentIndex(1)
        self.showMaximized()


    def init_db(self):
        self.conn = sqlite3.connect("pet_clinic.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        # Create tables
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                species TEXT NOT NULL,
                breed TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                FOREIGN KEY(owner_id) REFERENCES owners(id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS owners(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                address TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                pet_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                FOREIGN KEY(pet_id) REFERENCES pets(id)
                FOREIGN KEY(service_id) REFERENCES services(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS services(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                cost REAL NOT NULL
            )
        """)

        #commit changes 
        self.conn.commit()

    # Function to create a message
    def show_message(self, message_type, title, message):
        msg_box = QMessageBox(self)
        if message_type == "success":
            msg_box.setIcon(QMessageBox.Information)
            
        elif message_type == "error":
            msg_box.setIcon(QMessageBox.Critical)
        
        elif message_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()
    

    def create_form_page(self, title, description, fields, submit_callback):
        page = QWidget()
        container = QWidget()
        container.setFixedWidth(700)
        container.setObjectName("container")
        container.setStyleSheet("""
                                #container{
                                    background-color: #F8FAFC;
                                    border-radius: 10px;
                                }
                            """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(5)
        shadow.setYOffset(5)
        shadow.setColor(QColor(131, 133, 138, 80))
        container.setGraphicsEffect(shadow)
        
        outer_layout = QVBoxLayout(container)
        outer_layout.setContentsMargins(30, 40, 30, 40)
        
        header = QLabel(title)
        header.setStyleSheet("""
                            font-size: 40px; 
                            font-weight: 400; 
                            letter-spacing: 1;
                        """)
        header.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        header.setFixedHeight(40)
        
        paragraph = QLabel(description)
        paragraph.setStyleSheet("""
                                font-size: 19px;
                                font-weight: 200;
                                letter-spacing: 1;
                                color: grey;
                            """)
        paragraph.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        paragraph.setFixedHeight(18)
        
        outer_layout.addWidget(header)
        outer_layout.addWidget(paragraph)
        outer_layout.addSpacing(35)
        
        inputs = {}

        # Dynamically add fields
        for field in fields:
            form_group = QHBoxLayout()
            label = QLabel(field["label"])
            label.setFixedWidth(100)
            label.setObjectName("form-label")
            line_edit = QLineEdit(self)
            line_edit.setObjectName("form-input")
            line_edit.setPlaceholderText(field["placeholder"])
            form_group.addWidget(label)
            form_group.addWidget(line_edit)
            outer_layout.addLayout(form_group)

            inputs[field["name"]] = line_edit

        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet("""
                                    font-size: 20px;
                                    padding: 15px 8px;
                                    border: none;
                                    border-radius: 8px;
                                    background-color: #133E87;   
                                    color: #F8FAFC;                 
                                """)
        submit_button.setFixedWidth(200)
        submit_button.clicked.connect(lambda: submit_callback(inputs))
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(submit_button)
        
        outer_layout.addSpacing(15)
        outer_layout.addLayout(button_layout)
        
        page_layout = QVBoxLayout()
        page_layout.addStretch()
        page_layout.addWidget(container, alignment=Qt.AlignCenter)
        page_layout.addStretch()

        self.setStyleSheet("""
            QLabel#form-label{
                font-size: 20px;
                font-weight: light;
                letter-spacing: 1;
                margin-bottom: 10px;
            }
            QLineEdit#form-input{
                font-size: 20px;
                border: none;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #664343;
            }
            QLineEdit#form-input:focus{
                border: 2px solid #133E87;
            }
            """)
        
        page.setLayout(page_layout)
        return page
            

    def create_pages(self): 
        pet_fields = [
            {"label": "Name*", "placeholder": "Enter the pet's name", "name": "name"},
            {"label": "Age*", "placeholder": "Enter the pet's age", "name": "age"},
            {"label": "Species*", "placeholder": "Enter the pet's species", "name": "species"},
            {"label": "Breed*", "placeholder": "Enter the pet's breed", "name": "breed"},
            {"label": "Owner ID*", "placeholder": "Enter the pet's owner ID", "name": "owner_id"}
        ]

        owner_fields = [
            {"label": "Name*", "placeholder": "Enter the owner's name", "name": "name"},
            {"label": "Contact*", "placeholder": "Enter the owner's contact number", "name": "contact"},
            {"label": "Email*", "placeholder": "Enter the owner's email", "name": "email"},
            {"label": "Address*", "placeholder": "Enter the owner's address", "name": "address"}
        ]

        appointment_fields = [
            {"label": "Date*", "placeholder": "Enter the appointment date", "name": "date"},
            {"label": "Time*", "placeholder": "Enter the appointment time", "name": "time"},
            {"label": "Pet ID*", "placeholder": "Enter the pet's ID", "name": "pet_id"},
            {"label": "Service ID*", "placeholder": "Enter the service ID", "name": "service_id"}
        ]

        service_fields = [
            {"label": "Service*", "placeholder": "Enter the service name", "name": "service_name"},
            {"label": "Cost*", "placeholder": "Enter the service cost", "name": "cost"}
        ]
        
        self.create_pet_page = self.create_form_page(
            "Add a New Pet", 
            "Please fill out the form below to add a new pet to the system.", 
            pet_fields,
            self.submit_pet
        )
        self.create_owner_page = self.create_form_page(
            "Add a New Owner", 
            "Please fill out the form below to add a new owner to the system.", 
            owner_fields,
            self.submit_owner
        )
        self.create_appointment_page = self.create_form_page(
            "Schedule an Appointment", 
            "Please fill out the form below to schedule an appointment.", 
            appointment_fields,
            self.submit_appointment
        )
        self.create_service_page = self.create_form_page(
            "Add a New Service", 
            "Please fill out the form below to add a new service to the system.", 
            service_fields,
            self.submit_service
        )

        self.view_pets_page = self.create_table_page("pets")
        self.view_owners_page = self.create_table_page("owners")
        self.view_appointments_page = self.create_table_page("appointments")
        self.view_services_page = self.create_table_page("services")
        
        self.stacked_widget.addWidget(self.create_pet_page)
        self.stacked_widget.addWidget(self.create_owner_page)
        self.stacked_widget.addWidget(self.create_appointment_page)
        self.stacked_widget.addWidget(self.create_service_page)
        self.stacked_widget.addWidget(self.view_pets_page)
        self.stacked_widget.addWidget(self.view_owners_page)
        self.stacked_widget.addWidget(self.view_appointments_page)
        self.stacked_widget.addWidget(self.view_services_page)

    def submit_pet(self, inputs):
        try:
            if not inputs["name"].text() or not inputs["age"].text() or not inputs["species"].text() or not inputs["breed"].text() or not inputs["owner_id"].text():
                self.show_message("warning", "Warning", "Please fill out fields marked with *")
                return
            self.cursor.execute("""
            INSERT INTO pets (name, age, species, breed, owner_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                inputs["name"].text(),
                inputs["age"].text(),
                inputs["species"].text(),
                inputs["breed"].text(),
                inputs["owner_id"].text()
            )
        )
            self.conn.commit()
            self.show_message("success", "Success", "Pet added successfully!")

            for field in inputs.values():
                field.clear()
        except sqlite3.IntegrityError as e:
            self.show_message("error", "Error", f"An error occured: {str(e)}")
        except Exception as e:
            self.show_message("error", "Error", f"An error occurred: {str(e)}") 

    def submit_owner(self, inputs):
        if not inputs["name"].text() or not inputs["contact"].text() or not inputs["email"].text() or not inputs["address"].text():
            self.show_message("warning", "Warning", "Please fill out fields marked with *")
            return
        try:
            self.cursor.execute("""
            INSERT INTO owners (name, contact, email, address)
            VALUES (?, ?, ?, ?)
            """,
            (
                inputs["name"].text(),
                inputs["contact"].text(),
                inputs["email"].text(),
                inputs["address"].text()
            )
        )
            self.conn.commit()
            self.show_message("success", "Success", "Owner added successfully!")

            for field in inputs.values():
                field.clear()
        except sqlite3.IntegrityError as e:
            self.show_message("error", "Error", f"An error occured: {str(e)}")
        except Exception as e:
            self.show_message("error", "Error", str(e))

    def submit_appointment(self, inputs):
        if not inputs["date"].text() or not inputs["time"].text() or not inputs["pet_id"].text() or not inputs["service_id"].text():
            self.show_message("warning", "Warning", "Please fill out fields marked with *")
            return
        try:
            self.cursor.execute("""
            INSERT INTO appointments (date, time, pet_id, service_id)
            VALUES (?, ?, ?, ?)
            """,
            (
                inputs["date"].text(),
                inputs["time"].text(),
                inputs["pet_id"].text(),
                inputs["service_id"].text()
            )
        )
            self.conn.commit()
            self.show_message("success", "Success", "Appointment scheduled successfully!")

            for field in inputs.values():
                field.clear()
        except sqlite3.IntegrityError as e:
            self.show_message("error", "Error", f"An error occured: {str(e)}")
        except Exception as e:
            self.show_message("error", "Error", f"An error occurred: {str(e)}")

    def submit_service(self, inputs):
        if not inputs["service_name"].text() or not inputs["cost"].text():
            self.show_message("warning", "Warning", "Please fill fields marked with *")
            return
        try:
            self.cursor.execute("""
            INSERT INTO services (service_name, cost)
            VALUES (?, ?)
            """,
            (
                inputs["service_name"].text(),
                inputs["cost"].text()
            )
        )
            self.conn.commit()
            self.show_message("success", "Success", "Service added successfully!")

            for field in inputs.values():
                field.clear()
        except sqlite3.IntegrityError as e:
            self.show_message("error", "Error", f"An error occured: {str(e)}")
        except Exception as e:
            self.show_message("error", "Error", f"An error occurred: {str(e)}")   

    ##### FOR VIEWING DATA #########
    def create_table_page(self, table_name):
        page = QWidget()
        layout = QVBoxLayout(page)

        table_widget = QTableWidget()
        table_widget.setColumnCount(0)
        table_widget.setRowCount(0)

        refresh_button = QPushButton(f"Refresh {table_name} Table")
        refresh_button.setStyleSheet("""
                                     font-size: 20px;
                                """)
        refresh_button.clicked.connect(lambda: self.populate_table(table_widget, table_name))

        layout.addWidget(refresh_button)
        layout.addWidget(table_widget)

        self.populate_table(table_widget, table_name)

        return page
    
    def populate_table(self, table_widget, table_name):
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
            column_names = [description[0] for description in self.cursor.description] #self.cursor.description contains metadata about the columns

            table_widget.setRowCount(len(rows))
            table_widget.setColumnCount(len(column_names) + 1)
            table_widget.setHorizontalHeaderLabels(column_names + ["Actions"])

            for row_idx, row_data in enumerate(rows): #enumerate returns the index and the value
                for col_idx, col_data in enumerate(row_data):
                    table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

                button_layout  = QHBoxLayout()

                update_button = QPushButton("Update")
                update_button.setObjectName("update-button")
                update_button.setFixedWidth(100)
                update_button.clicked.connect(lambda _, r=row_idx, t=table_name: self.update_record(r, t, table_widget))

                delete_button  = QPushButton("Delete")
                delete_button.setObjectName("delete-button")
                delete_button.setFixedWidth(100)
                delete_button.clicked.connect(lambda _, r=row_idx, t=table_name: self.delete_record(r, t, table_widget))

                button_widget = QWidget()
                button_layout.addWidget(update_button)
                button_layout.addWidget(delete_button)
                button_layout.setAlignment(Qt.AlignCenter)
                button_widget.setLayout(button_layout)

                table_widget.setCellWidget(row_idx, len(column_names), button_widget)
            
            table_widget.setAlternatingRowColors(True)
            table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table_widget.setStyleSheet("""
                QTableWidget {
                    background-color: #F8FAFC; /* Even rows */
                    alternate-background-color: #E2E8F0; /* Odd rows */
                    gridline-color: #CBD5E0;
                }
                QHeaderView::section {
                    background-color: #133E87;
                    font-size: 20px;
                    color: white;
                    padding: 4px;
                    border: none;
                    text-transform: uppercase;
                    font-weight: 500;
                }
                QPushButton#update-button{
                    font-size: 20px;
                    padding: 8px;
                    border: none;
                    border-radius: 8px;
                    background-color: #133E87;   
                    color: #F8FAFC;
                }
                QPushButton#delete-button{
                    font-size: 20px;
                    padding: 8px;
                    border: none;
                    border-radius: 8px;
                    background-color: red;   
                    color: #F8FAFC;
                }
            """)                       
            # self.show_message("success", "Success", f"Loaded {table_name} table successfully!")
        except sqlite3.Error as e:
            self.show_message("error", "Error", f"Failed to load table: {str(e)}")

    def update_record(self, row_idx, table_name, table_widget):
        try:
            # Get the column names from a pragma query
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [info[1] for info in self.cursor.fetchall()]

            # Get the row data
            row_data = [table_widget.item(row_idx, col_idx).text() for col_idx in range(len(columns))]

            # Prompt the user for updated values
            inputs = {}
            for col_name, col_value in zip(columns, row_data):
                new_value, ok = QInputDialog.getText(self, f"Update {col_name}", f"Enter new value for {col_name}:", text=col_value) 
                if ok:
                    inputs[col_name] = new_value
                else:
                    return  # Exit if user cancels

            # Build the update query
            primary_key = columns[0]
            primary_value = row_data[0]
            update_query = f"UPDATE {table_name} SET {', '.join([f'{key} = ?' for key in inputs.keys()])} WHERE {primary_key} = ?" #constructs column name = ?

            self.cursor.execute(update_query, list(inputs.values()) + [primary_value])
            self.conn.commit()

            self.show_message("success", "Success", "Record updated successfully!")
            self.populate_table(table_widget, table_name)  # Refresh the table

        except sqlite3.Error as e:
            self.show_message("error", "Error", f"Failed to update record: {str(e)}")
    
    def delete_record(self, row_idx, table_name, table_widget):
        try:
            # Get the primary key column
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            primary_key = self.cursor.fetchone()[1]  # First column is assumed to be the primary key

            # Get the primary key value for the row
            primary_value = table_widget.item(row_idx, 0).text()

            # Confirm deletion
            reply = QMessageBox.question(
                self, "Delete Record",
                f"Are you sure you want to delete this record?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # Delete the record
                self.cursor.execute(f"DELETE FROM {table_name} WHERE {primary_key} = ?", (primary_value,))
                self.conn.commit()

                self.show_message("success", "Success", "Record deleted successfully!")
                self.populate_table(table_widget, table_name)  # Refresh the table

        except sqlite3.Error as e:
            self.show_message("error", "Error", f"Failed to delete record: {str(e)}")

    def create_navigation_menu(self):
        self.nav_menu = self.addToolBar("Navigation Menu")
        
        create_pet_action = QAction("Create Pet", self)
        create_owner_action = QAction("Create Owner", self)
        create_appointment_action = QAction("Schedule Appointment", self)
        create_service_action = QAction("Add Service", self)
        
        create_pet_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.create_pet_page))
        create_owner_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.create_owner_page))
        create_appointment_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.create_appointment_page))
        create_service_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.create_service_page))

        view_pet_action = QAction("View Pets", self)
        view_owner_action = QAction("View Owners", self)
        view_appointment_action = QAction("View Appointments", self)
        view_service_action = QAction("View Services", self)

        view_pet_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.view_pets_page))
        view_owner_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.view_owners_page))
        view_appointment_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.view_appointments_page))
        view_service_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.view_services_page))
        
        self.nav_menu.addAction(create_pet_action)
        self.nav_menu.addAction(create_owner_action)
        self.nav_menu.addAction(create_appointment_action)
        self.nav_menu.addAction(create_service_action)
        self.nav_menu.addSeparator()
        self.nav_menu.addAction(view_pet_action)
        self.nav_menu.addAction(view_owner_action)
        self.nav_menu.addAction(view_appointment_action)
        self.nav_menu.addAction(view_service_action)
        
        self.nav_menu.setStyleSheet("""
            QToolBar{
                background-color: #F8FAFC;
                margin: 0;
            }
            QToolButton{
                background-color: transparent;
                border: none;
                padding: 8px 10px;
                font-size: 20px;
                border-radius: 8px;
            }
            QToolButton:hover{
                background-color: #CBDCEB;
            }
        """)

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())