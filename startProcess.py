import win32com.client
import time
import numpy as np
from emailClass import Email
from sortEmail import buildBucketsDictionary, sortAlerts, sl_buckets_dict
from datetime import datetime, timedelta

'''
Global Variables
'''
emails = np.array([])
last_processed_time = None # Stores the last processed email's time

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
def extractEmailsfromInbox(app, account, folder, subfolder):

    global last_processed_time
    
    primary_inbox = app.Folders(account.DeliveryStore.DisplayName).Folders[folder]
    
    subfolder_inbox = primary_inbox.Folders[subfolder]

    emails = subfolder_inbox.Items

    # Filter emails received after the last processed email's time
    if last_processed_time:
        emails = emails.Restrict(f"[ReceivedTime] > '{last_processed_time}'")

    for em in emails:

        received_time = em.ReceivedTime

        if received_time > last_processed_time:
            last_processed_time = received_time
        
        np.append(emails, Email(em))
        sortAlerts(Email(em))

'''
function name: updateAlertsCount
inputs: None
outputs: None
side effects: prints the number of emails generated for each type of alert to the terminal
'''
def updateAlertsCount():

    for key in sl_buckets_dict:
        print(f"{key} : {len(sl_buckets_dict[key])}")

'''
function name: main
inputs: None
outputs: None
side effects: None
'''
def main():
    global last_processed_time

    outlook_app = openOutlook()

    account_name = "Logistic System Alert"

    # Checks to see if the desired email account exists within the Outlook application
    myAccount = None
    for acc in outlook_app.Accounts:
        if acc.DisplayName == account_name:
            account = acc
            break
    
    if not myAccount:
        print(f"Account '{account}' not found.")
        return

    buildBucketsDictionary()
    
    while True:
        # Retrieve new emails periodically
        extractEmailsfromInbox(outlook_app, myAccount, "Inbox", "Do Not Delete!!!")
        updateAlertsCount()

        # Time interval (in seconds) for how often the emails will be extracted
        time.sleep(60)

# Starts the program
if __name__ == "__main__":
    main()