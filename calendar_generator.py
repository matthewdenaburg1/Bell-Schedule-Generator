#!/usr/bin/env python3
"""
Creates the bell schedule calendar for SSFS
"""

from typing import Dict, List, Tuple

import csv
import datetime


BLOCKS: List[str] = list(map(lambda a: a + " Block",
                             ["A", "G", "F", "E", "D", "C", "B"]))

# block times (start, end) for Wednesday
WED_TIMES: List[Tuple[datetime.time, datetime.time]] = [
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
# block times (start, end) for days that are not Wednesday
TIMES: List[Tuple[datetime.time, datetime.time]] = [
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
        self.name: str = name
        self.start: datetime.datetime = start
        self.end: datetime.datetime = end
        self.all_day: bool = all_day

    def __str__(self) -> str:
        return "{self.name}: {self.start} - {self.end}".format(self=self)

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: "Event") -> bool:
        if other is None:
            return False
        if id(self) == id(other):
            return True
        if not isinstance(other, Event):
            return False
        if self.name != other.name or self.start != other.start or self.end != other.end:
            return False
        return True

    def to_csv(self) -> Dict[str, str]:
        """
        Creates a dict for csv.DictWriter

        return: a dict containing keys for a calendar event
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
    """
    Creates a day of the block schedule calendar.

    You must provide a day_number, even if school is closed. I use the
    previous day's day number.
    """

    def __init__(self, date: datetime.date, day_number: int, is_open: bool,
                 *all_day_events: List[str]):
        """
        Parameters:
        - date: the date of this RotationDay
        - day_number: the day's rotation number
        - is_open: true if school is open, or if there is a special event, like
                   Community Day
        - all_day_events: all day events, such as Community day or PSATs should
                          be listed here. Do not include "Day N"s
        """

        self.date: datetime.date = date
        self.day_number: int = day_number
        self.is_wednesday: bool = date.weekday() == 2
        self.is_open: bool = is_open
        self.all_day_events: List[str] = list(all_day_events)

        # if we're open, add the "Day *N*" event
        if self.is_open:
            self.all_day_events.append("Day " + str(self.day_number))

        # put the blocks in the right order
        day = self.day_number - 1
        # list[n:m:-1] === items from n (inclusive) to m (exclusive) in reverse order (-1)
        blocks = BLOCKS[day::-1] + BLOCKS[-1:day + 1:-1]
        if len(blocks) == 7:
            blocks = blocks[:-1]

        # insert at the start
        blocks.insert(0, "MS Advisory | US Morning Help")

        # add at the end if not wednesday (no electives/academic help on wednesdays)
        if not self.is_wednesday:
            blocks.append("MS Electives | US Academic Help")
        ms_activities = ["Advisory", "Tutorial", "MFW", "Tutorial", "Committees"]
        us_activities = ["Advisory", "MFW", "Academic Help", "Activity Period", "MFW"]

        # insert at lunch. US Lunch is after MS Lunch, but we'd have to fiddle
        # with the indices if it put MS lunch in first.
        blocks.insert(5, "US Lunch | MS " + ms_activities[self.date.weekday()])
        blocks.insert(5, "MS Lunch | US " + us_activities[self.date.weekday()])
        blocks.insert(3, "Break")

        self.blocks: List[str] = blocks

    def __str__(self) -> str:
        return str(self.date) + "(" + str(self.day_number) + ")"

    def __repr__(self) -> str:
        return str(self)

    def get_event_times(self, block_num: int) -> Tuple[datetime.datetime, datetime.datetime]:
        """Get the start and end times associated with this block"""
        times = TIMES if not self.is_wednesday else WED_TIMES
        start, end = times[block_num]
        start = datetime.datetime.combine(self.date, start)
        end = datetime.datetime.combine(self.date, end)
        return start, end

    def create_blocks(self) -> List[Event]:
        """Creates the events"""
        blocks = list()
        # create events for the all day events
        for all_day_event in self.all_day_events:
            # make sure the event is not None or the empty string
            if all_day_event:
                event = Event(all_day_event, self.date, self.date, True)
                blocks.append(event)
        # if school is not open, then there's no more events. We are done.
        if not self.is_open:
            return blocks
        # iterate through the events (the ones that are not all day)
        for num in range(len(self.blocks)):
            # if the date is wednesday, we do not want to add academic help
            if self.is_wednesday and num == len(self.blocks):
                break
            # create the event (block name, and expand `get_event_times`)
            block = Event(self.blocks[num], *self.get_event_times(num))
            # add the new event to the list
            blocks.append(block)
        return blocks


def main():
    """Main func"""
    with open("./data/2019-2020/2019-2020-input-test.csv", "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header row
        with open("./data/2019-2020/2019-2020-output2.csv", "w", newline="") as csvout:
            field_names = ["Subject", "Start Date", "Start Time", "End Date",
                           "End Time", "All Day Event"]

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
                except IndexError:
                    continue

                is_open_val = is_open and not is_special
                day = RotationDay(date, number, is_open_val, *(row[4:]))
                for block in day.create_blocks():
                    writer.writerow(block.to_csv())


if __name__ == "__main__":
    main()
