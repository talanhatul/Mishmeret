import calendar
import random
from collections import defaultdict

# Assuming a fixed list of workers
workers = ['Alex Johnson', 'Maria Garcia', 'Michael Brown', 'Emily Wilson', 'Daniel Anderson',
            'Samantha Miller', 'Christopher Davis', 'Olivia Rodriguez', 'Ethan Martinez', 'Isabella Hernandez']

# Store unavailability as sets
unavailability = {worker: set() for worker in workers}

# Track shifts for each worker
shifts_count = {worker: {'Total': 0, 'Morning': 0, 'Evening': 0, 'Night': 0, 'Weekend': 0} for worker in workers}

# Define shift desirability weights
shift_desirability = {'Morning': 1, 'Evening': 1, 'Night': 1}


# Adjust desirability for specific shifts
shift_desirability['Wednesday Night'] = 2  # Example: Wednesday Night is highly desirable
shift_desirability['Sunday Evening'] = 2
shift_desirability['Sunday Night'] = 2
shift_desirability['Saturday Night'] = 1.5


shift_desirability['Thursday Evening'] = 0.5
shift_desirability['Thursday Night'] = 0.5
shift_desirability['Friday Morning'] = 0.5
shift_desirability['Friday Evening'] = 0.5
shift_desirability['Friday Night'] = 0.5
shift_desirability['Saturday Morning'] = 0.5
shift_desirability['Saturday Evening'] = 0.5
shift_desirability['Sunday Morning'] = 0.5  # Example: Sunday Morning is less desirable

def load_unavailability(filename):
    """Load worker unavailability from a file."""
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            name = parts[0].strip()
            dates = parts[1].split(',')
            for date in dates:
                date = date.strip()
                if name in unavailability:
                    unavailability[name].add(date)

def generate_schedule(year, month):
    """Generate the schedule for the month."""
    _, num_days = calendar.monthrange(year, month)
    num_shifts_per_worker = {'Morning': 0, 'Evening': 0, 'Night': 0}
    for shift in num_shifts_per_worker:
        num_shifts_per_worker[shift] = num_days * 2 if shift != 'Night' else num_days

    # Track Friday and Saturday shifts separately
    friday_shifts = defaultdict(int)
    saturday_shifts = defaultdict(int)

    schedule = {day: {'Morning': [], 'Evening': [], 'Night': []} for day in range(1, num_days + 1)}

    for day in range(1, num_days + 1):
        available_workers = {worker for worker in workers if can_work(worker, year, month, day, 'Morning')}
        available_workers.update({worker for worker in workers if can_work(worker, year, month, day, 'Evening')})
        available_workers.update({worker for worker in workers if can_work(worker, year, month, day, 'Night')})

        for shift in ['Morning', 'Evening', 'Night']:
            if calendar.weekday(year, month, day) in [calendar.FRIDAY, calendar.SATURDAY]:
                needed_workers = 1
            else:
                needed_workers = 2 if shift in ['Morning', 'Evening'] else 1
            
            shift_weight = shift_desirability.get(shift, 1)  # Get the desirability weight for the shift
            for _ in range(needed_workers):
                if not available_workers:  # In case there's not enough workers
                    print(f"Cannot fulfill shift {shift} on {year}-{month:02d}-{day:02d}. Not enough available workers.")
                    # Relax the constraint temporarily by removing the availability check
                    chosen_worker = random.choice(workers)
                else:
                    chosen_worker = min(available_workers, key=lambda x: shifts_count[x][shift])
                schedule[day][shift].append(chosen_worker)
                shifts_count[chosen_worker]['Total'] += 1
                shifts_count[chosen_worker][shift] += 1
                if chosen_worker in available_workers:
                    available_workers.remove(chosen_worker)  # Remove the worker only if they are in the set
                    if calendar.weekday(year, month, day) == calendar.FRIDAY:
                        friday_shifts[chosen_worker] += 1
                    elif calendar.weekday(year, month, day) == calendar.SATURDAY:
                        saturday_shifts[chosen_worker] += 1
    # If a worker works a night shift, mark them unavailable for all shifts on the next day
                if shift == 'Night':
                    next_day = day + 1 if day < num_days else 1
                    unavailability[chosen_worker].add(f"{year}-{month:02d}-{next_day:02d} Morning")
                    unavailability[chosen_worker].add(f"{year}-{month:02d}-{next_day:02d} Evening")
                    unavailability[chosen_worker].add(f"{year}-{month:02d}-{next_day:02d} Night")

    # Balance Friday and Saturday shifts
    min_shifts = min(min(friday_shifts.values()), min(saturday_shifts.values()))
    for worker in workers:
        extra_shifts_friday = friday_shifts[worker] - min_shifts
        extra_shifts_saturday = saturday_shifts[worker] - min_shifts
        if extra_shifts_friday > 0:
            # Remove extra Friday shifts
            for day in range(1, num_days + 1):
                if calendar.weekday(year, month, day) == calendar.FRIDAY and extra_shifts_friday > 0:
                    if 'Morning' in schedule[day] and worker in schedule[day]['Morning']:
                        schedule[day]['Morning'].remove(worker)
                        shifts_count[worker]['Morning'] -= 1
                        shifts_count[worker]['Total'] -= 1
                        extra_shifts_friday -= 1
                    elif 'Evening' in schedule[day] and worker in schedule[day]['Evening']:
                        schedule[day]['Evening'].remove(worker)
                        shifts_count[worker]['Evening'] -= 1
                        shifts_count[worker]['Total'] -= 1
                        extra_shifts_friday -= 1
                    elif 'Night' in schedule[day] and worker in schedule[day]['Night']:
                        schedule[day]['Night'].remove(worker)
                        shifts_count[worker]['Night'] -= 1
                        shifts_count[worker]['Total'] -= 1
                        extra_shifts_friday -= 1
        elif extra_shifts_saturday > 0:
            # Remove extra Saturday shifts
            for day in range(1, num_days + 1):
                if calendar.weekday(year, month, day) == calendar.SATURDAY and extra_shifts_saturday > 0:
                    if 'Morning' in schedule[day] and worker in schedule[day]['Morning']:
                        schedule[day]['Morning'].remove(worker)
                        shifts_count[worker]['Morning'] -= 1
                        shifts_count[worker]['Total'] -= 1
                        extra_shifts_saturday -= 1
                    elif 'Evening' in schedule[day] and worker in schedule[day]['Evening']:
                        schedule[day]['Evening'].remove(worker)
                        shifts_count[worker]['Evening'] -= 1
                        shifts_count[worker]['Total'] -= 1
                        extra_shifts_saturday -= 1
                    elif 'Night' in schedule[day] and worker in schedule[day]['Night']:
                        schedule[day]['Night'].remove(worker)
                        shifts_count[worker]['Night'] -= 1
                        shifts_count[worker]['Total'] -= 1
                        extra_shifts_saturday -= 1

    return schedule


