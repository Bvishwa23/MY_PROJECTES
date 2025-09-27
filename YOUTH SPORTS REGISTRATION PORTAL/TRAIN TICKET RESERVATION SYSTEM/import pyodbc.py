import mysql.connector

# Database connection settings
server = 'localhost'
database = 'train'
username = 'root'
password = 'arjun@5425123'

# Create a connection to the database
cnx = mysql.connector.connect(
    user=root,
    password=arjun@5425123,
    host=localhost,
    database=Train
)

# Create a cursor object
cursor = cnx.cursor()

# Passenger class
class Passenger:
    def __init__(self, PAX_id, name, age, sex):
        self.PAX_id = PAX_id
        self.name = name
        self.age = age
        self.sex = sex

# Train class
class Train:
    def __init__(self, train_id, train_name, seats_available):
        self.train_id = train_id
        self.train_name = train_name
        self.seats_available = seats_available

# Ticket class
class Ticket:
    def __init__(self, ticket_id, passenger, train, seat_number):
        self.ticket_id = ticket_id
        self.passenger = passenger
        self.train = train
        self.seat_number = seat_number

# Login function
def login(username, password):
    # implement login logic here
    pass

# Search Train function
def search_train(train_name):
    # implement search train logic here
    pass

# Modify form function
def modify_form(passenger):
    # implement modify form logic here
    pass

# Pay charges function
def pay_charges(ticket):
    # implement pay charges logic here
    pass

# Book tickets function
def book_tickets(passenger, train, seat_number):
    query = "INSERT INTO Tickets (PAX_id, train_id, seat_number) VALUES (%s, %s, %s)"
    cursor.execute(query, (passenger.PAX_id, train.train_id, seat_number))
    cnx.commit()

# Cancel tickets function
def cancel_tickets(ticket):
    query = "DELETE FROM Tickets WHERE ticket_id = %s"
    cursor.execute(query, (ticket.ticket_id,))
    cnx.commit()

# Main function
def main():
    # create a list to store passengers
    passengers = []

    # create a list to store trains
    trains = []

    # create a list to store tickets
    tickets = []

    while True:
        print("1. Login")
        print("2. Search Train")
        print("3. Modify Form")
        print("4. Pay Charges")
        print("5. Book Tickets")
        print("6. Cancel Tickets")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            login(username, password)
        elif choice == "2":
            train_name = input("Enter train name: ")
            search_train(train_name)
        elif choice == "3":
            PAX_id = input("Enter PAX_id: ")
            name = input("Enter name: ")
            age = int(input("Enter age: "))
            sex = input("Enter sex: ")
            passenger = Passenger(PAX_id, name, age, sex)
            modify_form(passenger)
        elif choice == "4":
            ticket_id = input("Enter ticket id: ")
            ticket = next((t for t in tickets if t.ticket_id == ticket_id), None)
            if ticket:
                pay_charges(ticket)
            else:
                print("Ticket not found")
        elif choice == "5":
            PAX_id = input("Enter PAX_id: ")
            passenger = next((p for p in passengers if p.PAX_id == PAX_id), None)
            if passenger:
                train_id = input("Enter train id: ")
                train = next((t for t in trains if t.train_id == train_id), None)
                if train:
                    seat_number = input("Enter seat number: ")
                    book_tickets(passenger, train, seat_number)
                else:
                    print("Train not found")
            else:
                print("Passenger not found")
        elif choice == "6":
            ticket_id = input("Enter ticket id: ")
            ticket = next((t for t in tickets if t.ticket_id == ticket_id), None)
            if ticket:
                cancel_tickets(ticket)
            else:
                print("Ticket not found")
        elif choice == "7":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()