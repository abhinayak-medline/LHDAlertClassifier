import numpy as np

'''
Global Variables
'''
sl_buckets = {}
subject_lines = [
    "*URGENT*HTTP Service is down on <TMAP Server> at <Date>", "<Branch> - CROSSDOCK SERVICE CALL FAILURE", 
    "<Branch> - ERROR RECORDS IN T_CSINTERFACE", "<Branch> - RP Failed Messages", "<Branch> - WORK ASSIGN FAILED TO CATEGORIZE",
    "<Branch> dispatcher alert", "<Branch> G2P Incorrect Employee Issues", "<Branch> G2P MHE Pick Errors",
    "<Branch> G2P MHE Putaway Errors", "<Branch> ZPOGI - Stuck in picking", "<Server> - Hourly upload files",
    "<Server> HeartBeat Status is down", "<Service> down on <Server>", "15 minute old file on <Server>", "Additional Pick Errors",
    "Additional Pick not processed", "ADDPICKWQ Alert", "Alert : <Branch> Containers zero picked and in status 16 - need destaging.",
    "Alert t_csmastcontdtl multiple label_addr1 for mark_num", 
    'Alert: [HIGH] 1 alert for "CBMA_ExtEOIOPick" on "af.p42.prdsapgpidbha" by scenario "G2P_<Branch>_PickConfirmOut"',
    "Alert: Down: <Service> on Node <Server>", "Alert: ORA-00018 and ORA-03114", "ASN Not In CCT","BAM Notification",
    "Bot Loading <#> Error Message For Processing", "Branches with more than 150 orders not assigned carrier code",
    "CA APM Alert from munprdsmap31: G2P Backlog Messages in Caution state", "Carrier close alert",
    "CCT C_QUEUEDMESSAGE INPROCESS FAILURE", "CCT C_QUEUEDMESSAGE Threshold of 3500 Exceeded", "CCT T_QUEUEDMESSAGE INPROCESS FAILURE",
    "Completed wave still in 29", "Container stuck in status 11", "CPU utilization is at <##%> on <Server>",
    "Critical events detected for All Critical Alerts!", "Dead Message - order_close_ul-UpdatePickList",
    "Defunct process in prdcatap03 : High Priority", "Deleted Wave Stranded Pick WKA", "Delivery Not In Catalyst",
    "Delivery Not In CCT", "Down: <Service> on Node <Server>", "Embroidery non-LFE", "Error records in T_CSINTERFACE table",
    "Error while adjusting inventory from Auto lot update process", "Events detected for All Critical Alerts.","Failed Ship Close",
    "FedEx Database Service Error - NEW", "G2P <Branch> Location Checks - ALERT", "G2P <Branch> Pick Confirm Issues",
    "G2P <Branch> PRD Interface XML Errors", "G2P <Branch> Swisslog Pick Confirm Issues", 
    "G2P AUTOSTORE <Branch> Order Download Issues","G2P CARRYPICK <Branch> Order Download Issues", "G2P Download Order Issue Transaction Report",
    "G2P KNAPP <Branch> Order Download Issues", "G2PPA printing error - G2PPA device unavailable", "High : Missed H and Z Schedule",
    "HIGH: <Loftware Server> - Old files on the Loftware Shares", "High: MTP duplicate tracking", "HZ Backorders that Missed Cutoffs",
    "List of Deliveries missing Guaranteed flag", "Medline ship units need closing", "Message based Alerting Alert: CBMA_WMS",
    "Missing ITEMLOCCLS records", "Missing mark_num detail", "Missing t_csinterface Records", "More than 10 ship units have rating error",
    "MUNPRDFDX03 - FedEx DB Log File Size Threshold", "MUNPRDP<##> - - 0 KB files found", "Packlist Error", "PCAT<P#> Blocking Alert",
    "Precision file older than 2 days", "Print and Apply Error (G2P)", "Print and Apply Error (Numina)", 
    "Print Spooler Service is <Status> on <Server>", "Qty_alloc with no open work Assignment", "Recoverable Message Alert",
    "Setupsysctrl Error Record", "Shipments in status 60 for over 60 minutes", "Shipments not shipclosed",
    "Splunk Alert: Logistics_Alert and MIS_WMS-SHP_PRE_POGI_ASN_GENERATE", "Stranded Moves","t_csmastconthdr with no detail records",
    "Transhist Recovery File : Medium", "Unwaved delivery with Alloc_Qty", "UPS File Monitor",
    "Warning events detected for All Critical Alerts!", "Wave check failed", "Wave Errors", "Wave not processed","WDScan.dir is missing",
    "Whszone alert", "WMS <Branch> crossdock service call errors", "WMS <Branch> Missing Ship Units", "Work assign fail to categorize",
    "XML Recovery File : Medium", "Zero picked WKA", "Unmatched"
    ]