def can_work(worker, year, month, day, shift):
    """Check if the worker can work on the given shift."""
    if f"{year}-{month:02d}-{day:02d} {shift}" in unavailability[worker]:
        return False
    if shift == 'Night':
        next_day = day + 1 if day < calendar.monthrange(year, month)[1] else 1
        if any(f"{year}-{month:02d}-{next_day:02d} {next_shift}" in unavailability[worker] for next_shift in ['Morning', 'Evening', 'Night']):
            return False
    # Check the last 6 days of work history to ensure the worker has had a day off within that period
    last_6_days = [f"{year}-{month:02d}-{d:02d}" for d in range(day-6, day) if d > 0]
    if all(any(f"{day} {s}" in unavailability[worker] for s in ['Morning', 'Evening', 'Night']) for day in last_6_days):
        return False
    return True


def print_schedule(schedule):
    """Print the schedule in a friendly format."""
    for day, shifts in schedule.items():
        print(f"Day {day}:")
        for shift, workers in shifts.items():
            print(f" {shift}: {', '.join(workers)}")
        print("")


def print_shift_counts(shifts_count, schedule):
    """Print the number of shifts for each worker."""
    print("Shift counts for each worker:")
    for worker, counts in shifts_count.items():
        total_shifts = 0
        weekend_shifts = 0
        for day, shifts in schedule.items():
            for shift, workers in shifts.items():
                if worker in workers:
                    total_shifts += 1
                    if calendar.weekday(year, month, day) in [calendar.FRIDAY, calendar.SATURDAY]:
                        weekend_shifts += 1
        print(f"{worker}: Total - {total_shifts}, Morning - {counts['Morning']}, Evening - {counts['Evening']}, Night - {counts['Night']}, Weekend - {weekend_shifts}")

# Example usage
filename = r"C:\Users\GH24089\Desktop\workers\workers.txt" # This should be your file with unavailability data
load_unavailability(filename)
year, month = 2024, 4 # Example year and month
schedule = generate_schedule(year, month)
print_schedule(schedule)
print_shift_counts(shifts_count, schedule)
