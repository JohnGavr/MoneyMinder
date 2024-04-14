import json
import os
from datetime import datetime
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
        self.cursor = None
        
    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(
                host = self.host,
                user = self.user,
                password = self.password,
                database = self.database,
                )
            self.cursor = self.connection.cursor()
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
            # Construct the CREATE TABLE statement with IF NOT EXISTS clause
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)}"
            if foreign_keys:
                create_table_query += f", {', '.join(foreign_keys)}"
            create_table_query += ")"
            self.cursor.execute(create_table_query)
            self.connection.commit()
            print(f"Table '{table_name}' created or already exists.")
        except mysql.connector.Error as error:
            print(f"Error: {error}")
            
    def create_database(self, database_name):
        try:
            # Execute the SQL query to create the database
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            print(f"Database '{database_name}' created or already exists.")
            self.cursor.close()
        except mysql.connector.Error as error:
            print(f"Error: {error}")
            
    def insert_data(self, table_name, data):
        try:
            # Construct the INSERT INTO statement
            columns = ', '.join(data.keys())
            values_template = ', '.join(['%s'] * len(data))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values_template})"

            # Execute the query with data values
            self.cursor.execute(insert_query, list(data.values()))

            # Commit the transaction
            self.connection.commit()
            print(f"Data inserted into '{table_name}' successfully.")
        except mysql.connector.Error as error:
            print(f"Error: {error}")
            
    def insert_default_kind_values(self):
        try:
            # Check if KIND table is empty
            self.cursor.execute("SELECT COUNT(*) FROM KIND")
            count = self.cursor.fetchone()[0]

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
                self.cursor.executemany(insert_query, default_values)

                # Commit the transaction
                self.connection.commit()
                print("Default values inserted into 'KIND' table successfully.")
            else:
                print("Default values already exist in 'KIND' table.")
        except mysql.connector.Error as error:
            print(f"Error: {error}")

    def insert_default_category_values(self):
        try:
            # Check if CATEGORY table is empty
            self.cursor.execute("SELECT COUNT(*) FROM CATEGORY")
            count = self.cursor.fetchone()[0]

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
                self.cursor.executemany(insert_query, default_values)

                # Commit the transaction
                self.connection.commit()
                print("Default values inserted into 'CATEGORY' table successfully.")
            else:
                print("Default values already exist in 'CATEGORY' table.")
        except mysql.connector.Error as error:
            print(f"Error: {error}")
            
class Menu:
    def __init__(self,cursor):
        self.running = True
        self.cursor = cursor # Store the cursror as an instance variable.

    def display_menu(self):
        print("Menu:")
        print("1. Add Transaction")
        print("2. Configuration")
        print("0. Exit")

    def handle_input(self):
        while self.running:
            self.display_menu()
            choice = input("Enter your choice: ")

            if choice == "1":
                self.add_transaction()
            elif choice == "2":
                self.configure_submenu()
            elif choice == "0":
                self.exit_program()
            else:
                print("Invalid choice. Please try again.")

    def add_transaction(self):
        kind_choice= self.select_kind()
        category_choice = self.select_category(kind_choice)
        transaction_date= self.get_transaction_date()
        transaction_value = self.transaction_value()
        comments = self.get_comments()

        transaction_data ={
            "KINDID": kind_choice,
            "CATEGORYID": category_choice,
            "DATE": transaction_date,
            "VALUE": transaction_value,
            "COMMENTS": comments
        }
        sql_connector.insert_data("TRANSACTIONS", transaction_data)
        print("Transaction added successfully")


    def get_comments(self):
        while True:
            comments = input("Enter any comments (press Enter to skip): ")
            if comments.strip() == "":
                return None  # Return None if the user skips entering comments
            else:
                return comments  # Return the comments entered by the user
        
    def select_kind(self):    
        print("Select Transaction Type:")
        try:
            self.cursor.execute("SELECT ID, DESCRIPTION FROM KIND")
            kinds = self.cursor.fetchall()
            for kind in kinds:
                print(f"{kind[0]}. {kind[1]}")
            kind_choice = input("Enter your choice:")
            return kind_choice
        except mysql.connector.Error as error:
            print(f"Error: {error}")

    def select_category(self, kind_choice):
        print("Select Category Type:")
        try:
            self.cursor.execute(f"SELECT * FROM CATEGORY WHERE KINDID = {kind_choice}")
            categories = self.cursor.fetchall()
            if categories:
                category_mapping = {}  # Create an empty dictionary to store the mapping
                # Initialize a counter variable
                counter = 1
                for category in categories:
                    print(f"{counter}. {category[1]}")  # Display the counter along with the category description
                    category_mapping[counter] = category[0]  # Map the counter to the actual category ID
                    counter += 1  # Increment the counter
            else:
                print("No categories found for the selected kind.")
        except mysql.connector.Error as error:
            print(f"Error: {error}")
    
        while True:
            category_choice_input = input("Enter your choice: ")
            try:
                category_choice = int(category_choice_input)
                if category_choice in category_mapping:
                    return category_mapping[category_choice]  # Return the actual category ID
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def transaction_value(self):
        while True:
            value_str = input("Enter the value of the transaction (e.g., 12.34): ")
            try:
                # Try to convert the input string to a float
                value = float(value_str)
                # Check if the value has exactly two decimal places
                if round(value, 2) == value:
                    return value  # Return the value if it's valid
                else:
                    print("Please enter a value with exactly two decimal places.")
            except ValueError:
                print("Please enter a valid number.")

    def get_transaction_date(self):
        while True:
            date_str = input("Enter the date of the transaction (DD-MM-YYYY): ")
            try:
            # Try to parse the input string as a date with the specified format
                transaction_date = datetime.strptime(date_str, "%d-%m-%Y").date()
                return transaction_date  # Return the parsed date if successful
            except ValueError:
                print("Please enter a date in the format DD-MM-YYYY.")

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
menu = Menu(sql_connector.cursor)
# Start the menu loop
menu.handle_input()