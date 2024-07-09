import win32com.client
import os
import numpy as np
from emailClass import Email
from datetime import datetime, timedelta

'''
Global Variables
'''
emails = np.array([])
'''
function name: openOutlook
inputs: None
outputs: None
side effects: None
References: https://www.codeforests.com/2020/06/04/python-to-read-email-from-outlook/, ChatGPT 3.5
'''
def openOutlook():

    # Access the Outlook Application and its MAPI (Messaging Application Programming Interface) namespace
    outlook_app = win32com.client.Dispatch('outlook.application').GetNamespace("MAPI")
    extractEmailsfromInbox(outlook_app, "Logistic System Alert", "Inbox", "Do Not Delete!!!")

'''
function name: extractEmailsfromInbox
inputs: app - connection to the Outlook application
        account - name of the email account being examined
        folder - name of the folder that emails are being read from
        subfolder - name of the subfolder that contains the emails to be extracted
outputs: None
side effects: Populates global "emails" NumPy array with Email Objects that contain all of the necessary email data from a particular inbox
References: https://medium.com/@balakrishna0106/automating-outlook-effortless-email-retrieval-using-pythons-win32com-client-796b13746ad9, 
            ChatGPT 3.5
'''
def extractEmailsfromInbox(app, account, folder, subfolder):

    # Checks to see if the desired email account exists within the Outlook application
    myAccount = None
    for acc in app.Accounts:
        if acc.DisplayName == account:
            account = acc
            break
    
    if not myAccount:
        print(f"Account '{account}' not found.")
        return
    
    primary_inbox = app.Folders(myAccount.DeliveryStore.DisplayName).Folders[folder]
    
    subfolder_inbox = primary_inbox.Folders[subfolder]

    emails = subfolder_inbox.Items

    for em in emails:
        np.append(emails, Email(em))