import win32com.client
import time
import numpy as np
from emailClass import Email
from sortEmail import buildBucketsDictionary, sortAlerts, generateBucketSubstrings, sl_buckets
import datetime
import math
import sys
from prettytable import PrettyTable

'''
Global Variables
'''
alerts = np.array([])
last_processed_time = None # Stores the last processed email's time
target_alerts_to_process = 500 # Edit this value based on how many alerts you want to process from the inbox 
                                    # (Needs to be less than the size of the inbox)
size_of_inbox = 0

'''
function name: openOutlook
inputs: None
outputs: None
side effects: None
References: https://www.codeforests.com/2020/06/04/python-to-read-email-from-outlook/
'''
def openOutlook():

    # Access the Outlook Application and its MAPI (Messaging Application Programming Interface) namespace
    outlook_app = win32com.client.Dispatch('outlook.application').GetNamespace("MAPI")

    return outlook_app

'''
function name: extractEmailsfromInbox
inputs: app - connection to the Outlook application
        account - name of the email account being examined
        folder - name of the folder that emails are being read from
        subfolder - name of the subfolder that contains the emails to be extracted
outputs: None
side effects: Populates global "emails" NumPy array with Email Objects that contain all of the necessary email data from a particular inbox
References: https://medium.com/@balakrishna0106/automating-outlook-effortless-email-retrieval-using-pythons-win32com-client-796b13746ad9
'''
def extractEmailsfromInbox(app, account, email_address, folder, subfolder):

    global last_processed_time, sl_buckets, bucket_substrings, size_of_inbox
    
    primary_inbox = app.Folders(account.DeliveryStore.DisplayName).Folders[folder]
    
    subfolder_inbox = primary_inbox.Folders[subfolder]

    emails = subfolder_inbox.Items

    print("----------------------------------------------------------------------------------------------------------")
    print("Inbox Details:\n")
    print("Email Address : " + email_address)
    print("Size : " + str(len(emails)) + " Total Emails")
    print("----------------------------------------------------------------------------------------------------------")
    print("Error List:\n")
    
    size_of_inbox = len(emails)

    alertsProcessed = 0

    for em in emails:
        
        # np.append(alerts, Email(em))
        # print(Email(em).subject)
        # print(em)
        sl_buckets = sortAlerts(Email(em), sl_buckets, bucket_substrings)
        alertsProcessed+=1
        print(str(alertsProcessed) + "/" + str(target_alerts_to_process) + " emails processed", end='\r')
        sys.stdout.flush()
        if alertsProcessed == target_alerts_to_process:
            break

'''
function name: updateAlertsCount
inputs: None
outputs: None
side effects: prints the number of emails generated for each type of alert to the terminal
'''
def updateAlertsCount():

    print("----------------------------------------------------------------------------------------------------------")
    print("Logistics System Alert Inbox Snapshot: (Number of Alerts per Category)\n")
    # for key in sl_buckets:
    #     print(f"{key} : {len(sl_buckets[key])}")
    alertCategoryTable = PrettyTable(["#","Alert Categories", "Number of Alerts"])
    rowIndex = 1
    alertCategoryTable.align["Alert Categories"] = "l"
    alertCategoryTable.align["Number of Alerts"] = "c"
    for key, value in sl_buckets.items():
        alertCategoryTable.add_row([str(rowIndex), key, len(value)])
        rowIndex+=1
    print(alertCategoryTable)
    print("\n")
    totalAlertsTable = PrettyTable(["Total Number of Alerts Processed", "Total Size of Inbox", "Percentage of Inbox Processed"])
    totalAlertsTable.add_row([str(target_alerts_to_process), str(size_of_inbox), str(round(target_alerts_to_process/size_of_inbox,5)*100)+"%"])
    print(totalAlertsTable)
    print("\n")
    rowIndex = 1
    unmatchedAlertsTable = PrettyTable(["#", "Unmatched Alerts"])
    unmatchedAlertsTable.align["Unmatched Alerts"] = "l"
    for value in sl_buckets["Unmatched"]:
        unmatchedAlertsTable.add_row([str(rowIndex), value.subject])
        rowIndex+=1
    print(unmatchedAlertsTable)
    print("\n")
    print("Example of Stored Email Alert: (Unmatched Category)\n")
    print(sl_buckets["Unmatched"][0])
    print("----------------------------------------------------------------------------------------------------------")

'''
function name: main
inputs: None
outputs: None
side effects: None
'''
def main():
    global last_processed_time, sl_buckets, bucket_substrings

    # Set this value to be the date and time the alerts were last processed
    # last_processed_time = datetime.datetime(2024, 7, 15, 12, 0, 0)

    outlook_app = openOutlook()

    account_email_address = "LogisticSystemAlert@medline.com"

    # Checks to see if the desired email account exists within the Outlook application
    myAccount = None
    for acc in outlook_app.Accounts:
        if acc.SmtpAddress == account_email_address:
            myAccount = acc
            break
    
    if not myAccount:
        print(f"Account '{account_email_address}' not found.")
        return

    sl_buckets = buildBucketsDictionary()
    bucket_substrings = generateBucketSubstrings(sl_buckets)
    
    while True:
        # Retrieve new emails periodically
        extractEmailsfromInbox(outlook_app, myAccount, account_email_address, "Inbox", "Do Not Delete!!!")
        updateAlertsCount()
        break

        # Update last processed time to current time after processing emails
        #last_processed_time = datetime.datetime.now()

        # Time interval (in seconds) for how often the emails will be extracted
        time.sleep(10)

# Starts the program
if __name__ == "__main__":
    main()