#!/usr/bin/env python3
"""
Creates the events for the Bell Schedule calendar for SSFS.
"""

from typing import Dict, List, Tuple

import argparse
import csv
import datetime


# academic blocks
BLOCKS: List[str] = ["A Block", "B Block", "C Block", "D Block", "E Block",
                     "F Block", "G Block"]

# block times (start, end) for Wednesday
WED_TIMES: List[Tuple[datetime.time, datetime.time]] = [
    (datetime.time(7, 55), datetime.time(8, 10)),    # MS Advisory / US AM help
    (datetime.time(8, 10), datetime.time(8, 55)),    # 1st block
    (datetime.time(9), datetime.time(10, 10)),       # 2nd block
    (datetime.time(10, 10), datetime.time(10, 25)),  # break
    (datetime.time(10, 25), datetime.time(11, 10)),  # 3rd block
    (datetime.time(11, 15), datetime.time(11, 55)),  # 4th block
    (datetime.time(12), datetime.time(12, 30)),      # MS Lunch / US Acad help
    (datetime.time(12, 30), datetime.time(13)),      # US Lunch / MS MFW
    (datetime.time(13, 5), datetime.time(13, 50)),   # 5th block
    (datetime.time(13, 55), datetime.time(14, 40))   # 6th block
]
# block times (start, end) for days that are not Wednesday
REG_TIMES: List[Tuple[datetime.time, datetime.time]] = [
    (datetime.time(7, 55), datetime.time(8, 10)),    # MS Advisory / US AM help
    (datetime.time(8, 10), datetime.time(9)),        # 1st block
    (datetime.time(9, 5), datetime.time(10, 15)),    # 2nd block
    (datetime.time(10, 15), datetime.time(10, 30)),  # break
    (datetime.time(10, 30), datetime.time(11, 20)),  # 3rd block
    (datetime.time(11, 25), datetime.time(12, 5)),   # 4th block
    (datetime.time(12, 10), datetime.time(12, 50)),  # MS Lunch
    (datetime.time(12, 50), datetime.time(13, 25)),  # US Lunch
    (datetime.time(13, 25), datetime.time(14, 15)),  # 5th block
    (datetime.time(14, 20), datetime.time(15, 10)),  # 6th block
    (datetime.time(15, 10), datetime.time(15, 40)),  # MS Sports / US Acad help
]


# Weekly MS Common Time activities
MS_ACTIVITIES: List[str] = ["Advisory", "Tutorial", "MFW", "Tutorial",
                            "Committees"]
# weekly US Common Time activities
US_ACTIVITIES: List[str] = ["Advisory", "MFW", "Academic Help",
                            "Activity Period", "MFW"]

FIELD_NAMES: List[str] = ["Subject", "Start Date", "Start Time", "End Date",
                          "End Time", "All Day Event"]


