import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from event_history import build_events


class EventHistoryTests(unittest.TestCase):
    def test_full_history_retains_unknown_and_suspect_events(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fields = ['event_at', 'event_type', 'percentage_change', 'notes']
            with (root / 'change-events.csv').open('w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
                for index in range(300):
                    writer.writerow(dict(event_at='2026-10-17T00:00:00Z', event_type='custom_event'))
                writer.writerow(dict(event_at='2026-10-18T00:00:00Z', event_type='price_decrease', percentage_change='-95'))
            events = build_events(root, root / 'docs')
            payload = json.loads((root / 'docs/events-history.json').read_text())
            self.assertEqual(payload['total'], 301)
            self.assertEqual(len({event['id'] for event in events}), 301)
            self.assertEqual(events[0]['type'], 'price_decrease')
            self.assertTrue(events[0]['warning'])
            self.assertEqual(events[-1]['type'], 'custom_event')
            self.assertEqual(payload['events'], events)
