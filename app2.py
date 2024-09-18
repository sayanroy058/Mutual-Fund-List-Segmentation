import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Database connection details from environment variables
host = os.getenv('DB_HOST')
port = int(os.getenv('DB_PORT'))
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_NAME')

# Function to connect to the database
def get_db_connection():
    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )

# Function to fetch mutual funds from the Mutual_Fund_List table
def fetch_all_mutual_funds():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT Mutual_Fund_Name, URL FROM Mutual_Fund_List')
    mutual_funds = cursor.fetchall()
    cursor.close()
    connection.close()
    return mutual_funds

# Function to fetch mutual funds from the Segmented_Mutual_Fund_List table
def fetch_segmented_mutual_funds():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT ID, Mutual_Fund_Name FROM Segmented_Mutual_Fund_List')
    segmented_funds = cursor.fetchall()
    cursor.close()
    connection.close()
    return segmented_funds

# Function to add mutual funds to the Segmented_Mutual_Fund_List table
def add_to_segmented_list(fund_list):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        insert_query = '''
        INSERT INTO Segmented_Mutual_Fund_List (Mutual_Fund_Name, URL)
        SELECT %s, %s FROM DUAL
        WHERE NOT EXISTS (
            SELECT 1 FROM Segmented_Mutual_Fund_List WHERE Mutual_Fund_Name = %s
        )
        '''
        cursor.executemany(insert_query, [(name, url, name) for name, url in fund_list])
        connection.commit()
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

# Function to delete mutual fund from the Segmented_Mutual_Fund_List table
def delete_from_segmented_list(fund_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        delete_query = 'DELETE FROM Segmented_Mutual_Fund_List WHERE ID = %s'
        cursor.execute(delete_query, (fund_id,))
        connection.commit()
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

# Streamlit app
st.title("Mutual Fund Management App")

# Display all mutual funds from Mutual_Fund_List
mutual_funds = fetch_all_mutual_funds()
selected_funds = st.multiselect("Select Mutual Funds to Add:", mutual_funds, format_func=lambda x: x[0])

# Add button
if st.button("Add to Segmented Mutual Fund List"):
    if selected_funds:
        add_to_segmented_list(selected_funds)
        st.success("Selected mutual funds have been added to the segmented list.")

# Display mutual funds present in the Segmented_Mutual_Fund_List
segmented_funds = fetch_segmented_mutual_funds()
if segmented_funds:
    fund_to_delete = st.selectbox("Select Mutual Fund to Delete:", segmented_funds, format_func=lambda x: x[1])

    # Delete button
    if st.button("Delete from Segmented Mutual Fund List"):
        delete_from_segmented_list(fund_to_delete[0])
        st.success(f"{fund_to_delete[1]} has been deleted from the segmented list.")
