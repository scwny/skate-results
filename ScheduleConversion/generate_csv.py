#!/usr/bin/env python3
"""
generate_csv.py

Generate import-ready CSV files from a formatted text schedule.

Usage:
    python generate_csv.py SCHEDULE_FILE COMPETITION_NAME COMPETITION_DATE

    - SCHEDULE_FILE: path to the text schedule (e.g., "2025 Program Event List.txt")
    - COMPETITION_NAME: name of the competition (e.g., "Import Test")
    - COMPETITION_DATE: date of the competition in YYYY-MM-DD format (e.g., "2025-05-17")
"""

import argparse
import pandas as pd
import re
from datetime import datetime

def parse_schedule(file_path, competition_id):
    events = []
    clubs = {}
    skaters = {}
    scheduled = []

    current_event = None
    skater_order = 1

    with open(file_path, 'r') as f:
        lines = [l.rstrip('\n') for l in f]

    for line in lines:
        if line.startswith('#'):
            m = re.match(r'#(\d+)\s*-\s*(.*?)\s{2,}Rink\s+(\d+)\s{2,}(.*)', line)
            if m:
                ev_num    = int(m.group(1))
                ev_name   = m.group(2).strip()
                rink      = int(m.group(3))
                dt_text   = m.group(4).split(',', 1)[1].strip()
                dt_text   = re.sub(r'\s+', ' ', dt_text)
                dt        = datetime.strptime(dt_text, '%B %d %I:%M %p')
                events.append({
                    'id':             ev_num,
                    'competition_id': competition_id,
                    'eventNumber':    ev_num,
                    'name':           ev_name,
                    'date':           dt.date(),
                    'rink':           rink,
                    'time':           dt.time()
                })
                current_event = ev_num
                skater_order  = 1
            else:
                current_event = None
        elif current_event and line.strip():
            m2 = re.match(r'\s+(.*?)\s{2,}(.*)', line)
            if m2:
                fullname = m2.group(1).strip()
                club_raw = m2.group(2).strip()
                if club_raw.endswith('(Canada)'):
                    country   = 'CA'
                    club_name = club_raw[:-len('(Canada)')].strip()
                else:
                    country   = 'US'
                    club_name = club_raw
                if club_name not in clubs:
                    clubs[club_name] = {
                        'id':      len(clubs) + 1,
                        'name':    club_name,
                        'country': country
                    }
                club_id = clubs[club_name]['id']
                parts = fullname.split()
                first = ' '.join(parts[:-1])
                last  = parts[-1]
                sk_key = (first, last, club_id)
                if sk_key not in skaters:
                    skaters[sk_key] = {
                        'id':        len(skaters) + 1,
                        'firstName': first,
                        'lastName':  last,
                        'club_id':   club_id
                    }
                scheduled.append({
                    'event_id':    current_event,
                    'skater_id':   skaters[sk_key]['id'],
                    'orderNumber': skater_order
                })
                skater_order += 1

    events_df    = pd.DataFrame(events)
    clubs_df     = pd.DataFrame(list(clubs.values()))
    skaters_df   = pd.DataFrame(list(skaters.values()))
    scheduled_df = pd.DataFrame(scheduled)

    return events_df, clubs_df, skaters_df, scheduled_df

def main():
    parser = argparse.ArgumentParser(
        description="Generate CSV files for competitions, events, clubs, skaters, and scheduled skaters."
    )
    parser.add_argument("schedule_file",    help="Path to the text schedule file.")
    parser.add_argument("competition_name", help="Name of the competition.")
    parser.add_argument("competition_date", help="Date of the competition in YYYY-MM-DD format.")
    args = parser.parse_args()

    comp_date = datetime.strptime(args.competition_date, "%Y-%m-%d").date()
    comp_id   = 1

    events_df, clubs_df, skaters_df, scheduled_df = parse_schedule(args.schedule_file, comp_id)
    competition_df = pd.DataFrame([{
        'id':   comp_id,
        'name': args.competition_name,
        'date': comp_date
    }])

    competition_df.to_csv("competitions.csv", index=False)
    events_df.to_csv("events.csv",           index=False)
    clubs_df.to_csv("clubs.csv",             index=False)
    skaters_df.to_csv("skaters.csv",         index=False)
    scheduled_df.to_csv("scheduled_skaters.csv", index=False)

    print("CSV files generated: competitions.csv, events.csv, clubs.csv, skaters.csv, scheduled_skaters.csv")

if __name__ == "__main__":
    main()
