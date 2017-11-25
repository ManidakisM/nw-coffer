# Cofferer

Hello Neverwintians, one and all!
I wrote this script to help make life easier for those of us that count up guild coffer doantions.
It is intended to be used with a set of exported CSVs, exported from the game via the command:

```
/ExportGuildDonationLog <filename>
```

By default, all donatable currencies except for the tendable ones are included.
That means, out of the box you'll be getting statistics on log entries for:

- Heroic Shards of Power
- Adventurer's Shards of Power
- Dungeoneer's Shards of Power
- Conqueror's Shards of Power
- Labor
- Gold
- Glory
- Gems
- Surplus Equipment
- Astral Diamond Chests
- Treasures of Tyranny
- Frozen Treasures
- Fey Trinkets
- Dark Gifts
- Influence

## Configuration file
Here are the available configuration options:

**LogLocation** - the directory containing the log files. All files in this directory will be parsed, so make sure that ONLY exported coffer log files in CSV format exist in this directory!
**ResourceTypes** - the resource types that you want to have counted up
**ResourceMultipliers** - the amount to multiply each resource type by. This list should be the same length as the ResourceTypes list. Use multipliers when you want to adjust how much a donation in a particular resource category counts for in the final output.

## Known issues with the coffer log (things I can't fix)
It looks like the last entries in the exported log are actually donations made to the decorator.
This may or may not be the intended behavior - it seemed odd to me.
Regardless, you can ignore these entries simply by not specifying them as one of the filtered resources in the configuration file.
 