class RotationDay:
    """
    Creates a day of the block schedule calendar.

    You must provide a day_number, even if school is closed. I use the
    previous day's day number.
    """

    __slots__ = ("date", "day_number", "is_wednesday", "is_open",
                 "all_day_events", "blocks",)

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
        self.is_open: bool = is_open
        self.all_day_events: List[str] = list()

        # only add events that have titles
        for all_day_event in all_day_events:
            if all_day_event:
                self.all_day_events.append(all_day_event)

        weekday: int = self.date.weekday()
        self.is_wednesday: bool = weekday == 2

        # if we're open, add the "Day *N*" event
        if self.is_open:
            self.all_day_events.append("Day " + str(self.day_number))

        # get the rotation
        self.blocks: List[str] = self._get_block_rotation()

        # insert at the start
        self.blocks.insert(0, "MS Advisory | US Morning Help")

        # add at the end if not Wednesday (no electives/academic help on
        # Wednesdays)
        if not self.is_wednesday:
            self.blocks.append("MS Electives | US Academic Help")

        # Insert at lunch. US Lunch is after MS Lunch, but we'd have to fiddle
        # with the indices if we put MS Lunch in first.
        self.blocks.insert(5, "US Lunch | MS " + str(MS_ACTIVITIES[weekday]))
        self.blocks.insert(5, "MS Lunch | US " + str(US_ACTIVITIES[weekday]))
        self.blocks.insert(3, "Break")

    def __str__(self) -> str:
        return str(self.date) + "(" + str(self.day_number) + ")"

    def __repr__(self) -> str:
        string: str = "RotationDay(date={self.date:%Y-%m-%d}, "
        string += "day_number={self.day_number}, "
        string += "is_wednesday={self.is_wednesday}, is_open={self.is_open}, "
        string += "all_day_events:{self.all_day_events})"
        return string.format(self=self)

    def _get_block_rotation(self) -> List[str]:
        """Get the block rotation using day_number.

        >>> # all blocks
        >>> BLOCKS
        ['A Block', 'B Block', 'C Block', 'D Block', 'E Block', 'F Block', 'G Block']

        The example below gives the rotation for Day 1, dropping G Block. See
        the following article for an explanation of the slice notation:
        https://stackoverflow.com/a/509295/664950
        >>> # Day 1: drop G block
        >>> day = 0
        >>> BLOCKS[(6 - day) % 7 + 1:]
        []
        >>> BLOCKS[:(6 - day) % 7]
        ['A Block', 'B Block', 'C Block', 'D Block', 'E Block', 'F Block']
        >>> BLOCKS[(6 - day) % 7 + 1:] + BLOCKS[:(6 - day) % 7]
        ['A Block', 'B Block', 'C Block', 'D Block', 'E Block', 'F Block']

        This example gives the rotation for Day 2, dropping F Block.
        >>> # Day 2: drop F block
        >>> day = 1
        >>> BLOCKS[(6 - day) % 7 + 1:]
        ['G Block']
        >>> BLOCKS[:(6 - day) % 7]
        ['A Block', 'B Block', 'C Block', 'D Block', 'E Block']
        >>> BLOCKS[(6 - day) % 7 + 1:] + BLOCKS[:(6 - day) % 7]
        ['G Block', 'A Block', 'B Block', 'C Block', 'D Block', 'E Block']
        """

        # lists are 0-indexed, so decrease the day number by one
        day = self.day_number - 1
        # put the blocks in the right order (see docstring)
        return BLOCKS[(6 - day) % 7 + 1:] + BLOCKS[:(6 - day) % 7]

    def get_event_times(self, block_num: int) -> Tuple[datetime.datetime, datetime.datetime]:
        """Get the start and end times associated with this block_num"""
        # use the correct times depending on if it's wednesday or not
        times = REG_TIMES if not self.is_wednesday else WED_TIMES
        # get the actual values
        try:
            start, end = times[block_num]
        except:
            day = self.day_number - 1
            print("day - 1:", day)
            print("1st:", BLOCKS[day::-1])
            print("2nd:", BLOCKS[-1:day + 1:-1])
            raise
        # combine date and time into datetime
        start = datetime.datetime.combine(self.date, start)
        end = datetime.datetime.combine(self.date, end)
        return start, end

    def create_blocks(self) -> List[Dict[str, str]]:
        """Creates the events"""
        blocks = list()

        # create events for the all day events
        for all_day_event in self.all_day_events:
            # make sure the event is not None or the empty string
            if all_day_event:
                event = event_to_dict(all_day_event, self.date, self.date,
                                      True)
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
            block = event_to_dict(self.blocks[num], *self.get_event_times(num))
            # add the new event to the list
            blocks.append(block)

        return blocks


def event_to_dict(event_name: str, start: datetime.datetime,
                  end: datetime.datetime, all_day: bool = False) -> Dict[str, str]:
    """A helper class for exporting calendar events to a CSV file."""
    ret = dict()
    ret["Subject"] = str(event_name)
    ret["Start Date"] = str(start.date().strftime("%m/%d/%Y"))
    ret["Start Time"] = str(start.time().strftime("%I:%M %p"))
    ret["End Date"] = str(end.date().strftime("%m/%d/%Y"))
    ret["End Time"] = str(end.time().strftime("%I:%M %p"))
    ret["All Day Event"] = str(all_day)
    return ret


def _arg_parser() -> argparse.ArgumentParser:
    """Argument parser."""

    description = """Create a CSV file of events for the Middle School and
    Upper School's shared bell schedule, based on the standard rotation.
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input_file", help="See README for instructions")
    parser.add_argument("output_file", help="See README for instructions")
    return parser


def main():
    """Main func"""

    args = _arg_parser().parse_args()

    with open(args.input_file, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header row
        with open(args.output_file, "w", newline="") as csvout:
            writer = csv.DictWriter(csvout, FIELD_NAMES, quoting=csv.QUOTE_ALL)
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
                    writer.writerow(block)


if __name__ == "__main__":
    main()
