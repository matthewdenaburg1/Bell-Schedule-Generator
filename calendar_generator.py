#!/usr/bin/env python3

import datetime
import csv


BLOCKS = ["A", "G", "F", "E", "D", "C", "B"]
BLOCKS = list(map(lambda a: a + " Block", BLOCKS))


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
    def __init__(self, date, number, isOpen, desc1="", desc2="", msActivity="", usActivity=""):
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
        blocks = BLOCKS[day::-1] + BLOCKS[-1:day + 1:-1]
        
        if len(blocks) == 7:
            blocks = blocks[:-1]

        if not self.isWed:
            blocks.append("MS Electives/US Academic Help")
        blocks.insert(4, "US Lunch" + ("/MS " + msActivity if msActivity else ""))
        blocks.insert(4, "MS Lunch" + ("/US " + usActivity if usActivity else ""))
        blocks.insert(2, "Break")

        self.blocks = blocks

    def __str__(self):
        return str(self.date) + "(" + str(self.dayNumber) + ")"

    def __repr__(self):
        return str(self)

    def _getWedTime(self, b):
        date = datetime.datetime(self.date.year, self.date.month, self.date.day)
        if b == 1:
            # start time for block 1
            s = date.replace(hour=8, minute=0)
            e = date.replace(hour=8, minute=45)
        elif b == 2:
            s = date.replace(hour=8, minute=50)
            e = date.replace(hour=10, minute=0)
        elif b == 3:
            s = date.replace(hour=10, minute=0)
            e = date.replace(hour=10, minute=15)
        elif b == 4:
            s = date.replace(hour=10, minute=15)
            e = date.replace(hour=11, minute=0)
        elif b == 5:
            s = date.replace(hour=11, minute=5)
            e = date.replace(hour=11, minute=45)
        elif b == 6:
            s = date.replace(hour=11, minute=50)
            e = date.replace(hour=12, minute=20)
        elif b == 7:
            s = date.replace(hour=12, minute=20)
            e = date.replace(hour=13, minute=0)
        elif b == 8:
            s = date.replace(hour=13, minute=0)
            e = date.replace(hour=13, minute=45)
        elif b == 9:
            s = date.replace(hour=13, minute=50)
            e = date.replace(hour=14, minute=35)
        return s, e

    def _getDayTime(self, b):
        date = datetime.datetime(self.date.year, self.date.month, self.date.day)
        if b == 1:
            s = date.replace(hour=8)
            e = date.replace(hour=8, minute=50)
        elif b == 2:
            s = date.replace(hour=8, minute=55)
            e = date.replace(hour=10, minute=5)
        elif b == 3:
            s = date.replace(hour=10, minute=5)
            e = date.replace(hour=10, minute=20)
        elif b == 4:
            s = date.replace(hour=10, minute=20)
            e = date.replace(hour=11, minute=10)
        elif b == 5:
            s = date.replace(hour=11, minute=15)
            e = date.replace(hour=11, minute=55)
        elif b == 6:
            s = date.replace(hour=12)
            e = date.replace(hour=12, minute=40)
        elif b == 7:
            s = date.replace(hour=12, minute=40)
            e = date.replace(hour=13, minute=20)
        elif b == 8:
            s = date.replace(hour=13, minute=20)
            e = date.replace(hour=14, minute=10)
        elif b == 9:
            s = date.replace(hour=14, minute=15)
            e = date.replace(hour=15, minute=5)
        elif b == 10:
            s = date.replace(hour=15, minute=5)
            e = date.replace(hour=15, minute=35)
        return s, e

    def _getTime(self, b):
        if self.isWed:
            return self._getWedTime(b)
        else:
            return self._getDayTime(b)

    @property
    def title1(self):
        return Event(self.desc1, self.date, self.date, True)

    @property
    def title2(self):
        if self.desc2:
            return Event(self.desc2, self.date, self.date, True)
        else:
            return None

    @property
    def block1(self):
        start, end = self._getTime(1)
        return Event(self.blocks[0], start, end)

    @property
    def block2(self):
        start, end = self._getTime(2)
        return Event(self.blocks[1], start, end)

    @property
    def block3(self):
        start, end = self._getTime(3)
        return Event(self.blocks[2], start, end)

    @property
    def block4(self):
        start, end = self._getTime(4)
        return Event(self.blocks[3], start, end)

    @property
    def block5(self):
        start, end = self._getTime(5)
        return Event(self.blocks[4], start, end)

    @property
    def block6(self):
        start, end = self._getTime(6)
        return Event(self.blocks[5], start, end)

    @property
    def block7(self):
        start, end = self._getTime(7)
        return Event(self.blocks[6], start, end)

    @property
    def block8(self):
        start, end = self._getTime(8)
        return Event(self.blocks[7], start, end)

    @property
    def block9(self):
        start, end = self._getTime(9)
        return Event(self.blocks[8], start, end)

    @property
    def block10(self):
        if self.isWed:
            return None
        start, end = self._getTime(10)
        return Event(self.blocks[9], start, end)

    def getBlocks(self):
        blocks = list()
        blocks.append(self.title1)
        if self.title2:
            blocks.append(self.title2)
        if not self.open:
            return blocks
        # for i in range(1, 11):
            # if i == 10 and self.isWed:
                # continue
            # blocks.append(self.block(blockNum=i))
        blocks.append(self.block1)
        blocks.append(self.block2)
        blocks.append(self.block3)
        blocks.append(self.block4)
        blocks.append(self.block5)
        blocks.append(self.block6)
        blocks.append(self.block7)
        blocks.append(self.block8)
        blocks.append(self.block9)
        if self.block10:
            blocks.append(self.block10)
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
            i = 0
            for row in reader:
                date = datetime.datetime.strptime(row[0], "%m-%d-%Y")
                if date.weekday() >= 5:
                    continue
                # print(row)
                isOpen = row[3] == "TRUE"
                try:
                    number = int(row[4])
                except:
                    continue
                
                desc1, desc2, msActivity, usActivity = row[5:]
                # desc2 = row[6]
                # day = RotationDay(date, number, isOpen, desc1, desc2, msActivity, usActivity)
                day = RotationDay(date, number, isOpen, *(row[5:]))
                # print(day.title1)
                for block in day.getBlocks():
                    writer.writerow(block.csv)
                    i += 1
    pass

