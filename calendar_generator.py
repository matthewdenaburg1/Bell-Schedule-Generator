#!/usr/bin/env python3

from typing import Dict, Tuple, List

import datetime
import csv


class Event:
    """A helper class for exporting calendar events to a CSV file."""

    def __init__(self, name: str, start: datetime.datetime, end: datetime.datetime,
                 all_day: bool = False):
        """
        name: the name of the event
        start: the start date/time of the event
        end: the end date/time of the event
        allDay: true if this is an all day event
        """
        self.name = name
        self.start = start
        self.end = end
        self.all_day = all_day

    def __str__(self):
        return "{self.name}: {self.start} - {self.end}".format(self=self)

    def __repr__(self):
        return str(self)

    def __eq__(self, other: "Event"):
        if other is None:
            return False
        if id(self) == id(other):
            return True
        if not isinstance(other, Event):
            return False
        if self.name != other.name or self.start != other.start or self.end != other.end:
            return False
        return True

    @property
    def csv(self) -> Dict[str, str]:
        """creates a dict for csv.DictWriter
        :return: a dict containing keys for a calendar event
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
    """Creates a day of the block schedule calendar."""

    def __init__(self, date: datetime.date, day_number: int, is_open: bool,
                 primary_description: str, secondary_description: str = "",
                 ms_activity: str = "", us_activity: str = ""):
        """
        :param date: the date of the rotation
        :param day_number: day number
        :param is_open: true if school is open, or if there is a special event, like Community Day
        :param primary_description: a description of the day
        :param secondary_description: a second description of the day (optional)
        :param msAct: Middle School Common Time activity
        :param usAct: Upper School Common Time activity
        """
        self.date = date
        self.day_number = day_number
        self.is_wednesday = date.weekday() == 2
        self.is_open = is_open

        if self.is_open:
            if description_line_one:
                self.primary_description = primary_description
            else:
                self.primary_description = "Day " + str(self.day_number)
        else:
            self.primary_description = primary_description

        self.secondary_description = secondary_description

        # put the blocks in the right order
        day = self.day_number - 1
        blocks = BLOCKS[day::-1] + BLOCKS[-1:day + 1:-1]
        if len(blocks) == 7:
            blocks = blocks[:-1]

        if not self.is_wednesday:
            blocks.append("MS Electives/US Academic Help")
        blocks.insert(4, "US Lunch" + ("/MS " + ms_activity if ms_activity else ""))
        blocks.insert(4, "MS Lunch" + ("/US " + us_activity if us_activity else ""))
        blocks.insert(2, "Break")

        self.blocks = blocks

    def __str__(self):
        return str(self.date) + "(" + str(self.day_number) + ")"

    def __repr__(self):
        return str(self)

    def _get_time(self, block):
        times = TIMES if not self.is_wednesday else WED_TIMES
        start, end = times[block]
        start = datetime.datetime.combine(self.date, start)
        end = datetime.datetime.combine(self.date, end)
        return start, end

    @property
    def title1(self) -> Event:
        return Event(self.primary_description, self.date, self.date, True)

    @property
    def title2(self) -> Event:
        if self.secondary_description:
            return Event(self.secondary_description, self.date, self.date, False)
        return None

    def get_blocks(self) -> List[Event]:
        blocks = list()
        blocks.append(self.title1)
        if self.title2:
            blocks.append(self.title2)
        if not self.open:
            return blocks
        for block_num in range(10):
            if self.is_wednesday and block_num == 9:
                break
            block = Event(self.blocks[block_num], *self._get_time(block_num))
            blocks.append(block)
        return blocks


def getBlockTimesForDate(date: datetime.date, block: int) -> Tuple[datetime.time]:
    """get the start and end time of a block on a date

    :param date: the date of the event
    :param block: the block number

    :return: Length two, contains datetime.time objects
    """
    WED_TIMES = [  # block times (start, end) for Wednesday
        (datetime.time(8, 0), datetime.time(8, 45)),
        (datetime.time(8, 50), datetime.time(10)),
        (datetime.time(10, 0), datetime.time(10, 15)),
        (datetime.time(10, 15), datetime.time(11)),
        (datetime.time(11, 5), datetime.time(11, 45)),
        (datetime.time(11, 50), datetime.time(12, 20)),
        (datetime.time(12, 20), datetime.time(13)),
        (datetime.time(13), datetime.time(13, 45)),
        (datetime.time(13, 50), datetime.time(14, 35)),
        (None, None)
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
    return [WED_TIMES if date.weekday() == 2 else TIMES][block]


def block_rotation(day_number):
    letters = ["A", "B", "C", "D", "E", "F", "G"]
    return letters[7 - day_number + 1:] + letters[:7 - day_number]


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
                except IndexError as e:
                    continue

                day = RotationDay(date, number, is_open, *(row[5:]))
                for block in day.get_blocks():
                    writer.writerow(block.csv)


if __name__ == "__main__":
    print(str(Event('test', datetime.datetime.today(), datetime.datetime.today())))
    import sys
    sys.exit(0)
