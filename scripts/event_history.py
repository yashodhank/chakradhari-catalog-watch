"""Publish every recorded event without silently dropping uncertain observations."""
import csv
import json
from pathlib import Path


def build_events(data, docs):
    path = Path(data) / 'change-events.csv'
    events = []
    if path.exists():
        with path.open(encoding='utf-8-sig', newline='') as source:
            for index, row in enumerate(csv.DictReader(source)):
                try:
                    percent = float(row.get('percentage_change') or 'nan')
                except ValueError:
                    percent = float('nan')
                suspect = row.get('event_type') == 'price_decrease' and -99.5 <= percent <= -90 and not row.get('notes')
                events.append({
                    'id': index + 1, 'at': row.get('event_at', ''),
                    'type': row.get('event_type') or 'unknown',
                    'name': row.get('name_observed', ''), 'url': row.get('canonical_url', ''),
                    'old': row.get('old_value_observed', ''), 'new': row.get('new_value_observed', ''),
                    'percent': row.get('percentage_change', ''), 'notes': row.get('notes', ''),
                    'warning': 'Possible currency/localization artifact; verify with merchant.' if suspect else '',
                    'evidenceUrl': row.get('evidence_url', ''), 'runId': row.get('run_id', ''),
                })
    events.sort(key=lambda e: (e['at'], e['id']), reverse=True)
    Path(docs).mkdir(exist_ok=True, parents=True)
    (Path(docs) / 'events-history.json').write_text(
        json.dumps({'total': len(events), 'events': events}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    return events


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    print('Published', len(build_events(root / 'data', root / 'docs')), 'events')
