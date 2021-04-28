#!/usr/bin/env python3
# https://gitlab.com/juan.abia/updatearkk/-/blob/develop/main.py

import os
from urllib import request
from datetime import datetime
import csv


def download(urlresp, file_name):
    opener = request.build_opener()
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    request.install_opener(opener)
    request.urlretrieve(urlresp, file_name)


def rotatecsv():
    os.rename(csv0, csv1)
    download(url, csv0)


def undoRotation():
    os.remove(csv0)
    os.rename(csv1, csv0)


def csvtodict(csvfile, dict):
    with open(csvfile, 'r') as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if row[0] == "":
                return aux
            if i != 0:
                if not(row[3] in stockBlackList):
                    dict[row[3]] = [row[2]]
                    dict[row[3]].append(i)
                    dict[row[3]].append(float(row[7]))
            if i == 1:
                aux = row[0]


def checkdate(d0, d1):
    d0 = datetime.strptime(d0, "%m/%d/%Y")
    d1 = datetime.strptime(d1, "%m/%d/%Y")

    if (d0-d1).days == 0:
        print("No days have passed!")
        undoRotation()
        return 0

    print("last update: {}   |   days between dates: {}".format(d1.strftime("%d/%m/%y"), (d0 - d1).days))
    return 1


def countChanges(dict0, dict1):
    ch, bigCh, add, rem = {}, {}, {}, {}

    for stock0 in dict0:
        if not(stock0 in dict1):
            add[stock0] = dict0[stock0]
        else:
            if round(dict0[stock0][2], 1) != round(dict1[stock0][2], 1):
                ch[stock0] = dict0[stock0]
                if abs(dict0[stock0][2] - dict1[stock0][2]) >= bigChangePct:
                    bigCh[stock0] = dict0[stock0]
    for stock1 in dict1:
        if not(stock1 in dict0):
            rem[stock1] = (dict1[stock1])

    return ch, bigCh, add, rem


def emptydir():
    if os.path.exists(csv0):
        return 0
    print("Empty directory\n downloading csv")
    download(url, csv0)
    return 1


def main():
    if emptydir():
        return 0

    rotatecsv()

    dict0, dict1 = {}, {}
    date0 = csvtodict(csv0, dict0)
    date1 = csvtodict(csv1, dict1)

    if not(checkdate(date0, date1)):
        return 0

    changes, bigChanges, additions, removals = countChanges(dict0, dict1)
    print("You have to make the next updates:\n"
          "\tAllocation changes: {}\n"
          "\tBig allocation changes: {}\n"
          "\tStock additions: {}\n"
          "\tStock removals: {}\n".format(len(changes), len(bigChanges), len(additions), len(removals)))
    answer = input("Do you want to proceed?(y/n):")

    if answer.lower() != "y":
        undoRotation()
        return 0

    if len(changes) > 0:
        input("Allocation Changes:")
        atATime = 0
        for change in changes:
            print("{} % \t--> \t{} %   \t{}\t {}\n".format(dict1[change][2], dict0[change][2], change, dict0[change][0]))
            atATime += 1
            if atATime == atATimeChanges:
                input("----------------------------------------------------------------------\n")
                atATime = 0
    else:
        input("No changes")

    if len(additions) > 0:
        input("Additions:")
        for addition in additions:
            print("{} % \t{} \t{}\n".format(dict0[addition][2], addition, dict0[addition][0]))
    else:
        input("No additions")

    if len(removals) > 0:
        input("Removals:")
        for removal in removals:
            print("{} % \t{} \t{}\n".format(0, removal, dict1[removal][0]))
    else:
        input("No removals")
    os.remove(csv1)
    if input("Display full list? (y/n):").lower() != "y":
        return 0

    for stock in dict0:
        print("{} % \t{} \t{}\n".format(dict0[stock][2], stock, dict0[stock][0]))

# Uncomment the etf you want, and comment all the other ones
#ARKK
url = 'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv'

#ARKG
#url = "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_GENOMIC_REVOLUTION_MULTISECTOR_ETF_ARKG_HOLDINGS.csv"

#ARKQ
#url = "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_AUTONOMOUS_TECHNOLOGY_&_ROBOTICS_ETF_ARKQ_HOLDINGS.csv"

#ARKW
#url = "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.csv"

#ARKF
#url = "https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.csv"


csv0 = os.getcwd() + '/csv0.csv'
csv1 = os.getcwd() + '/csv1.csv'
stockBlackList = [""]                   # Place here the tickers of the stocks you can't buy on your broker
atATimeChanges = 3                      # Number of stocks to show at a time when updating allocations
bigChangePct = 1                        # Percentage difference to consider it a big change
main()
