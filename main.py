import csv
import os
import ConfigParser
import json
from collections import defaultdict
import operator
import datetime

class LogEntry:
    def __init__(self, characterName, accountName, time, item, itemCount, resource, resourceQuantity, donorGuild, recipientGuild):
        # TODO: There is a trick I've forgotten that lets you assign object attributes based on the name
        # of the arguments coming in... would be better than this. Then if the format of the CSV changes
        # we only need to change the constructor signature, and not the constructor itself.
        self.characterName = characterName
        self.accountName = accountName
        self.time = time
        self.itemCount = itemCount
        self.resource = resource
        self.resourceQuantity = resourceQuantity
        self.donorGuild = donorGuild
        self.recipientGuild = recipientGuild

"""Reads a log file, returning a list of lists with the log entries"""
def readFile(filename):
    lines = []

    with open(filename, 'rb') as log:
        reader = csv.reader(log, delimiter=',', quotechar='"')
        for line in reader:
            lines.append(line)

    return lines

# Credit to https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
"""Returns the names of all of the files in a directory"""
def globDirectory(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

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

def getTimeSlice(log, startTime, endTime):
    entries = []
    print(startTime)
    print(endTime)
    dateFormat = '%m/%d/%Y %I:%M:%S %p'
    start = datetime.datetime.strptime(startTime, dateFormat)
    end = datetime.datetime.strptime(endTime, dateFormat)

    for entry in log:
        timestamp = datetime.datetime.strptime(entry.time, dateFormat)
        if (timestamp >= start and timestamp <= end):
            entries.append(entry)

    return entries

"""Filter entries to include only donations of the types specified in resourceList"""
def filterEntries(log, resourceList):
    return [e for e in log if e.resource in resourceList]

def applyMultipliers(log, multipliers):
    for entry in log:
        entry.resourceQuantity *= multipliers[entry.resource]

    return log

def sumByAccount(log):
    total = defaultdict(lambda: 0)

    for entry in log:
        total[entry.accountName] += int(entry.resourceQuantity)

    return total

def printLeaderboard(totals):
    sortedTotals = sorted(totals.items(), key=operator.itemgetter(1))
    sortedTotals.reverse()
    
    for account, total in sortedTotals:
        print(account + ": " + str(total))

def loadLogfiles(path):
    # load the log files and get them into one array
    logfiles = globDirectory(path)
    log = []
    
    for f in logfiles:
        # Read the log file, but slice off the header (the first line)
        log = combineLogs(log, readFile(path + os.sep + f)[1:])

    log = objectify(log)
    return log

def applyFilters(log, filters):
    """ Filter resources based on time slice and resource type """
    filteredLog = []

    for dates, resources in filters:
        entries = getTimeSlice(log, dates[0], dates[1])
        entries = filterEntries(entries, resources)
        filteredLog.extend(entries)

    return filteredLog

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.read('./config')
    path = config.get('OPTIONS', 'LogLocation')
    filters = json.loads(config.get('OPTIONS', 'ResourceFilters'))
    multipliers = json.loads(config.get('OPTIONS', 'ResourceMultipliers'))

    log = loadLogfiles(path)
    log = applyFilters(log, filters)
    # Apply multipliers to adjust how much each resource is worth in terms of points
    resourceMultipliers = json.loads(config.get('OPTIONS', 'ResourceMultipliers'))
    log = applyMultipliers(log, multipliers)

    # Add totals up per account and print
    log = sumByAccount(log)
    printLeaderboard(log)
