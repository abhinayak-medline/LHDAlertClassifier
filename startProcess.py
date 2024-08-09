import win32com.client
import time
import numpy as np
from emailClass import Email
from sortEmail import buildBucketsDictionary, sortAlerts, generateBucketSubstrings, sl_buckets
import threading
import pythoncom
from prettytable import PrettyTable
import sqlite3
import sys
import json

'''
Global Variables
'''
alerts = np.array([])
last_processed_time = None
target_alerts_to_process = 1000  # Edit this value based on how many alerts you want to process from the inbox
size_of_inbox = 0

'''
Function to open Outlook application and return the namespace
'''
def openOutlook():
    outlook_app = win32com.client.Dispatch('Outlook.Application')
    return outlook_app

'''
Function to extract emails from a specified subfolder in the Outlook inbox
'''
def extractEmailsfromInbox(outlook_app, account, email_address, folder_name, subfolder_name, batch_size=1000):

    global last_processed_time, sl_buckets, bucket_substrings, size_of_inbox

    try:
        primary_inbox = outlook_app.Session.Folders(account.DeliveryStore.DisplayName).Folders[folder_name]
        subfolder_inbox = primary_inbox.Folders[subfolder_name]

        print("----------------------------------------------------------------------------------------------------------")
        print(f"Inbox Details for {subfolder_name}:\n")
        print(f"Email Address : {email_address}")
        print(f"Size : {len(subfolder_inbox.Items)} Total Emails")
        print("----------------------------------------------------------------------------------------------------------")
        #print("Error List:\n")

        size_of_inbox = len(subfolder_inbox.Items)
        alerts_processed = 0

        emails = subfolder_inbox.Items

        # Sort messages by received time from oldest to newest
        emails.Sort("[ReceivedTime]", True)

        start_time = time.time()  # Start time for processing

        # Process emails in batches
        for idx in range(min(target_alerts_to_process, len(subfolder_inbox.Items))):
            em = emails[idx]
            sl_buckets = sortAlerts(Email(em), sl_buckets, bucket_substrings)
            alerts_processed += 1
            print(f"{alerts_processed}/{target_alerts_to_process} emails processed", end='\r')
            sys.stdout.flush()

            if alerts_processed == target_alerts_to_process:
                break

            # Introduce a small delay between batches
            # if alerts_processed % batch_size == 0:
            #     time.sleep(1)  # Adjust as needed based on performance

        end_time = time.time()  # End time for processing
        print(f"\nTime taken to process emails: {end_time - start_time:.2f} seconds")

    except Exception as e:
        print(f"Error occurred while accessing folder: {e}")

    finally:
        # Clean up resources
        subfolder_inbox = None
        primary_inbox = None

'''
Function to update alerts count and print statistics
'''
def updateAlertsCount():
    global size_of_inbox, target_alerts_to_process

    print("----------------------------------------------------------------------------------------------------------")
    print("Logistics System Alert Inbox Snapshot: (Number of Alerts per Category)\n")
    alertCategoryTable = PrettyTable(["#", "Alert Categories", "Number of Alerts"])
    rowIndex = 1
    for key, value in sl_buckets.items():
        alertCategoryTable.add_row([str(rowIndex), key, len(value)])
        rowIndex += 1
    print(alertCategoryTable)
    print("\n")
    totalAlertsTable = PrettyTable(["Total Number of Alerts Processed", "Total Size of Inbox", "Percentage of Inbox Processed"])
    totalAlertsTable.add_row([str(target_alerts_to_process), str(size_of_inbox), str(round(target_alerts_to_process / size_of_inbox, 5) * 100) + "%"])
    print(totalAlertsTable)
    print("\n")
    rowIndex = 1
    unmatched_counter = 0
    unmatchedAlertsTable = PrettyTable(["#", "Unmatched Alerts"])
    unmatchedAlertsTable.align["Unmatched Alerts"] = "l"
    for value in sl_buckets["Unmatched"]:
        unmatchedAlertsTable.add_row([str(rowIndex), value.subject])
        rowIndex += 1
        unmatched_counter+=1
        if unmatched_counter == 50:
            break
    print(unmatchedAlertsTable)
    print("\n")
    print("Example of Stored Email Alert: (Unmatched Category)\n")
    print(sl_buckets["Unmatched"][0])
    print("----------------------------------------------------------------------------------------------------------")

