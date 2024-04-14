import json
import os
import mysql.connector

class DatabaseConfig:
    def __init__(self, config_file):
        self.config_file = config_file
        
    def load_json(self):
        if not os.path.exists(self.config_file):
            print("Please complete the configuration file")
            self.create_new_config()
            
        with open(self.config_file, 'r', encoding = 'utf-8') as file:
            loaded_data = json.load(file)
            return loaded_data
    
    def save_json(self, data):
        with open(self.config_file, 'w', encoding='utf-8') as file:
            json.dump(data, file)
            
    def create_new_config(self):
        new_data = {
            'host': input("Enter host: "),
            'user': input("Enter user: "),
            'password': input("Enter Password: "),
            'database': input("Enter database: ")
            }
        with open(self.config_file, 'w', encoding='utf-8') as file:
            json.dump(new_data, file)
            
        print("New configuration file created successfully.")

class SqlConnector:
    def __init__(self, host, user, password, database=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(
                host = self.host,
                user = self.user,
                password = self.password,
                database = self.database,
                )
            print("Connected to MySQL database successfully.")
        except mysql.connector.Error as mistake:
            print(f"Error: {mistake}")
            
    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from MySQL database.")
            
    def create_tables(self, tables):
        for table_name, (columns, foreign_keys) in tables.items():
            self.create_table(table_name, columns, foreign_keys)

    def create_table(self, table_name, columns, foreign_keys=None):
        try:
            cursor = self.connection.cursor()
            # Construct the CREATE TABLE statement with IF NOT EXISTS clause
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)}"
            if foreign_keys:
                create_table_query += f", {', '.join(foreign_keys)}"
            create_table_query += ")"
            cursor.execute(create_table_query)
            self.connection.commit()
            print(f"Table '{table_name}' created or already exists.")
        except mysql.connector.Error as error:
            print(f"Error: {error}")
            
    def create_database(self, database_name):
        try:
            cursor = self.connection.cursor()
            # Execute the SQL query to create the database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            print(f"Database '{database_name}' created or already exists.")
            cursor.close()
        except mysql.connector.Error as error:
            print(f"Error: {error}")
            
    def insert_data(self, table_name, data):
        try:
            cursor = self.connection.cursor()

            # Construct the INSERT INTO statement
            columns = ', '.join(data.keys())
            values_template = ', '.join(['%s'] * len(data))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values_template})"

            # Execute the query with data values
            cursor.execute(insert_query, list(data.values()))

            # Commit the transaction
            self.connection.commit()
            print(f"Data inserted into '{table_name}' successfully.")
        except mysql.connector.Error as error:
            print(f"Error: {error}")
            
    def insert_default_kind_values(self):
        try:
            cursor = self.connection.cursor()

            # Check if KIND table is empty
            cursor.execute("SELECT COUNT(*) FROM KIND")
            count = cursor.fetchone()[0]

            if count == 0:
                # Define default values for KIND table
                default_values = [
                    ('1', 'Revenue'),
                    ('2', 'Expenses')
                    # Add more default values as needed
                ]

                # Construct the INSERT INTO statement
                insert_query = "INSERT INTO KIND (ID, DESCRIPTION) VALUES (%s, %s)"

                # Execute the query for each default value
                cursor.executemany(insert_query, default_values)

                # Commit the transaction
                self.connection.commit()
                print("Default values inserted into 'KIND' table successfully.")
            else:
                print("Default values already exist in 'KIND' table.")
        except mysql.connector.Error as error:
            print(f"Error: {error}")

    def insert_default_category_values(self):
        try:
            cursor = self.connection.cursor()

            # Check if CATEGORY table is empty
            cursor.execute("SELECT COUNT(*) FROM CATEGORY")
            count = cursor.fetchone()[0]

            if count == 0:
                # Define default values for CATEGORY table
                default_values = [
                    ('1', 'Salary', '1'),  # Assuming KIND ID 0 is default
                    ('2', 'Other', '1'),
                    ('3', 'Going Out', '2'),   # Assuming KIND ID 1 is default
                    ('4', 'Smoking', '2'),
                    ('5', 'Shopping', '2'),
                    ('6', 'Vehicles and gas', '2'),
                    ('7', 'Other', '2')
                    # Add more default values as needed
                ]

                # Construct the INSERT INTO statement
                insert_query = "INSERT INTO CATEGORY (ID, DESCRIPTION, KINDID) VALUES (%s, %s, %s)"

                # Execute the query for each default value
                cursor.executemany(insert_query, default_values)

                # Commit the transaction
                self.connection.commit()
                print("Default values inserted into 'CATEGORY' table successfully.")
            else:
                print("Default values already exist in 'CATEGORY' table.")
        except mysql.connector.Error as error:
            print(f"Error: {error}")
            
