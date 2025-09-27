import mysql.connector
from mysql.connector import Error
import random
import string
from datetime import datetime, timedelta

class Train:
    def __init__(self, train_id, capacity, train_type, arrival_time, departure_time):
        self.train_id = train_id
        self.capacity = capacity
        self.train_type = train_type
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.reservations = 0

    def book_ticket(self):
        if self.reservations < self.capacity:
            self.reservations += 1
            return True
        else:
            return False

    def cancel_ticket(self):
        if self.reservations > 0:
            self.reservations -= 1
            return True
        else:
            return False

    def __str__(self):
        return f"Train ID: {self.train_id}, Capacity: {self.capacity}, Reserved: {self.reservations}, Train Type: {self.train_type}, Arrival: {self.arrival_time}, Departure: {self.departure_time}"

class ReservationSystem:
    def __init__(self):
        self.connection = self.create_connection()
        if self.connection:
            self.cursor = self.connection.cursor()
            self.load_predefined_trains()
        else:
            self.cursor = None

    def create_connection(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',  # Update with your MySQL root password
                database='train_reservation'
            )
            if connection.is_connected():
                print("Successfully connected to the database.")
                return connection
        except Error as e:
            print(f"Error: {e}")
            return None

    def load_predefined_trains(self):
        predefined_trains = [
            ("T001", 100, "Express", "2024-07-28 10:00:00", "2024-07-28 09:30:00"),
            ("T002", 150, "Superfast", "2024-07-28 12:00:00", "2024-07-28 11:30:00"),
            ("T003", 200, "Local", "2024-07-28 14:00:00", "2024-07-28 13:30:00")
        ]
        for train in predefined_trains:
            self.add_train(*train)

    def add_train(self, train_id, capacity, train_type, arrival_time, departure_time):
        if self.cursor:
            try:
                if self.train_exists(train_id):
                    print(f"Train {train_id} already exists.")
                    return
                query = "INSERT INTO trains (train_id, capacity, reservations, train_type, arrival_time, departure_time) VALUES (%s, %s, %s, %s, %s, %s)"
                values = (train_id, capacity, 0, train_type, arrival_time, departure_time)
                self.cursor.execute(query, values)
                self.connection.commit()
                print(f"Train {train_id} added successfully.")
            except Error as e:
                print(f"Error: {e}")
        else:
            print("Database connection is not available.")

    def train_exists(self, train_id):
        if self.cursor:
            try:
                query = "SELECT COUNT(*) FROM trains WHERE train_id = %s"
                self.cursor.execute(query, (train_id,))
                return self.cursor.fetchone()[0] > 0
            except Error as e:
                print(f"Error: {e}")
                return False
        return False

    def generate_ticket_id(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    def generate_seat_number(self, train_id):
        if self.cursor:
            try:
                query = "SELECT COUNT(*) FROM passengers WHERE train_id = %s"
                self.cursor.execute(query, (train_id,))
                return self.cursor.fetchone()[0] + 1
            except Error as e:
                print(f"Error: {e}")
                return 1
        return 1

    def book_ticket(self, train_id, passenger_details):
        if self.cursor:
            if self.train_exists(train_id):
                try:
                    self.cursor.execute("SELECT capacity, reservations, arrival_time, departure_time FROM trains WHERE train_id = %s", (train_id,))
                    train = self.cursor.fetchone()
                    if train:
                        capacity, reservations, arrival_time, departure_time = train
                        if reservations < capacity:
                            new_reservations = reservations + 1
                            update_query = "UPDATE trains SET reservations = %s WHERE train_id = %s"
                            self.cursor.execute(update_query, (new_reservations, train_id))
                            self.connection.commit()

                            # Generate random ticket ID and seat number
                            ticket_id = self.generate_ticket_id()
                            seat_number = self.generate_seat_number(train_id)

                            # Add passenger details
                            passenger_query = """
                                INSERT INTO passengers (name, phone, email, ticket_id, train_id, seat_number, arrival_time, departure_time, scheduled_station, station_name)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            passenger_details_with_generated = (passenger_details[0], passenger_details[1], passenger_details[2], ticket_id, train_id, seat_number, arrival_time, departure_time, passenger_details[3], passenger_details[4])
                            self.cursor.execute(passenger_query, passenger_details_with_generated)
                            self.connection.commit()

                            print(f"Ticket booked successfully. Ticket ID: {ticket_id}, Seat Number: {seat_number}, Arrival Time: {arrival_time}, Departure Time: {departure_time}")
                        else:
                            print("Booking failed. Train might be full.")
                except Error as e:
                    print(f"Error: {e}")
            else:
                print("Train not found.")
        else:
            print("Database connection is not available.")

    def cancel_ticket(self, train_id, ticket_id):
        if self.cursor:
            if self.train_exists(train_id):
                try:
                    self.cursor.execute("SELECT reservations FROM trains WHERE train_id = %s", (train_id,))
                    reservations = self.cursor.fetchone()[0]
                    if reservations > 0:
                        new_reservations = reservations - 1
                        update_query = "UPDATE trains SET reservations = %s WHERE train_id = %s"
                        self.cursor.execute(update_query, (new_reservations, train_id))
                        self.connection.commit()

                        # Remove passenger details
                        delete_query = "DELETE FROM passengers WHERE ticket_id = %s AND train_id = %s"
                        self.cursor.execute(delete_query, (ticket_id, train_id))
                        self.connection.commit()

                        print("Ticket canceled successfully.")
                    else:
                        print("Cancellation failed. No reservations to cancel.")
                except Error as e:
                    print(f"Error: {e}")
            else:
                print("Train not found.")
        else:
            print("Database connection is not available.")

    def view_train(self, train_id):
        if self.cursor:
            if self.train_exists(train_id):
                try:
                    self.cursor.execute("SELECT * FROM trains WHERE train_id = %s", (train_id,))
                    train = self.cursor.fetchone()
                    if train:
                        print(f"Train ID: {train[0]}, Capacity: {train[1]}, Reserved: {train[2]}, Train Type: {train[3]}, Arrival Time: {train[4]}, Departure Time: {train[5]}")
                except Error as e:
                    print(f"Error: {e}")
            else:
                print("Train not found.")
        else:
            print("Database connection is not available.")

    def view_passenger(self, ticket_id):
        if self.cursor:
            try:
                self.cursor.execute("SELECT * FROM passengers WHERE ticket_id = %s", (ticket_id,))
                passenger = self.cursor.fetchone()
                if passenger:
                    print(f"Passenger ID: {passenger[0]}, Name: {passenger[1]}, Phone: {passenger[2]}, Email: {passenger[3]}, Ticket ID: {passenger[4]}, Train ID: {passenger[5]}, Seat Number: {passenger[6]}, Arrival Time: {passenger[7]}, Departure Time: {passenger[8]}, Scheduled Station: {passenger[9]}, Station Name: {passenger[10]}")
                else:
                    print("Passenger not found.")
            except Error as e:
                print(f"Error: {e}")
        else:
            print("Database connection is not available.")

def main():
    system = ReservationSystem()
    
    while True:
        print("\nTrain Ticket Reservation System")
        print("1. Book Ticket")
        print("2. Cancel Ticket")
        print("3. View Train Info")
        print("4. View Passenger Info")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            train_id = input("Enter Train ID: ")
            name = input("Enter Passenger Name: ")
            phone = input("Enter Passenger Phone: ")
            email = input("Enter Passenger Email: ")
            scheduled_station = input("Enter Scheduled Station: ")
            station_name = input("Enter Station Name: ")
            passenger_details = (name, phone, email, scheduled_station, station_name)
            system.book_ticket(train_id, passenger_details)
        elif choice == '2':
            train_id = input("Enter Train ID: ")
            ticket_id = input("Enter Ticket ID: ")
            system.cancel_ticket(train_id, ticket_id)
        elif choice == '3':
            train_id = input("Enter Train ID: ")
            system.view_train(train_id)
        elif choice == '4':
            ticket_id = input("Enter Ticket ID: ")
            system.view_passenger(ticket_id)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()
