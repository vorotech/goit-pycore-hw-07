"""Module that contains classes for working with address book."""

import re
import datetime

from collections import UserDict

class Field:
    """
    Represents a base field object.
    """
    def __init__(self, value: any) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Field):
            return False

        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

class Name(Field):
    """
    Represents a name field.
    """
    def __init__(self, value: str) -> None:
        super().__init__(value)


class Phone(Field):
    """
    Represents a phone number field.

    Args:
        value (str): The phone number value.

    Attributes:
        value (str): The normalized phone number value.

    Raises:
        ValueError: If the phone number format is not valid.
    """
    pattern = r"[+\d]"
    country_code = "38"

    def __init__(self, value: str) -> None:
        phone = "".join(re.findall(self.pattern, value))

        if not phone.startswith("+"):
            phone = re.sub(fr"^({self.country_code})?", f"+{self.country_code}", phone)

        if len(phone) != 13:
            raise ValueError("Invalid phone number. Use (+38) XXX-XXX-XX-XX format.")

        super().__init__(phone)

class Birthday(Field):
    """
     Represents a birthday field.

     Raises:
        ValueError: If the bitrhday format is not valid.
    """
    def __init__(self, value: str) -> None:
        bday = None
        try:
            bday = datetime.datetime.strptime(value, "%d.%m.%Y")
        except ValueError as e:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from e
        if bday > datetime.datetime.now():
            raise ValueError("Birthday can't be in the future.")
        if bday.year < 1900:
            raise ValueError("Birthday can't be earlier than 1900.")
        super().__init__(bday)

class Record:
    """
    Represents a contact record with a name and a list of phone numbers.

    Args:
        name (str): The name of the contact.

    Attributes:
        name (Name): The name of the contact.
        phones (list): A list of phone numbers associated with the contact.
        birthday (Birthday): Optional birthday of the contact.
    """

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        """
        Adds a phone number to the contact's list of phone numbers.

        Args:
            phone (Phone): The phone number to add.

        Raises:
            ContactError: If the phone number already exists in the contact's list of phone numbers.
        """
        if self.find_phone(phone):
            raise ContactError("Phone number already exists.")

        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str):
        """
        Removes a phone number from the contact's list of phone numbers.
        Won't raise error if phone number not exist.

        Args:
            phone (str): The phone number to remove.
        """
        existing_phone = self.find_phone(phone)
        if existing_phone:
            self.phones.remove(existing_phone)

    def edit_phone(self, phone: str, new_phone: str):
        """
        Edits a phone number in the contact's list of phone numbers.

        Args:
            phone (str): The phone number to edit.
            new_phone (str): The new phone number.

        Raises:
            ContactError: If the phone number to edit does not exist in the contact's phones list,
                        or if the new phone number already exists in the contact's phones list.
        """
        existing_phone = self.find_phone(phone)
        if not existing_phone:
            raise ContactError("No such phone number.")

        if self.find_phone(new_phone):
            raise ContactError("New phone number already exists.")

        self.phones[self.phones.index(existing_phone)] = Phone(new_phone)

    def find_phone(self, phone: str) -> Phone | None:
        """
        Finds a phone number in the contact's list of phone numbers.

        Args:
            phone (str): The phone number to check.

        Returns:
            Phone: The phone number if found, None otherwise.
        """
        target_phone = Phone(phone)
        return next((p for p in self.phones if p == target_phone), None)

    def add_birthday(self, birthday: str):
        """
        Adds or overrides a birthday of the contact.
        """
        self.birthday = Birthday(birthday)

    def __str__(self):
        chunks = []
        chunks.append(f"Contact name: {self.name}")
        chunks.append(f"phones: {'; '.join(p.value for p in self.phones)}")
        if self.birthday:
            chunks.append(f"birthday: {self.birthday.value.strftime('%d.%m.%Y')}")
        return ", ".join(chunks)

class AddressBook(UserDict):
    """
    A class representing an address book.

    This class extends the UserDict class to provide functionality for managing contacts in an address book.

    Attributes:
        data (dict): A dictionary to store the contacts in the address book.

    Methods:
        add_record(record: Record): Adds a record to the address book.
        find(name: Name) -> Record: Finds a record in the address book by name.
        delete(name: Name): Deletes a record from the address book by name.
    """

    def add_record(self, record: Record) -> None:
        """
        Adds a record to the data dictionary.

        Args:
            record (Record): The record to be added.

        Raises:
            ContactError: If the contact already exists in the data dictionary.
        """
        if record.name in self.data:
            raise ContactError("Contact already exists.")

        self.data[record.name] = record

    def find(self, name: str, raise_error: bool = True) -> Record | None:
        """
        Find a contact by name.

        Args:
            name (str): The name of the contact to find.
            raise_error (bool): Whether to raise an error if the contact is not found.

        Returns:
            Record: The contact record associated with the given name.
            None if not found if raise_error is False.

        Raises:
            ContactError: If no contact with the given name is found. Only if raise_error is True.
        """
        name = Name(name)

        if name not in self.data:
            if raise_error:
                raise ContactError("No such contact.")
            return None

        return self.data[name]

    def delete(self, name: str):
        """
        Deletes the specified name from the data dictionary.
        Won't raise error if phone number not exist.

        Args:
            name (str): The name to be deleted.
        """
        name = Name(name)

        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        """
        Calculates upcoming birthdays of contacts who has their birthday specified
        for next 7 days including today.
        """
        today = datetime.date.today()
        upcoming_birthdays = []

        for user in self.data.values():
            if user.birthday is not None:
                # user.birthday.value is already a datetime.date object
                birthday = user.birthday.value
                birthday_this_year = datetime.date(today.year, birthday.month, birthday.day)
                # 7 days including today is 6 days from today
                if today <= birthday_this_year <= (today + datetime.timedelta(days=6)):
                    congratulation_date = birthday_this_year
                    if birthday_this_year.weekday() in (5, 6):
                        congratulation_date = birthday_this_year + \
                            datetime.timedelta(days = 7 - birthday_this_year.weekday())

                    upcoming_birthdays.append(
                        {
                            'name': user.name.value,
                            'congratulation_date': congratulation_date.strftime("%d.%m.%Y"),
                        }
                    )

        return upcoming_birthdays


class ContactError(Exception):
    """Custom exception for contact errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