def viewDatabase():
    try:
        conn = sqlite3.connect('alerts.db')
        cursor = conn.cursor()

        # Print table schema
        cursor.execute("PRAGMA table_info(alerts)")
        schema = cursor.fetchall()
        print("Table Schema:")
        for column in schema:
            print(column)

        # Select all rows from alerts table
        cursor.execute("SELECT * FROM alerts")
        rows = cursor.fetchall()

        # Print fetched rows
        print("\nData in alerts table:")
        for row in rows:
            print(row)

        conn.close()

    except Exception as e:
        print(f"Error occurred while viewing database: {e}")

'''
Function to insert alerts into SQLite database
'''
def insertAlertsIntoDatabase():

    global sl_buckets

    try:
        # Establish connection to SQLite database
        conn = sqlite3.connect('data/alerts.db')
        cursor = conn.cursor()

        # cursor.execute('''DELETE FROM alerts''')

        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                urgency TEXT,
                subject TEXT,
                sender_name TEXT,
                sender_email_address TEXT,
                to_recipients TEXT,
                cc_recipients TEXT,
                bcc_recipients TEXT,
                received_time TEXT,
                sent_on TEXT,
                html_body TEXT,
                text_body TEXT,
                attachments TEXT,
                size INTEGER
            )
        ''')

        # Insert each alert from sl_buckets into database
        for category, emails in sl_buckets.items():
            for email in emails:
                subject = getattr(email, 'subject', 'No Subject')
                urgency = getattr(email, 'urgency', 'No Urgency Assigned')
                sender = getattr(email, 'sender_name', 'Unknown Sender')
                sender_ea = getattr(email, 'sender_email', 'Unknown Email')
                to = getattr(email, 'to_recipients', 'No recipients')
                cc = getattr(email, 'cc_recipients', 'No recipients')
                bcc = getattr(email, 'bcc_recipients', 'No recipients')
                received_time = getattr(email, 'received_time', 'Unknown')
                sent_time = getattr(email, 'sent_on', 'Unknown')
                h_body = getattr(email, 'html_body', 'HTMLBody not Found')
                t_body = getattr(email, 'text_body', 'Body not Found')
                attachments = json.dumps(getattr(email, 'attachments', []))  # Convert to JSON string
                size = getattr(email, 'size', 'Size Not Found')

                if isinstance(to, list):
                    to = '; '.join(to)
                if isinstance(cc, list):
                    cc = '; '.join(cc)
                if isinstance(bcc, list):
                    bcc = '; '.join(bcc)

                cursor.execute('''
                    INSERT INTO alerts (category, urgency, subject, sender_name, sender_email_address, to_recipients, cc_recipients, bcc_recipients, received_time, sent_on, html_body, text_body, attachments, size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (category, urgency, subject, sender, sender_ea, to, cc, bcc, received_time, sent_time, h_body, t_body, attachments, size))

    # Commit changes and close connection
        conn.commit()
        conn.close()

        print("Alerts have been successfully inserted into the database.")

    except Exception as e:
        print(f"Error occurred while inserting alerts into database: {e}")

'''
Function to perform email processing in a separate thread
'''
def process_emails_in_background():
    global last_processed_time, sl_buckets, bucket_substrings, size_of_inbox

    try:
        # Initialize COM for the thread
        pythoncom.CoInitialize()

        # Initialize Outlook application in the background thread
        outlook_app = openOutlook()
        account_email_address = "LogisticSystemAlert@medline.com"
        myAccount = next((acc for acc in outlook_app.Session.Accounts if acc.SmtpAddress == account_email_address), None)

        if not myAccount:
            print(f"Account '{account_email_address}' not found.")
            return

        # Initialize other necessary data structures (sl_buckets, bucket_substrings, etc.)
        sl_buckets = buildBucketsDictionary()
        bucket_substrings = generateBucketSubstrings(sl_buckets)

        # Extract emails from Inbox subfolder
        extractEmailsfromInbox(outlook_app, myAccount, account_email_address, "Inbox", "Do Not Delete!!!")

        # Update alerts count and print statistics
        updateAlertsCount()

        # Insert alerts into SQLite database
        insertAlertsIntoDatabase()

    except Exception as e:
        print(f"Error occurred in background thread: {e}")

    finally:
        # Clean up resources
        if outlook_app:
            outlook_app = None
        
        # Uninitialize COM for the thread
        pythoncom.CoUninitialize()

        # Create a flag file to indicate completion
        with open('data/process_complete.txt', 'w') as f:
            f.write('Process completed')

'''
Main function to start the program
'''
def main():
    # Start processing emails in a separate thread
    email_thread = threading.Thread(target=process_emails_in_background)
    email_thread.start()

    # Wait for the email processing thread to complete
    email_thread.join()

    # After the thread completes, view database and print data
    # viewDatabase()

if __name__ == "__main__":
    main()