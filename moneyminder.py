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
sql_connector = SqlConnector(data['host'], data['user'], data['password'])
# Connect to the MySQL database
sql_connector.connect_to_database()
# Disconnect from the MySQL
sql_connector.disconnect()

# Create an instance of the menu
menu = Menu()
# Start the menu loop
menu.handle_input()