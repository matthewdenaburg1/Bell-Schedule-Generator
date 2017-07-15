#!/usr/bin/env python3

import datetime
import csv


BLOCKS = ["A", "G", "F", "E", "D", "C", "B"]
BLOCKS = list(map(lambda a: a + " Block", BLOCKS))


WED_TIMES = [  # block times (start, end) for Wednesday
        (datetime.time(8, 0), datetime.time(8, 45)),
        (datetime.time(8, 50), datetime.time(10)),
        (datetime.time(10, 0), datetime.time(10, 15)),
        (datetime.time(10, 15), datetime.time(11)),
        (datetime.time(11, 5), datetime.time(11, 45)),
        (datetime.time(11, 50), datetime.time(12, 20)),
        (datetime.time(12, 20), datetime.time(13)),
        (datetime.time(13), datetime.time(13, 45)),
        (datetime.time(13, 50), datetime.time(14, 35))
    ]
TIMES = [  # block times (start, end) for days that aren't Wednesday
        (datetime.time(8), datetime.time(8, 50)),
        (datetime.time(8, 55), datetime.time(10, 5)),
        (datetime.time(10, 5), datetime.time(10, 20)),
        (datetime.time(10, 20), datetime.time(11, 10)),
        (datetime.time(11, 15), datetime.time(11, 55)),
        (datetime.time(12), datetime.time(12, 40)),
        (datetime.time(12, 40), datetime.time(13, 20)),
        (datetime.time(13, 20), datetime.time(14, 10)),
        (datetime.time(14, 15), datetime.time(15, 5)),
        (datetime.time(15, 5), datetime.time(15, 35))
    ]


class Event(object):
    def __init__(self, name, start, end, allDay=False):
        self.name = name
        self.start = start
        self.end = end
        self.allDay = allDay

    def __str__(self):
        return "%s: %s - %s" % (self.name, self.start, self.end)

    def __repr__(self):
        return str(self)

    def __eq__(self, o):
        if not isinstance(o, Event):
            return False
        if self.name != o.name:
            return False
        elif self.start != o.start:
            return False
        elif self.end != o.end:
            return False
        return True

    @property
    def csv(self):
        ret = dict()
        ret["Subject"] = self.name
        ret["Start Date"] = str(self.start.date())
        ret["Start Time"] = str(self.start.time())
        ret["End Date"] = str(self.end.date())
        ret["End Time"] = str(self.end.time())
        ret["All Day Event"] = self.allDay
        return ret


class RotationDay(object):
    def __init__(self, date, number, isOpen, desc1="", desc2="", msAct="", usAct=""):
        self.date = date
        self.dayNumber = number
        self.isWed = date.weekday() == 2
        self.open = isOpen
        if self.open:
            self.desc1 = desc1 if desc1 else "Day " + str(self.dayNumber)
        else:
            self.desc1 = desc1
        self.desc2 = desc2

        day = self.dayNumber - 1
        # put the blocks in the right order
        blocks = BLOCKS[day::-1] + BLOCKS[-1:day + 1:-1]
        
        if len(blocks) == 7:
            blocks = blocks[:-1]

        if not self.isWed:
            blocks.append("MS Electives/US Academic Help")
        blocks.insert(4, "US Lunch" + ("/MS " + msAct if msAct else ""))
        blocks.insert(4, "MS Lunch" + ("/US " + usAct if usAct else ""))
        blocks.insert(2, "Break")

        self.blocks = blocks

    def __str__(self):
        return str(self.date) + "(" + str(self.dayNumber) + ")"

    def __repr__(self):
        return str(self)

    def _getTime(self, block):
        times = TIMES if not self.isWed else WED_TIMES
        start, end = times[block]
        start = datetime.datetime.combine(self.date, start)
        end = datetime.datetime.combine(self.date, end)
        return start, end

    @property
    def title1(self):
        return Event(self.desc1, self.date, self.date, True)

    @property
    def title2(self):
        if self.desc2:
            return Event(self.desc2, self.date, self.date, True)
        else:
            return None

    def getBlocks(self):
        blocks = list()
        blocks.append(self.title1)
        if self.title2:
            blocks.append(self.title2)
        if not self.open:
            return blocks
        for block_num in range(10):
            if self.isWed and block_num == 9:
                break
            block = Event(self.blocks[block_num], *self._getTime(block_num))
            blocks.append(block)
        return blocks


if __name__ == "__main__":
    with open("2017-2018_MS_US_Cal-input.csv", "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header row
        with open("2017-2018_calendar.csv", "w", newline="") as csvout:
            field_names = ["Subject", "Start Date", "Start Time", "End Date",
                "End Time", "All Day Event"]

            writer = csv.DictWriter(csvout, field_names, dialect="excel")
            writer.writeheader()

            for row in reader:
                date = datetime.datetime.strptime(row[0], "%m-%d-%Y")
                if date.weekday() >= 5:
                    continue
                isOpen = row[3] == "TRUE"
                try:
                    number = int(row[4])
                except:
                    continue
                
                day = RotationDay(date, number, isOpen, *(row[5:]))
                for block in day.getBlocks():
                    writer.writerow(block.csv)

