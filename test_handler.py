"""Module for testing the handler functions."""

import datetime
import unittest
import handler

from models import AddressBook, Record, ContactError

class TestAddressBook(unittest.TestCase):
    def setUp(self):
        """
        Set up the test case by creating an instance of AddressBook and adding a contact.
        """
        self.book = AddressBook()
        record = Record("Dmytro")
        record.add_phone("096-123-46-57")
        self.book.add_record(record)

    def test_add_contact(self):
        """
        Test the add_contact function by adding a contact and checking if it is in the address book.
        """
        msg = handler.add_contact(["John", "123-456-78-90"], self.book)
        self.assertIsNotNone(self.book.find("John", raise_error=False))
        self.assertEqual(msg, "Contact added.")


    def test_add_contact_phone(self):
        """
        Test the add_contact function by adding a phone to an existing contact and checking if it is set correctly.
        """
        msg = handler.add_contact(["Dmytro", "123-456-78-90"], self.book)
        contact = self.book.find("Dmytro")
        self.assertEqual(contact.phones[1].value, "+381234567890")
        self.assertEqual(msg, "Contact updated.")

    def test_add_contact_phone_existing_error(self):
        """
        Test the add_contact function by adding a phone to an existing contact and checking if an error is raised.
        """
        msg = handler.add_contact(["Dmytro", "096-123-46-57"], self.book)
        self.assertIn("Phone number already exists.", msg)

    def test_change_contact(self):
        """
        Test the change_contact function by changing a phone number and checking if it is updated correctly.
        """
        msg = handler.change_contact(["Dmytro", "096-123-46-57", "123-456-78-90"], self.book)
        contact = self.book.find("Dmytro")
        self.assertEqual(contact.phones[0].value, "+381234567890")
        self.assertEqual(msg, "Contact updated.")

    def test_delete_contact(self):
        """
        Test the delete_contact function by deleting a contact and checking if it is no longer in the address book.
        """
        handler.delete_contact(["Dmytro"], self.book)
        self.assertIsNone(self.book.find("Dmytro", raise_error=False))

    def test_get_contact(self):
        """
        Test the get_contact function by retrieving a contact and checking if the name matches.
        """
        contact = handler.get_contact(["Dmytro"], self.book)
        self.assertEqual(contact.name.value, "Dmytro")

    def test_get_all_contacts(self):
        """
        Test the get_all_contacts function by retrieving all contacts and checking if the count is correct.
        """
        contacts = handler.get_all_contacts(None, self.book)
        self.assertEqual(len(contacts), 1)

    def test_add_birthday(self):
        """
        Test the add_birthday function by adding a birthday to a contact and checking if it is set correctly.
        """
        handler.add_birthday(["Dmytro", "01.04.1990"], self.book)
        contact = handler.get_contact(["Dmytro"], self.book)
        self.assertEqual(contact.birthday.value, datetime.datetime(1990, 4, 1))

    def test_show_birthday(self):
        """
        Test the show_birthday function by adding a birthday to a contact and checking if it is displayed correctly.
        """
        handler.add_birthday(["Dmytro", "01.04.1990"], self.book)
        birthday = handler.show_birthday(["Dmytro"], self.book)
        self.assertEqual(birthday, "01.04.1990")

    def test_upcoming_birthdays(self):
        """
        Test the birthdays function by adding a birthday to a contact and checking if it is included in the upcoming birthdays list.
        """
        bday = datetime.datetime.today() + datetime.timedelta(days=4)
        handler.add_birthday(["Dmytro", f"{bday.day:02}.{bday.month:02}.1990"], self.book)
        msg = handler.birthdays(None, self.book)
        self.assertIn("Dmytro", msg)


if __name__ == "__main__":
    unittest.main()