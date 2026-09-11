"""
HOSTEL ROOM BOOKING AND FEES MANAGEMENT SYSTEM
Data Persistence: JSON File (hostel_records.json)
"""

import json
import os


# CONSTANTS & INITIAL DATA STRUCTURES
# Requirement (a): Predefine at least three hostel blocks with fixed rooms and capacities
ROOM_FEE = 1500000.0  # Standard hostel fee per student in UGX

# Predefined Hostel Blocks Data Structure (Nested Dictionaries)
#we could have implemented a list of lists here but for future use, we have to change data or add data to our hostel_blocks
#so we implemented a global students = [] variable below 
hostel_blocks = {
    "Block A": {"101": 2, "102": 2, "103": 4},
    "Block B": {"201": 2, "202": 3, "203": 3},
    "Block C": {"301": 1, "302": 2, "303": 2}
}

# Global List to store student records (List of Dictionaries)
students = [] #by default python wil set this as a global container but with a few restrictions
               #so we implemented it inside the load_data() so as to be able to change its data directly without
               #python creating  new variables each time

DATA_FILE = "hostel_records.json"


# FILE PERSISTENCE FUNCTIONS
# Requirement (e): Save/load records to file & handle missing/damaged files gracefully

def load_data():
    """Requirement (e): Load student records from JSON on program start."""
    global students  #so here is our students variable made global so that it can be changed 
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                students = json.load(file)
            print("Hostel records successfully loaded from database.")
        except (json.JSONDecodeError, OSError):
            print("Warning: Data file corrupted or unreadable. Starting with fresh records.")
            students = [] #this will reload the students data without the program crashing
    else:
        print("No prior data file found. System initialized with fresh records.")


def save_data():
    """Requirement (e): Persist student records to JSON on system exit."""
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(students, file, indent=4)
        print("Data saved successfully to hostel_records.json.")
    except OSError as e:
        print(f"Error saving data to file: {e}")



# SYSTEM CORE & OCCUPANCY FUNCTIONS
# Requirement (a): Data setup and occupancy overview
#this is like a helper function, actually its a helper function that we will use in other functions to get room occupancy
#without creating several loops again and again..
def get_room_occupancy(block, room):
    """Helper: Calculates current student count for a specific room."""
    return sum(1 for s in students if s["block"] == block and s["room"] == room)


def display_occupancy_overview():
    """Requirement (a): Print a brief overview of hostel block/room occupancy."""
    print("\n================ HOSTEL OCCUPANCY OVERVIEW ================")
    print(f"{'Block':<10} | {'Room':<8} | {'Occupancy':<12} | {'Status'}")
    print("-" * 55)

    for block, rooms in hostel_blocks.items():
        for room, capacity in rooms.items():
            current = get_room_occupancy(block, room) #like here we have called it, otherwise we would have created new loops
            status = "FULL" if current >= capacity else f"{capacity - current} Space(s) Left"
            print(f"{block:<10} | Room {room:<3} | {current}/{capacity} occupants  | {status}")
    print("-" * 55)


# STUDENT REGISTRATION & ALLOCATION
# Requirement (b): Student registration, room capacity validation, and allocation
# here in this function, we will allocate students after crucial checks pass.
def allocate_student_room():
    """Requirement (b): Register a student and allocate them to an available room."""
    print("\n--- NEW STUDENT REGISTRATION & ROOM ALLOCATION ---")
    reg_no = input("Enter Registration Number: ").strip().upper()
    if not reg_no:
        print("Error: Registration number cannot be empty.")
        return

    # Check for duplicate registration
    if any(s["reg_no"] == reg_no for s in students):#if there happens to be any student in our dictionary, then we will safeguard 
        print(f"Error: Student with Reg No '{reg_no}' is already registered!")
        return

    name = input("Enter Student Full Name: ").strip() #stripping is just deleting unnecessary spaces that are beyond the input

    display_occupancy_overview()

    # Block Selection
    block = input("Select Block (e.g., Block A, Block B, Block C): ").strip().title()
    if block not in hostel_blocks:
        print(f"Allocation Rejected: '{block}' does not exist.")
        return

    # Room Selection
    room = input(f"Enter Room Number in {block} (e.g., {', '.join(hostel_blocks[block].keys())}): ").strip()
    if room not in hostel_blocks[block]:
        print(f"Allocation Rejected: Room '{room}' does not exist in {block}.")
        return

    # Capacity Check
    current_count = get_room_occupancy(block, room)
    max_capacity = hostel_blocks[block][room]

    if current_count >= max_capacity:
        print(f"\n[ALLOCATION REJECTED]: Room {room} in {block} is completely FULL ({current_count}/{max_capacity}).")
        return

    # Register new student profile
    student_record = {
        "reg_no": reg_no,
        "name": name,
        "block": block,
        "room": room,
        "total_fee": ROOM_FEE,
        "paid_fee": 0.0,
        "balance": ROOM_FEE
    }
    students.append(student_record)
    print(f"\n[SUCCESS]: {name} ({reg_no}) allocated to {block}, Room {room}!")
    print(f"Total Hostel Fee Assigned: UGX {ROOM_FEE:,.2f}")


