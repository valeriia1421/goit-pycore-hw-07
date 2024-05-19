from collections import UserDict
import datetime
import re


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Невірний формат номеру телефону. Номер повинен містити 10 цифр.")
        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        return re.fullmatch(r"\d{10}", value)

class Birthday(Field):
    def __init__(self, value):
        self.value = self.validate_birthday(value)
    
    @staticmethod
    def validate_birthday(value):
        try:
            birthday = datetime.datetime.strptime(value, "%d.%m.%Y").date()
            return birthday
        except ValueError:
            raise ValueError("Birthday must be in DD.MM.YYYY format")

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.birthday = Birthday(birthday) if birthday else None
        self.phones = []
        
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return True
        return False

    def find_phone(self, phone):
        for phone_record in self.phones:
            if phone_record.value == phone:
                return phone
        return False

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        birthday_str = f", Birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"



class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find_record(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def get_upcoming_birthdays(self):
        today = datetime.date.today()
        one_week = today + datetime.timedelta(days=7)
        upcoming_birthdays = []
        for name, record in self.data.items():
            if record.birthday:
                this_year_birthday = record.birthday.value.replace(year=today.year)
                if this_year_birthday < today:
                    this_year_birthday = this_year_birthday.replace(year=today.year + 1)
                if today <= this_year_birthday <= today + datetime.timedelta(days=7):
                    upcoming_birthdays.append((name, this_year_birthday.strftime('%d.%m.%Y')))
        return upcoming_birthdays

###################################################################################################

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error: {e}"
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Error: Please provide both name and phone number."
    name, phone, *_ = args
    record = book.find_record(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def show_phone(args, book):
    if len(args) < 1:
        return "Error: Please specify the contact name."
    name = args[0]
    record = book.data.get(name)
    if not record:
        return "Contact not found."
    if record.phones:
        return f"{name}'s phone numbers: " + ', '.join([phone.value for phone in record.phones])
    else:
        return f"No phone numbers found for {name}."

@input_error
def show_all_contacts(args, book):
    if not book.data:
        return "The address book is empty."
    return "\n".join(f"{name}: {', '.join(phone.value for phone in record.phones)}" for name, record in book.data.items())

@input_error
def change_contact(args, book):
    if len(args) < 3:
        return "Error: Please provide contact name, old phone number, and new phone number."
    name, old_phone, new_phone = args
    record = book.data.get(name)
    if not record:
        return "Contact not found."
    if not any(phone.value == old_phone for phone in record.phones):
        return f"No phone number {old_phone} found for {name}."
    for phone in record.phones:
        if phone.value == old_phone:
            phone.value = new_phone
            return f"Phone number updated for {name} from {old_phone} to {new_phone}."
    return "Unexpected error during phone number update."


@input_error
def add_birthday(args, book):
    if len(args) < 2:
        return "Error: Please provide both name and birthday."
    try:
        name, birthday_str = args
        record = book.data.get(name)
        if record:
            record.add_birthday(birthday_str)
            return f"Birthday {birthday_str} has been added to {name}."
        else:
            return "Contact not found."
    except ValueError:
        return "Invalid input. Please specify name and birthday in format DD.MM.YYYY."

@input_error
def show_birthday(args, book):
    if len(args) < 1:
        return "Error: Please specify the contact name."
    try:
        name, = args
        record = book.data.get(name)
        if record and record.birthday:
            return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."
        return "Birthday not found."
    except ValueError:
        return "Invalid input. Please specify the name."

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return '\n'.join(f"{name}'s birthday on {date}" for name, date in upcoming_birthdays)
    else:
        return "No upcoming birthdays."

def parse_input(user_input):
    parts = user_input.strip().split(maxsplit=1)
    command = parts[0]
    args = parts[1].split() if len(parts) > 1 else []    
    return command, args

def main():
    book = AddressBook()
    print("Welcome to your address book!")

    while True:
        user_input = input("Enter command (add, change, phone, all, add-birthday, show-birthday, birthdays, hello, exit or close): ")
        if len(user_input) > 0 and user_input != '':
            
            command, args = parse_input(user_input)
            try:
                if command in ["close", "exit"]:
                    print("Good bye!")
                    break

                elif command == "hello":
                    print("How can I help you?")

                elif command == "add":                    
                    message = add_contact(args, book)
                    print(message)

                elif command == "change":
                    message = change_contact(args, book)
                    print(message)

                elif command == "phone":
                    message = show_phone(args, book)
                    print(message)

                elif command == "all":
                    message = show_all_contacts(args, book)
                    print(message)

                elif command == "add-birthday":
                    message = add_birthday(args, book)
                    print(message)

                elif command == "show-birthday":
                    message = show_birthday(args, book)
                    print(message)

                elif command == "birthdays":
                    message = birthdays(args, book)
                    print(message)

            except ValueError as e:
                print(e)
                continue
        else:
            print("Enter the command from the list")


if __name__ == '__main__':
    main()	