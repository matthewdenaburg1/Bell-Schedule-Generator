#!/usr/bin/env python3
"""
Creates the bell schedule calendar for SSFS
"""

from typing import Dict, List

import datetime
import csv

BLOCKS = ["A", "G", "F", "E", "D", "C", "B"]
BLOCKS = list(map(lambda a: a + " Block", BLOCKS))

WED_TIMES = [  # block times (start, end) for Wednesday
    (datetime.time(7, 55), datetime.time(8, 10)),    # MS Advisory / US morning help
    (datetime.time(8, 10), datetime.time(8, 55)),    # 1st block
    (datetime.time(9), datetime.time(10, 10)),       # 2nd block
    (datetime.time(10, 10), datetime.time(10, 25)),  # break
    (datetime.time(10, 25), datetime.time(11, 10)),  # 3rd block
    (datetime.time(11, 15), datetime.time(11, 55)),  # 4th block
    (datetime.time(12), datetime.time(12, 30)),      # MS Lunch / US Academic Help
    (datetime.time(12, 30), datetime.time(13)),      # US Lunch / MS MFW
    (datetime.time(13, 5), datetime.time(13, 50)),   # 5th block
    (datetime.time(13, 55), datetime.time(14, 40))   # 6th block
]
TIMES = [  # block times (start, end) for days that are not Wednesday
    (datetime.time(7, 55), datetime.time(8, 10)),    # MS Advisory / US morning help
    (datetime.time(8, 10), datetime.time(9)),        # 1st block
    (datetime.time(9, 5), datetime.time(10, 15)),    # 2nd block
    (datetime.time(10, 15), datetime.time(10, 30)),  # break
    (datetime.time(10, 30), datetime.time(11, 20)),  # 3rd block
    (datetime.time(11, 25), datetime.time(12, 5)),   # 4th block
    (datetime.time(12, 10), datetime.time(12, 50)),  # MS Lunch
    (datetime.time(12, 50), datetime.time(13, 25)),  # US Lunch
    (datetime.time(13, 25), datetime.time(14, 15)),  # 5th block
    (datetime.time(14, 20), datetime.time(15, 10)),  # 6th block
    (datetime.time(15, 10), datetime.time(15, 40)),  # MS Sports / US Academic Help
]


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
                 *all_day_events: List[str]):
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
        self.all_day_events: List[str] = list(all_day_events)

        if self.is_open:
            self.all_day_events.append("Day " + str(self.day_number))

        # put the blocks in the right order
        day = self.day_number - 1
        blocks = BLOCKS[day::-1] + BLOCKS[-1:day + 1:-1]
        if len(blocks) == 7:
            blocks = blocks[:-1]

        blocks.insert(0, "MS Advisory | US Morning Help")

        if not self.is_wednesday:
            blocks.append("MS Electives | US Academic Help")
        ms_activities = ["Advisory", "Tutorial", "MFW", "Tutorial", "Committees"]
        us_activities = ["Advisory", "MFW", "Academic Help", "Activity Period", "MFW"]
        # insert at lunch in reverse order
        blocks.insert(5, "US Lunch | MS " + ms_activities[self.date.weekday()])
        blocks.insert(5, "MS Lunch | US " + us_activities[self.date.weekday()])
        blocks.insert(3, "Break")

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

    def get_blocks(self) -> List[Event]:
        """get blocks"""
        blocks = list()
        for all_day_event in self.all_day_events:
            if all_day_event:
                event = Event(all_day_event, self.date, self.date, True)
                blocks.append(event)
        if not self.is_open:
            return blocks
        for block_num in range(len(self.blocks)):
            if self.is_wednesday and block_num == len(self.blocks):
                break
            block = Event(self.blocks[block_num], *self._get_time(block_num))
            blocks.append(block)
        return blocks


def main():
    """Main func"""
    with open("./data/2019-2020/2019-2020-input-test.csv", "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header row
        with open("./data/2019-2020/2019-2020-output2.csv", "w", newline="") as csvout:
            field_names = ["Subject", "Start Date", "Start Time", "End Date", "End Time",
                           "All Day Event"]

            writer = csv.DictWriter(csvout, field_names, dialect="excel")
            writer.writeheader()

            for row in reader:
                date = datetime.datetime.strptime(row[0], "%m/%d/%Y")
                # no weekends
                if date.weekday() >= 5:
                    continue
                is_open = row[1] == "TRUE"
                is_special = row[2] == "TRUE"
                try:
                    number = int(row[3])
                except IndexError as _:
                    continue

                is_open_val = is_open and not is_special
                day = RotationDay(date, number, is_open_val, *(row[4:]))
                for block in day.get_blocks():
                    writer.writerow(block.csv)


if __name__ == "__main__":
    main()