# FEE PAYMENT RECORDING
# Requirement (c): Record full/partial fee payments and update balance ledger
# one of the critical functions that required alot of logical thinking and research
def record_fee_payment():
    """Requirement (c): Record fee payments and update student outstanding balance."""
    print("\n--- RECORD FEE PAYMENT ---")
    query = input("Enter Student Reg No or Name: ").strip().lower()

    matches = [s for s in students if query in s["reg_no"].lower() or query in s["name"].lower()]

    if not matches:
        print("No student records found matching your query.")
        return

    # if multiple students match, get the index of the same no. in a list form
    #also called deambiguating
    student = matches[0]
    if len(matches) > 1:
        print("\nMultiple students found:")
        for idx, s in enumerate(matches, 1):
            print(f"{idx}. {s['name']} ({s['reg_no']}) - Room: {s['block']} {s['room']}")
        try:
            choice = int(input("Select student index number: "))
            student = matches[choice - 1]
        except (ValueError, IndexError):
            print("Invalid choice selection.")
            return

    print(f"\nStudent Found: {student['name']} ({student['reg_no']})")
    print(f"Room: {student['block']}, Room {student['room']}")
    print(f"Current Paid Amount : UGX {student['paid_fee']:,.2f}")
    print(f"Current Outstanding Balance: UGX {student['balance']:,.2f}")

    if student["balance"] <= 0:
        print("This student has already fully cleared all hostel fees!")
        return

    # Validated Payment Input Loop
    while True:
        try:
            amount = float(input("\nEnter Payment Amount (UGX): "))
            if amount <= 0:
                print("Payment amount must be greater than zero.")
            elif amount > student["balance"]:
                print(f"Warning: Amount exceeds balance. Max required payment is UGX {student['balance']:,.2f}.")
            else:
                break
        except ValueError:
            print("Invalid input! Enter a valid numerical amount.")

    # Update ledger balance
    student["paid_fee"] += amount
    student["balance"] -= amount

    print("\n--- PAYMENT RECEIPT ---")
    print(f"Student Name       : {student['name']}")
    print(f"Amount Paid        : UGX {amount:,.2f}")
    print(f"Updated Total Paid : UGX {student['paid_fee']:,.2f}")
    print(f"Remaining Balance  : UGX {student['balance']:,.2f}")



# SEARCH & REPORTING SYSTEM
# Requirement (d): Search student, generate block occupancy report, generate defaulters report

def search_and_reporting():
    """Requirement (d): Search by student details and generate administrative reports."""
    print("\n================ SEARCH & REPORTING SYSTEM ================")
    print("1. Search Student by Name or Reg Number")
    print("2. Generate Full Block-by-Block Occupancy Report")
    print("3. Generate Fee Defaulters List")
    print("-----------------------------------------------------------")

    choice = input("Select report option (1-3): ").strip()

    # 1. Search Student
    if choice == "1":
        query = input("\nEnter Student Name or Reg Number to Search: ").strip().lower()
        results = [s for s in students if query in s["reg_no"].lower() or query in s["name"].lower()]

        if not results:
            print("No matching student records found.")
        else:
            print(f"\nFound {len(results)} matching record(s):")
            print(f"{'Reg No':<12} | {'Name':<20} | {'Location':<15} | {'Balance (UGX)'}")
            print("-" * 65)
            for s in results:
                location = f"{s['block']} R{s['room']}"
                print(f"{s['reg_no']:<12} | {s['name']:<20} | {location:<15} | {s['balance']:,.2f}")

    # 2. Block-by-Block Occupancy Report
    elif choice == "2":
        print("\n--- FULL HOSTEL BLOCK OCCUPANCY REPORT ---")
        for block, rooms in hostel_blocks.items():
            print(f"\n>>> {block.upper()} <<<")
            for room, cap in rooms.items():
                room_students = [s for s in students if s["block"] == block and s["room"] == room]
                print(f"  Room {room} (Capacity: {len(room_students)}/{cap}):")
                if not room_students:
                    print("    [ Empty Room ]")
                else:
                    for s in room_students:
                        print(f"    - {s['name']} ({s['reg_no']}) | Paid: UGX {s['paid_fee']:,.2f}")

    # 3. Fee Defaulters List Report
    elif choice == "3":
        print("\n--- FEE DEFAULTERS REPORT ---")
        try:
            threshold = float(input("Enter minimum outstanding balance threshold (e.g., 0 for any balance): "))
        except ValueError:
            threshold = 0.0

        defaulters = [s for s in students if s["balance"] > threshold]

        if not defaulters:
            print(f"Great news! No students found with an outstanding balance above UGX {threshold:,.2f}.")
        else:
            print(f"\nStudents owing MORE than UGX {threshold:,.2f}:")
            print(f"{'Reg No':<12} | {'Name':<20} | {'Room':<12} | {'Paid (UGX)':<12} | {'Balance Due (UGX)'}")
            print("-" * 75)
            for s in defaulters:
                loc = f"{s['block']} {s['room']}"
                print(f"{s['reg_no']:<12} | {s['name']:<20} | {loc:<12} | {s['paid_fee']:<12,.2f} | {s['balance']:,.2f}")

    else:
        print("Invalid reporting selection.")



# MAIN DRIVER LOOP
# Requirement (f): Well-organized looping menu system with input validation throughout
# responsible for all navigation of the functions easily 
def main():
    """Requirement (f): Interactive user interface loop for system operation."""
    load_data()
    display_occupancy_overview()

    while True:
        print("\n==============================================")
        print("    HOSTEL ROOM BOOKING & FEES MANAGEMENT     ")
        print("==============================================")
        print("1. View Hostel Occupancy Overview")
        print("2. Register Student & Allocate Room")
        print("3. Record Fee Payment")
        print("4. Search & Generate Reports (Defaulters/Occupancy)")
        print("5. Save and Exit System")
        print("==============================================")

        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            display_occupancy_overview()
        elif choice == "2":
            allocate_student_room()
        elif choice == "3":
            record_fee_payment()
        elif choice == "4":
            search_and_reporting()
        elif choice == "5":
            save_data()
            print("System closed. Have a nice day Warden!")
            break
        else:
            print("Invalid selection! Please enter a choice between 1 and 5.")


if __name__ == "__main__":
    main()