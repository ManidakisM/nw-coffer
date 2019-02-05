import csv
import os
import configparser
import json
from collections import defaultdict
import operator
from prettytable import PrettyTable
import argparse

class LogEntry:
    def __init__(self, *args):
        (self.characterName, 
        self.accountName, 
        self.time, 
        self.item, 
        self.itemCount, 
        self.resource, 
        self.resourceQuantity, 
        self.donorGuild, 
        self.recipientGuild) = args

"""Reads a log file, returning a list of lists with the log entries"""
def readFile(filename):
    lines = []

    with open(filename, 'r') as log:
        reader = csv.reader(log, delimiter=',', quotechar='"')
        for line in reader:
            lines.append(line)

    return lines

# Credit to https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
"""Returns the names of all of the files in a directory with '.csv' extension"""
def globDirectory(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(".csv")]

"""Combine two log files, returning the unique entries in each"""
def combineLogs(log1, log2):
    log1.extend(log2)
    # Credit to https://stackoverflow.com/questions/3724551/python-uniqueness-for-list-of-lists
    combined = [list(i) for i in set(tuple(i) for i in log1)]
    return combined

"""
Takes a list of lists, and returns a list of objects, where each object is a representation of a row in
 the log file
"""
def objectify(log):
    l = []
    for entry in log:
        l.append(LogEntry(*tuple(entry)))

    return l

"""Filter entries to include only donations of the types specified in resourceList"""
def filterEntries(log, resourceList):
    return [e for e in log if e.resource in resourceList]

def sumByAccount(log, resourceTypes):
    total = defaultdict(list)

    for entry in log:
        for resource in resourceTypes:
            if resourceTypes.index(resource) not in total[entry.accountName]:
                total[entry.accountName].append(resourceTypes.index(resource))

    for entry in log:
        for resource in resourceTypes:
                total[entry.accountName][resourceTypes.index(resource)] = 0

    for entry in log:
        total[entry.accountName][resourceTypes.index(entry.resource)] += int(entry.resourceQuantity)

    return total

def printLeaderboard(totals, resourceTypes, outputfile):
    headers = ['Account']
    i = 1
    for resource in resourceTypes:
        headers.insert(i, resource)
        i += 1

    table = PrettyTable(headers)
    
    for account in totals:
        row = [account]
        i = 1
        for resource in totals[account]:
            row.insert(i, resource)
            i += 1

        table.add_row(row)

    table_txt = table.get_string()
    with open(outputfile, 'w') as file:
        file.write(table_txt)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Neverwinter donations parser')
    parser.add_argument('outputfile', nargs='?', help='Specify the output file (defaults to "output.txt")', default="output.txt")
    args = parser.parse_args()

    outputfile = args.outputfile

    config = configparser.ConfigParser()
    config.read('./config')
    path = config.get('OPTIONS', 'LogLocation')

    logfiles = globDirectory(path)
    log = []

    if not logfiles:
        print("No log files found in: " + path)
        exit()

    for f in logfiles:
        log = combineLogs(log, readFile(path + os.sep + f))

    resourceTypes = json.loads(config.get('OPTIONS', 'ResourceTypes'))

    log = objectify(log)
    log = filterEntries(log, resourceTypes)
    log = sumByAccount(log, resourceTypes)
    printLeaderboard(log, resourceTypes, outputfile)
