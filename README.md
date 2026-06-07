# UCSD Schedulizer

Turn your UCSD course list into a Google Calendar schedule in one command. Give it a quarter and the classes you're taking, and it fetches meeting times from UCSD's Schedule of Classes and writes an `.ics` file you can import into Google Calendar.

## Usage

Generate a calendar for Spring 2026:

```bash
ucsd-schedulizer "Spring Quarter 2026" "DSC 190, CSE 100" -o my_schedule.ics
```

Use a term code instead of the full name:

```bash
ucsd-schedulizer SP26 "DSC 190" --sections A00 -o dsc190.ics
```

Preview sections without writing a file:

```bash
ucsd-schedulizer SP26 "DSC 190" --dry-run
```

List supported quarters:

```bash
ucsd-schedulizer --list-terms FA25
```

### Options

| Flag | Description |
|------|-------------|
| `-o`, `--output` | Output `.ics` path (default: `schedule.ics`) |
| `--sections` | Comma-separated section codes to include, e.g. `A00,B01` |
| `--types` | Section types to include (default: `LE,DI,LA`) |
| `--dry-run` | Print found sections without writing a calendar |
| `--list-terms` | Show supported quarter codes and dates |

### Add to Google Calendar

1. Open [Google Calendar](https://calendar.google.com) → **Settings** → **Import & export** → **Import**
2. Select your `.ics` file
3. Choose which calendar to add events to

To share the schedule, create a dedicated calendar in Google Calendar, import the events there, then use **Settings → Share with specific people** or make the calendar public.

### Install

```bash
uv add "git+https://github.com/<your-username>/ucsd-schedulizer.git"
```

Or clone and run locally:

```bash
git clone https://github.com/<your-username>/ucsd-schedulizer.git
cd ucsd-schedulizer
uv sync
uv run ucsd-schedulizer SP26 "DSC 190" --dry-run
```
