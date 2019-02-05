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

    parser = argparse.ArgumentParser(description='Combine log files into one big csv')
    parser.add_argument('outputfile', nargs='?', help='Specify the output file (defaults to "combined_logs.csv")', default="combined_logs.csv")
    args = parser.parse_args()

    outputfile = args.outputfile

    config = configparser.ConfigParser()
    config.read('./config')
    path = config.get('OPTIONS', 'LogLocation')
    resourceTypes = ["Heroic Shard of Power", "Adventurer's Shard of Power", "Dungeoneer's Shard of Power", "Conqueror's Shard of Power", "Professions Supplies", "Gold", "Glory", "Gems", "Surplus Equipment", "Astral Diamond Chests", "Treasures of Tyranny", "Frozen Treasures", "Fey Trinkets", "Dark Gifts", "Influence"]

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

    # export all data to a new csv file
    with open(outputfile, "w", newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL, delimiter=',', quotechar='"')
        
        writer.writerow(resourceTypes)
        for line in log:
            writer.writerow(line)

    exit()