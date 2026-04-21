import sys
import re
from collections import defaultdict


LOG_PATTERN = re.compile(
    r'(?P<time>\d{2}:\d{2}:\d{2})\s+'
    r'(?P<method>\w+)\s+'
    r'(?P<endpoint>\S+)\s+'
    r'(?P<status>\d{3})\s+'
    r'(?P<duration>[\d.]+)s'
)

TRACKED_ENDPOINTS = ['/api/products', '/api/orders']


def parse_log(lines):
    stats = defaultdict(lambda: {'durations': [], 'errors_500': 0})

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = LOG_PATTERN.match(line)
        if not match:
            continue

        endpoint = match.group('endpoint')
        status = int(match.group('status'))
        duration = float(match.group('duration'))

        if endpoint not in TRACKED_ENDPOINTS:
            continue

        stats[endpoint]['durations'].append(duration)

        if status == 500:
            stats[endpoint]['errors_500'] += 1

    return stats


def print_report(stats):
    for endpoint in TRACKED_ENDPOINTS:
        data = stats.get(endpoint)
        print(f"\n{endpoint}:")

        if not data or not data['durations']:
            print("  Нет данных")
            continue

        durations = data['durations']
        avg_duration = sum(durations) / len(durations)

        print(f"  Среднее время ответа: {avg_duration:.3f}s")
        print(f"  Количество запросов:  {len(durations)}")

        if endpoint == '/api/orders':
            print(f"  Ошибок 500:           {data['errors_500']}")


def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Ошибка: файл '{filename}' не найден", file=sys.stderr)
            sys.exit(1)
    else:
        lines = sys.stdin.readlines()

    stats = parse_log(lines)
    print_report(stats)


if __name__ == '__main__':
    main()
