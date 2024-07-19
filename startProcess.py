import win32com.client
import time
import numpy as np
from emailClass import Email
from sortEmail import buildBucketsDictionary, sortAlerts, generateBucketSubstrings, sl_buckets, subject_lines
import datetime

'''
Global Variables
'''
alerts = np.array([])
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

    global last_processed_time, sl_buckets, bucket_substrings
    
    primary_inbox = app.Folders(account.DeliveryStore.DisplayName).Folders[folder]
    
    subfolder_inbox = primary_inbox.Folders[subfolder]

    emails = subfolder_inbox.Items

    print("Inbox Size: " + str(len(emails)))

    emailsProcessed = 0

    for em in emails:
        
        #np.append(alerts, Email(em))
        print(Email(em).subject)
        # print(em)
        sl_buckets = sortAlerts(Email(em), sl_buckets, bucket_substrings)
        emailsProcessed+=1
        if emailsProcessed == 50:
            break

'''
function name: updateAlertsCount
inputs: None
outputs: None
side effects: prints the number of emails generated for each type of alert to the terminal
'''
def updateAlertsCount():

    for key in sl_buckets:
        print(f"{key} : {len(sl_buckets[key])}")

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
        extractEmailsfromInbox(outlook_app, myAccount, "Inbox", "Do Not Delete!!!")
        updateAlertsCount()
        break

        # Update last processed time to current time after processing emails
        #last_processed_time = datetime.datetime.now()

        # Time interval (in seconds) for how often the emails will be extracted
        time.sleep(10)

# Starts the program
if __name__ == "__main__":
    main()