class Menu:
    def __init__(self):
        self.running = True

    def display_menu(self):
        print("Menu:")
        print("1. Configuration")
        print("0. Exit")

    def handle_input(self):
        while self.running:
            self.display_menu()
            choice = input("Enter your choice: ")

            if choice == "1":
                self.configure_submenu()
            elif choice == "0":
                self.exit_program()
            else:
                print("Invalid choice. Please try again.")

    def configure_submenu(self):
        submenu_running = True
        while submenu_running:
            print("Configuration Submenu:")
            print("1. View Configuration")
            print("2. Change Configuration")
            print("3. Back to Main Menu")

            submenu_choice = input("Enter your choice: ")

            if submenu_choice == "1":
                self.view_configuration()
            elif submenu_choice == "2":
                self.change_configuration()
            elif submenu_choice == "3":
                submenu_running = False
            else:
                print("Invalid choice. Please try again.")

    def view_configuration(self):
        print("Current Configuration:")
        print(f"Host: {data['host']}")
        print(f"User: {data['user']}")
        print(f"Password: {data['password']}")
        print(f"Database: {data['database']}")
        input("Press Enter to go to Submenu...")

    def change_configuration(self):
        print("Enter new configuration:(If you want the old value Press Enter")
        new_host = input(f"Host [{data['host']}]: ") or data['host']
        new_user = input(f"User [{data['user']}]: ") or data['user']
        new_password = input(f"Password [{data['password']}]: ") or data['password']
        new_database = input(f"Database [{data['database']}]: ") or data['database']

        # Update the configuration file
        new_data = {
            'host': new_host,
            'user': new_user,
            'password': new_password,
            'database': new_database
        }
        db_config.save_json(new_data)
        print("Configuration updated successfully.")
        # Reload the configuration
        self.reload_configuration()

    def reload_configuration(self):
        global data  # Declare data as global to update its value
        data = db_config.load_json()

    def exit_program(self):
        print("Exiting program.")
        self.running = False
            

configuration = "database_config.json"

db_config = DatabaseConfig(configuration)
data = db_config.load_json()

# Testing Connection
test_sql_connector = SqlConnector(data['host'], data['user'], data['password'])
# Connect to the MySQL database
test_sql_connector.connect_to_database()
test_sql_connector.create_database(data['database'])
# Disconnect from the MySQL
test_sql_connector.disconnect()

sql_connector = SqlConnector(data['host'], data['user'], data['password'], data['database'])
sql_connector.connect_to_database()
# Define tables with columns and foreign keys
tables = {
    "KIND": ([
        "ID INTEGER PRIMARY KEY AUTO_INCREMENT",
        "DESCRIPTION VARCHAR(50)"
    ], None),
    "CATEGORY": ([
        "ID INTEGER PRIMARY KEY AUTO_INCREMENT",
        "DESCRIPTION VARCHAR(50)",
        "KINDID INTEGER",
        "FOREIGN KEY (KINDID) REFERENCES KIND(ID)"
    ], None),
    "TRANSACTIONS": ([
        "ID INTEGER PRIMARY KEY AUTO_INCREMENT",
        "KINDID INTEGER",
        "CATEGORYID INTEGER",
        "DATE DATE",
        "VALUE FLOAT",
        "COMMENTS VARCHAR(255)",
        "FOREIGN KEY (KINDID) REFERENCES KIND(ID)",
        "FOREIGN KEY (CATEGORYID) REFERENCES CATEGORY(ID)"
    ], None)
}

sql_connector.create_tables(tables)
sql_connector.insert_default_kind_values()
sql_connector.insert_default_category_values()


# Create an instance of the menu
menu = Menu()
# Start the menu loop
menu.handle_input()