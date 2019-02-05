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

# Open a the log file and return the lines in a list
def readFile(filename):
    with open(filename, 'r') as log:
        reader = csv.reader(log, delimiter=',', quotechar='"')
        return [l for l in reader]

# sum all resouce quantities by account and type of resource
def sumByAccount(log, resourceTypes):
    total = defaultdict(list)

    for entry in log:
        if not total[entry.accountName]:
            total[entry.accountName].extend([0] * len(resourceTypes))

        total[entry.accountName][resourceTypes.index(entry.resource)] += int(entry.resourceQuantity)

    return total

# print into a nice format the data
def printLeaderboard(totals, resourceTypes, outputfile):
    table = PrettyTable(['Account', *resourceTypes])
    
    for account in totals:
        table.add_row([account, *totals[account]])

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

    # get all the logfiles with .csv extension
    logfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(".csv")]
    log = []

    if not logfiles:
        print("No log files found in: " + path)
        exit()

    # combine all the log files in the logs directory
    for f in logfiles:
        tempLog = log
        tempLog.extend(readFile(path + os.sep + f))
        log = [list(i) for i in set(tuple(i) for i in tempLog)]

    resourceTypes = json.loads(config.get('OPTIONS', 'ResourceTypes'))

    # convert to a list of objects
    log = [LogEntry(*tuple(e)) for e in log]

    # keep only the data for the resource types specified in the config
    log = [e for e in log if e.resource in resourceTypes]
    
    log = sumByAccount(log, resourceTypes)
    printLeaderboard(log, resourceTypes, outputfile)