'''
function name: buildBucketDictionary
inputs: None
outputs: sl_buckets - dictionary that will store the sorted alerts
side effects: Populates the global sl_buckets dictionary with keys representing the different subject lines of the email alerts
'''
def buildBucketsDictionary():
    sl_buckets = {key: [] for key in subject_lines}
    return sl_buckets

'''
function name: generateBucketSubstrings
inputs: buckets - dictionary that will store the sorted emails
outputs: bucket_substrings - 2D list that stores non-keyword parts of each key
side effects: None
'''
def generateBucketSubstrings(buckets):

    fillerKeywords = ["<Branch>", "<TMAP Server>", "<Date>", "<Server>", "<Service>", "<##%>", "<Loftware Server>", "<##>", "<P#>", "<Status>", "<#>"]

    bucket_substrings = []

    for key in buckets:
        # Appends the keywords that exist in the current key to a separate list
        keywords_in_key = [keyword for keyword in fillerKeywords if key.count(keyword) != 0]

        # Modifies the current key to replace all of its keywords with the arbitrary string "<xx>"
        mod_key = ''.join(key.replace(ks, "<xx>") for ks in keywords_in_key)

        if len(keywords_in_key) == 0:
            bucket_substrings.append([key])
        else:
            # If the key contains any keywords, it splits the key into several substrings at each of the <xx> locations
            bucket_substrings.append(mod_key.split("<xx>"))
    
    return bucket_substrings

'''
function name: sortEmail
inputs: email - Email Object to be sorted
        buckets - dictionary that will store the sorted emails
        bucket_substrings - 2D list that stores non-keyword parts of each key
outputs: buckets - dictionary that Email object will be pushed into where it will be matched to a key based on its subject line
side effects:
'''
def sortAlerts(email, buckets, bucket_substrings):

    curr_index = 0
    matchFound = False

    for key in buckets:
        
        # Checks if the key has been split or not due to whether or not it contains any keywords
        if len(bucket_substrings[curr_index]) == 1:

            if bucket_substrings[curr_index][0] in email.subject:
                email = assignPriority(key, email)
                buckets[key].append(email)
                matchFound = True
                break

        elif len(bucket_substrings[curr_index]) > 1:

            target_match_num = len(bucket_substrings[curr_index])
            curr_match_num = 0

            # Checks if every non-keyword substring of the key is contained within the email's subject line
            curr_match_num += sum(1 for ks in bucket_substrings[curr_index] if ks in email.subject)
            
            if curr_match_num == target_match_num:
                email = assignPriority(key, email)
                buckets[key].append(email)
                matchFound = True
                break
        
        curr_index+=1

    if matchFound == False:
        buckets["Unmatched"].append(email)
            
    return buckets


