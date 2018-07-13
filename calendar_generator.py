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


class Event:
    """A helper class for exporting calendar events to a CSV file."""

    def __init__(self, name, start, end, all_day=False):
        """
        :param name: the name of the event
        :type name: str
        :param start: the start date and time of the event
        :type start: datetime.datetime
        :param end: the end date and time of the event
        :type end: datetime.datetime
        :param allDay: determines if this is an all day event (default: False)
        """
        self.name = name
        self.start = start
        self.end = end
        self.all_day = all_day

    def __str__(self):
        return "%s: %s - %s" % (self.name, self.start, self.end)

    def __repr__(self):
        return str(self)

    def __eq__(self, o):
        if not isinstance(o, Event):
            return False
        if self.name != o.name:
            return False
        if self.start != o.start:
            return False
        if self.end != o.end:
            return False
        return True

    @property
    def csv(self):
        """creates a dict for csv.DictWriter

        :returns: a dict for a calendar event
        :rtype: dict
        """
        ret = dict()
        ret["Subject"] = self.name
        ret["Start Date"] = str(self.start.date())
        ret["Start Time"] = str(self.start.time())
        ret["End Date"] = str(self.end.date())
        ret["End Time"] = str(self.end.time())
        ret["All Day Event"] = self.all_day
        return ret


class RotationDay:
    """creates a day of the block schedule calendar."""

    def __init__(self, date, number, is_open, desc1="", desc2="", ms_act="", us_act=""):
        """
        :param date: the date of the rotation
        :param number: day number
        :param isOpen: true if school is open, or if there is a special event,
        like Community Day
        :param desc1: a description of the day.
        :param desc2: a second description of the day.
        """
        self.date = date
        self.day_number = number
        self.is_wed = date.weekday() == 2
        self.open = is_open
        if self.open:
            self.desc1 = desc1 if desc1 else "Day " + str(self.day_number)
        else:
            self.desc1 = desc1
        self.desc2 = desc2

        day = self.day_number - 1
        # put the blocks in the right order
        blocks = BLOCKS[day::-1] + BLOCKS[-1:day + 1:-1]

        if len(blocks) == 7:
            blocks = blocks[:-1]

        if not self.is_wed:
            blocks.append("MS Electives/US Academic Help")
        blocks.insert(4, "US Lunch" + ("/MS " + ms_act if ms_act else ""))
        blocks.insert(4, "MS Lunch" + ("/US " + us_act if us_act else ""))
        blocks.insert(2, "Break")

        self.blocks = blocks

    def __str__(self):
        return str(self.date) + "(" + str(self.day_number) + ")"

    def __repr__(self):
        return str(self)

    def _get_time(self, block):
        times = TIMES if not self.is_wed else WED_TIMES
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
        return None

    def get_blocks(self):
        blocks = list()
        blocks.append(self.title1)
        if self.title2:
            blocks.append(self.title2)
        if not self.open:
            return blocks
        for block_num in range(10):
            if self.is_wed and block_num == 9:
                break
            block = Event(self.blocks[block_num], *self._get_time(block_num))
            blocks.append(block)
        return blocks


def main():
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
                is_open = row[3] == "TRUE"
                try:
                    number = int(row[4])
                except IndexError:
                    continue

                day = RotationDay(date, number, is_open_pen, *(row[5:]))
                for block in day.get_blocks():
                    writer.writerow(block.csv)


if __name__ == "__main__":
    main()
