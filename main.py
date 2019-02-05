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

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Neverwinter donations parser')
    parser.add_argument('outputfile', nargs='?', help='Specify the output file (defaults to "output.txt")', default="output.txt")
    args = parser.parse_args()

    outputfile = args.outputfile

    config = configparser.ConfigParser()
    config.read('./config')
    path = config.get('OPTIONS', 'LogLocation')
    resourceTypes = json.loads(config.get('OPTIONS', 'ResourceTypes'))

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


    # convert to a list of objects
    log = [LogEntry(*tuple(e)) for e in log]

    # keep only the data for the resource types specified in the config
    log = [e for e in log if e.resource in resourceTypes]
    
    # Sum resource quantities for each account
    data = defaultdict(list)
    for entry in log:
        if not data[entry.accountName]:
            data[entry.accountName].extend([0] * len(resourceTypes))

        data[entry.accountName][resourceTypes.index(entry.resource)] += int(entry.resourceQuantity)

    # export data into a pretty table
    table = PrettyTable(['Account', *resourceTypes])
    for account in data:
        table.add_row([account, *data[account]])

    table_txt = table.get_string()
    with open(outputfile, 'w') as file:
        file.write(table_txt)