def assignPriority(key, email):

    priority_1 = [
        "<Server> HeartBeat Status is down",
        "Alert: Down: <Service> on Node <Server>",
        "Alert: ORA-00018 and ORA-03114",
        "BAM Notification",
        "CA APM Alert from munprdsmap31: G2P Backlog Messages in Caution state",
        "CCT C_QUEUEDMESSAGE Threshold of 3500 Exceeded",
        "CPU utilization is at <##%> on <Server>",
        "Critical events detected for All Critical Alerts!",
        "Defunct process in prdcatap03 : High Priority",
        "Deleted Wave Stranded Pick WKA",
        "Down: <Service> on Node <Server>",
        "HIGH: <Loftware Server> - Old files on the Loftware Shares",
        "High: MTP duplicate tracking",
        "PCAT<P#> Blocking Alert",
        "Print Spooler Service is <Status> on <Server>",
        "Splunk Alert: Logistics_Alert:MIS_ECC-EDI_OUTBOUND_SHIP_ASN and MIS_WMS-SHP_PRE_POGI_ASN_GENERATE",
        "Wave check failed",
        "Wave Errors"
    ]

    priority_2 = [
        "<Branch> G2P MHE Pick Errors",
        "<Branch> G2P MHE Putaway Errors",
        "<Service> down on <Server>",
        "Alert t_csmastcontdtl multiple label_addr1 for mark_num",
        "Branches with more than 150 orders not assigned carrier code",
        "CCT T_QUEUEDMESSAGE INPROCESS FAILURE",
        "Dead Message - order_close_ul-UpdatePickList",
        "Failed Ship Close",
        "FedEx Database Service Error - NEW",
        "High : Missed H and Z Schedule",
        "HZ Backorders that Missed Cutoffs",
        "List of Deliveries missing Guaranteed flag",
        "Missing mark_num detail",
        "Shipments in status 60 for over 60 minutes",
        "t_csmastconthdr with no detail records",
        "Unwaved delivery with Alloc_Qty",
        "WDScan.dir is missing",
        "Whszone alert",
        "WMS <Branch> crossdock service call errors"
    ]

    priority_3 = [
        "*URGENT*HTTP Service is down on <TMAP Server> at <Date>",
        "<Branch> - ERROR RECORDS IN T_CSINTERFACE",
        "<Server> - Hourly upload files",
        "Additional Pick Errors",
        "Additional Pick not processed",
        "ADDPICKWQ Alert",
        "Alert : <Branch> Containers zero picked and in status 16 - need destaging.",
        "ASN Not In CCT",
        "Delivery Not In Catalyst",
        "Delivery Not In CCT",
        "Error records in T_CSINTERFACE table",
        "G2P <Branch> Location Checks - ALERT",
        "G2P <Branch> Pick Confirm Issues",
        "G2P <Branch> Swisslog Pick Confirm Issues",
        "G2P AUTOSTORE <Branch> Order Download Issues",
        "G2P CARRYPICK <Branch> Order Download Issues",
        "G2P KNAPP <Branch> Order Download Issues",
        "G2PPA printing error - G2PPA device unavailable",
        "Missing t_csinterface Records",
        "More than 10 ship units have rating error",
        "Qty_alloc with no open work Assignment",
        "Recoverable Message Alert",
        "Setupsysctrl Error Record",
        "Stranded Moves",
        "Transhist Recovery File : Medium",
        "UPS File Monitor",
        "Work assign fail to categorize",
        "XML Recovery File : Medium",
        "Zero picked WKA error"
    ]

    priority_4 = [
        "<Branch> - CROSSDOCK SERVICE CALL FAILURE",
        "<Branch> dispatcher alert",
        "15 minute old file on <Server>",
        "Completed wave still in 29",
        "Container stuck in status 11",
        "Embroidery non-LFE",
        "Error while adjusting inventory from Auto lot update process",
        "Missing ITEMLOCCLS records",
        "MUNPRDP## - - 0 KB files found"
    ]

    priority_5 = [
        "<Branch> - RP Failed Messages",
        "<Branch> - WORK ASSIGN FAILED TO CATEGORIZE",
        "<Branch> G2P Incorrect Employee Issues",
        "<Branch> ZPOGI - Stuck in picking",
        'Alert: [HIGH] 1 alert for "CBMA_ExtEOIOPick" on "af.p42.prdsapgpidbha"  by scenario "G2P_<Branch>_PickConfirmOut"',
        "Bot Loading # Error Message For Processing",
        "Carrier close alert",
        "CCT C_QUEUEDMESSAGE INPROCESS FAILURE",
        "Events detected for All Critical Alerts.",
        "G2P <Branch> PRD Interface XML Errors",
        "G2P Download Order Issue Transaction Report",
        "Medline ship units need closing",
        "Message based Alerting Alert: CBMA_WMS",
        "Packlist Error",
        "Precision file older than 2 days",
        "Print and Apply Error (G2P)",
        "Print and Apply Error (Numina)",
        "Shipments not shipclosed",
        "Warning events detected for All Critical Alerts!",
        "WMS <Branch> Missing Ship Units",
        "MUNPRDFDX03  - FedEx DB Log File Size Threshold"
    ]

    if key in priority_1:
        email.urgency = 1
    elif key in priority_2:
        email.urgency = 2
    elif key in priority_3:
        email.urgency = 3
    elif key in priority_4:
        email.urgency = 4
    elif key in priority_5:
        email.urgency = 5
    
    return email