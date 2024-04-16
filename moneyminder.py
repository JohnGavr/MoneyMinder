import json
import os
from datetime import datetime
import mysql.connector
from prettytable import PrettyTable

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
    ''' Managing Sql Actions'''
    def __init__(self, host, user, password, database=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        
    def connect_to_database(self):
        '''Connect to database'''
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
        '''Disconnect from database'''
        if self.connection:
            self.connection.close()
            print("Disconnected from MySQL database.")

    def create_tables(self, tables):
        '''Create table'''
        for table_name, (columns, foreign_keys) in tables.items():
            self.create_table(table_name, columns, foreign_keys)

    def create_table(self, table_name, columns, foreign_keys=None):
        '''Create table'''
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
        '''Create the database'''
        try:
            # Execute the SQL query to create the database
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            print(f"Database '{database_name}' created or already exists.")
            self.cursor.close()
        except mysql.connector.Error as error:
            print(f"Error: {error}")

    def insert_data(self, table_name, data):
        ''' Insert Data to MySql'''
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
        '''Insert initial Data'''
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
        '''Insert initial Data'''
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

    def select_from_table(self, atribbutes, table_name, condition=None):
        ''' Select From table'''
        try:
            query = f"SELECT {atribbutes} from {table_name}"
            if condition:
                query += f" WHERE {condition}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"Error: {error}")
            return None

class Menu:
    '''The Menu of App'''
    def __init__(self,cursor):
        self.running = True
        self.cursor = cursor # Store the cursror as an instance variable.

    def display_menu(self):
        '''Main Menu'''
        print("Menu:")
        print("1. Add Transaction")
        print("2. Reports")
        print("3. Configuration")
        print("0. Exit")

    def handle_input(self):
        '''Handle the input of Main Menu'''
        while self.running:
            self.display_menu()
            choice = input("Enter your choice: ")

            if choice == "1":
                self.add_transaction()
            elif choice =="2":
                self.submenu_reports()
            elif choice == "3":
                self.configure_submenu()
            elif choice == "0":
                self.exit_program()
            else:
                print("Invalid choice. Please try again.")

    def submenu_reports(self):
        ''' Submenu of Reports'''
        submenu_running = True
        while submenu_running:
            print("Reports Submenu:")
            print("1. Total Revenue")
            print("2. Total Expenses")
            print("3. Back to Main Menu")

            submenu_choice = input("Enter your choice: ")

            if submenu_choice == "1":
                self.analytical_report(1)
            elif submenu_choice == "2":
                self.analytical_report(2)
            elif submenu_choice == "3":
                submenu_running = False
            else:
                print("Invalid choice. Please try again.")

    def analytical_report(self, kind):
        ''' Report for Revenues and Expenses Analytical'''
        attributes_table = "ID,DATE,VALUE,COMMENTS"
        conditions_table = f"KINDID={kind}"
    
        # Ask the user if they want to set a date range
        set_date_range = input("Do you want to set a date range? (Y/N): ").upper()
        if set_date_range == 'Y':
            # Prompt the user to enter the date range
            date_from = input("Enter the start date (YYYY-MM-DD): ")
            date_to = input("Enter the end date (YYYY-MM-DD): ")
            # Convert date strings to datetime objects
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            # Format the date range condition
            date_condition = f"DATE BETWEEN '{date_from_obj.strftime('%Y-%m-%d')}' AND '{date_to_obj.strftime('%Y-%m-%d')}'"
            # Add the date range condition to the query
            conditions_table += f" AND {date_condition}"

        entries = sql_connector.select_from_table(attributes_table, "TRANSACTIONS", conditions_table)

    # Convert tuple to list, modify the date format, and convert back to tuple
        modified_entries = [list(row) for row in entries]
        for row in modified_entries:
            row[1] = row[1].strftime('%d-%m-%Y')
    
        table = PrettyTable()
        table.field_names = ["ID", "DATE", "VALUE", "COMMENTS"]
        for row in modified_entries:
            table.add_row(row)
        print(table)



    def add_transaction(self):
        ''' Add transaction, creating the insert statement values'''
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
        ''' Comments for transaction'''
        while True:
            comments = input("Enter any comments (press Enter to skip): ")
            if comments.strip() == "":
                return None  # Return None if the user skips entering comments
            else:
                return comments  # Return the comments entered by the user

    def select_kind(self):
        ''' Kind of transaction'''    
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
        '''Category of transaction'''
        print("Select Category Type:")
        try:
            self.cursor.execute(f"SELECT * FROM CATEGORY WHERE KINDID = {kind_choice}")
            categories = self.cursor.fetchall()
            if categories:
                category_mapping = {}  # Create an empty dictionary to store the mapping
                # Initialize a counter variable
                counter = 1
                for category in categories:
                    # Display the counter along with the category description
                    print(f"{counter}. {category[1]}")
                    # Map the counter to the actual category ID
                    category_mapping[counter] = category[0]  
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
        '''Value of transaction'''
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
        '''Date of transaction'''
        while True:
            date_str = input("Enter the date of the transaction (DD-MM-YYYY): ")
            try:
            # Try to parse the input string as a date with the specified format
                transaction_date = datetime.strptime(date_str, "%d-%m-%Y").date()
                return transaction_date  # Return the parsed date if successful
            except ValueError:
                print("Please enter a date in the format DD-MM-YYYY.")

    def configure_submenu(self):
        ''' Configure configuration file'''
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
        ''' View configuration file'''
        print("Current Configuration:")
        print(f"Host: {data['host']}")
        print(f"User: {data['user']}")
        print(f"Password: {data['password']}")
        print(f"Database: {data['database']}")
        input("Press Enter to go to Submenu...")

    def change_configuration(self):
        ''' Change configuration file'''
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
        ''' Reload the changes of configuration file'''
        global data  # Declare data as global to update its value
        data = db_config.load_json()

    def exit_program(self):
        '''Exit program'''
        print("Exiting program.")
        sql_connector.cursor.close()
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