#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 18:26:10 2025

@author: sachinkalahasti
"""
import sqlite3
import streamlit as stl
import pandas as pd


# Function to connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('library2.db')
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.executescript('''
                   CREATE TABLE IF NOT EXISTS books(
                       book_id INTEGER PRIMARY KEY,
                       title TEXT NOT NULL,
                       author TEXT NOT NULL,
                       year INTEGER NOT NULL,
                       genre TEXT NOT NULL,
                       quantity INTEGER NOT NULL,
                       available INTEGER NOT NULL,
                       customer_ids TEXT
                       );
                   
                   CREATE TABLE IF NOT EXISTS customer(
                       customer_id INTEGER PRIMARY KEY,
                       first_name TEXT NOT NULL,
                       last_name TEXT NOT NULL,
                       email TEXT NOT NULL);
                   ''')
    conn.commit()
    conn.close()
             
def insert_book(title, author, year, genre, quantity, available):
    conn = get_db_connection()
    cursor = conn.cursor()
    customer_ids = "[]"
    
    cursor.execute('''
                   INSERT INTO books (title, author, year, genre, quantity, available, customer_ids)
                   VALUES (?, ?, ?, ?, ?, ?, ?);
                   ''', (title, author, year, genre, quantity, available, customer_ids))
    conn.commit()
    conn.close()
    
def view_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
                   SELECT * FROM books;
                   ''')
    books = cursor.fetchall()
    conn.commit()
    conn.close()
    return books

def view_available_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
                   SELECT * FROM books WHERE available > 0;
                   ''')
    books = cursor.fetchall()
    conn.commit()
    conn.close()
    return books
        
def search_books(author, genre):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if (author and genre):
        cursor.execute('''
                       SELECT * FROM books 
                       WHERE author = ? AND genre = ?;
                       ''', (author, genre))
    elif (author or genre):
        
        cursor.execute('''
                   SELECT * FROM books 
                   WHERE author = ? OR genre = ?;
                   ''', (author, genre))
    books = cursor.fetchall()
    conn.close()
    return books

def checkout_book(book_id, customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Deduct availability if the book is available
        cursor.execute('''
            UPDATE books
            SET available = available - 1
            WHERE available > 0 AND book_id = ?;
        ''', (book_id,))
        
        # Update the customer_ids JSON column
        cursor.execute('''
            UPDATE books
            SET customer_ids = json_insert(customer_ids, '$[#]', ?)
            WHERE book_id = ?;
        ''', (customer_id, book_id))

        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

    finally:
        conn.close()
        
def return_book(book_id, customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE books
            SET available = available + 1
            WHERE book_id = ?;
        ''', (book_id,))

        cursor.execute('''
            UPDATE books
            SET customer_ids = json_remove(customer_ids, 
                (SELECT json_each.key 
                 FROM json_each(customer_ids) 
                 WHERE json_each.value = ?))
            WHERE book_id = ?;
        ''', (customer_id, book_id))

        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

        
def update_books(title, author, year, genre, book_id, quantity):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
                   UPDATE books
                   SET title = ?, author = ?, year = ?, genre = ?, quantity = ?
                   WHERE book_id = ?;
                   ''', (title, author, year, genre, quantity, book_id))
    conn.commit()
    conn.close()
    
def delete_books(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
     
    cursor.execute('''
                   DELETE FROM books WHERE book_id = ?;
                   ''', (book_id))
    conn.commit()
    conn.close()    
    
def insert_customer(first_name, last_name, email):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
                   INSERT INTO customer (first_name, last_name, email)
                   VALUES (?, ?, ?);
                   ''', (first_name, last_name, email))
    conn.commit()
    conn.close()
    
def view_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
                   SELECT * FROM customer;
                   ''')
    customers = cursor.fetchall()
    conn.commit()
    conn.close()
    return customers

def update_customer(customer_id, book_id, first_name, last_name, email):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
                   UPDATE customer
                   SET book_id = ?, first_name = ?, last_name = ?, email = ?
                   WHERE customer_id = ?;
                   ''', (book_id, first_name, last_name, email, customer_id))
    conn.commit()
    conn.close()
    
def remove_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
     
    cursor.execute('''
                   DELETE FROM customer WHERE customer_id = ?;
                   ''', (customer_id))
    conn.commit()
    conn.close()


def app():
    create_table()
    stl.title("Library Management")
    menu = ["Add Book", "View Books", "Search Books", "View Available Books", "Check Out Book", "Return Book", "Update Book", "Delete Book", "Manage Customers"]
    choice = stl.sidebar.selectbox("Menu", menu)
    
    if choice == "Add Book":
        stl.header("Add a New Book")
        book_title = stl.text_input('Title')
        book_author = stl.text_input('Author')
        book_year = stl.number_input('Year', min_value = 1000, max_value = 2025)
        book_genre = stl.text_input('Genre')
        no_of_copies = stl.number_input('Number of Copies', min_value = 1, max_value = 10)
        available = no_of_copies
        if stl.button('Add'):
            if book_title and book_author and book_year and book_genre and no_of_copies and available:
                insert_book(book_title, book_author, book_year, book_genre, no_of_copies, available)
                stl.info("Book Has Been Added")
            else:
                stl.error("Please Fill All Fields")
                
    elif choice == "View Books":
        stl.header("View All Books")
        books = view_books()
        if len(books) == 0:
            stl.info("No Books Entered")
        else:
            columns = ['ID', 'Title', 'Author', 'Year', 'Genre', "# of Copies", "# of Copies Available", "Who Has Copies"]

            books = pd.DataFrame(books, columns=columns)
            
            stl.write(books)
            
    elif choice == "Search Books":
        stl.header("Search Books by Author/Genre")
        author_search = stl.text_input("Author")
        genre_search = stl.text_input("Genre")
    
        
        if stl.button("Search"):
            author = author_search.strip()
            genre = genre_search.strip()
            if author or genre: 
                books = search_books(author, genre)
                if books:
                    stl.write(f"Books found for: Author: {author} Genre: {genre}")
                    for book in books:
                        stl.write(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Genre: {book[4]}")
                else:
                    stl.warning(f"No books found for Author: {author} Genre:{ genre}.")
            else:
                stl.warning("Please enter author or genre to search.")
            
            
    elif choice == "View Available Books":
        stl.header("View Available Books")
        books = view_available_books()
        if len(books) == 0:
            stl.info("No Books Available")
        else:
            columns = ['ID', 'Title', 'Author', 'Year', 'Genre', "# of Copies", "# of Copies Available", "Who Has Copies"]

            books = pd.DataFrame(books, columns=columns)
            
            stl.write(books)
            
    elif choice == "Check Out Book":
        stl.header("Check Out Book")
        customer_id = stl.text_input('Customer ID')
        available_books = view_available_books()
        if available_books:
            # Create a dictionary to map IDs to formatted labels
            id_to_label = {row[0]: f"ID: {row[0]}, Col1: {row[1]}, Col2: {row[2]}" for row in available_books}
            # Create a form to handle row selection
            with stl.form("row_selection_form"):
                # Use a radio button to select an ID
                selected_id = stl.radio(
                    "Select a row",
                    options=list(id_to_label.keys()),
                    index=0,
                    format_func=id_to_label.get,  # Directly pass the mapping function
                    )
                
                # Submit button
                submitted = stl.form_submit_button("Submit")

                # Process the form
                if submitted:
                    if selected_id:
                        stl.write(f"You selected row ID: {selected_id}")
                        selected_row = next(row for row in available_books if row[0] == selected_id)

                        # Extract individual elements
                        book_id = selected_row[0]
                        
                        # Call the update function
                        checkout_book(book_id, customer_id)
                        stl.success("Database updated successfully!")
                    else:
                        stl.warning("No data found in the database.")
                        
    elif choice == "Return Book":
        stl.header("Return a Book")
        customer_id = stl.text_input('Customer ID')
        books = view_books()
        
        if books:
            # Create a dictionary to map IDs to formatted labels
            id_to_label = {row[0]: f"ID: {row[0]}, Title: {row[1]}, Author: {row[2]}" for row in books}
            
            # Create a form to handle row selection
            with stl.form("return_book_form"):
                # Use a radio button to select a book ID
                selected_id = stl.radio(
                    "Select a book to return",
                    options = list(id_to_label.keys()),
                    index = 0,
                    format_func = id_to_label.get,  # Directly pass the mapping function
                )
                
                # Submit button
                submitted = stl.form_submit_button("Return Book")
                
                # Process the form
                if submitted:
                    if selected_id:
                        stl.write(f"You selected to return book ID: {selected_id}")
                        
                        # Call the return function
                        return_book(selected_id, customer_id)
                        stl.success("Book returned successfully!")
                    else:
                        stl.warning("Please select a book to return.")
            
    elif choice == "Update Book":
        stl.header("Update Book Details")
        book_id = stl.text_input('Book ID')
        book_title = stl.text_input('Title')
        book_author = stl.text_input('Author')
        book_year = stl.number_input('Year', min_value = 1000, max_value = 2025)
        book_genre = stl.text_input('Genre')
        if stl.button('Update'):
            if book_id:
                update_books(book_id, book_title, book_author, book_year, book_genre)
                stl.info("Book Has Been Update")
            else:
                stl.error("Please Fill All Fields")
    
    elif choice == "Delete Book":
        stl.header("Delete a Book")
        book_id = stl.text_input('Book ID')
        if stl.button('Delete'):
            if book_id:
                delete_books(book_id)
                stl.info("Book Has Been Deleted")
            else:
                stl.error("Please Fill All Fields")
    
    elif choice == "Manage Customers":
        customer_menu = ["Add Customer", "View Customers", "Update Customer", "Remove Customer"]
        customer_choice = stl.sidebar.selectbox("Customer Menu", customer_menu)
        
        if customer_choice == "Add Customer":   
            stl.header("Add a New Customer")
            first_name = stl.text_input('First Name')
            last_name = stl.text_input('Last Name')
            email = stl.text_input('Email')
            if stl.button('Add Customer'):
                if first_name and last_name and email:
                    insert_customer(first_name, last_name, email)
                    stl.info("Customer Has Been Added")
                else:
                    stl.error("Please Fill All Fields")
    
        elif customer_choice == "View Customers":
            stl.header("View All Customers")
            customers = view_customers()
            if len(customers) == 0:
                stl.info("No Information on Any Customers")
            else:
                columns = ['ID', 'First Name', 'Last Name', 'Email']

                customers = pd.DataFrame(customers, columns=columns)
                
                stl.write(customers)
            
        elif customer_choice == "Update Customer":
            stl.header("Update Customer Details")
            customer_id = stl.text_input('Customer_ID')
            first_name = stl.text_input('First Name')
            last_name = stl.text_input('Last Name')
            email = stl.text_input('Email')
            if stl.button('Update Customer'):
                if customer_id and first_name and last_name:
                    update_books(first_name, last_name, email)
                    stl.info("Customer Information Has Been Update")
                else:
                    stl.error("Please Fill All Fields")
    
        elif customer_choice == "Remove Customer":
            stl.header("Remove a Customer")
            customer_id = stl.text_input('Customer ID')
            if stl.button('Remove Customer'):
                if customer_id:
                    delete_books(customer_id)
                    stl.info("Customer Has Been Deleted")
                else:
                    stl.error("Please Fill All Fields")
                

if __name__ == '__main__':
    app()