# UCSD Schedulizer

Turn your UCSD course list into a Google Calendar schedule in one command. Give it a quarter and the classes you're taking, and it fetches meeting times from UCSD's Schedule of Classes and writes a `schedule.ics` file you can import into Google Calendar.

## Usage

```bash
ucsd-schedulizer SP26 -c "MATH 20E, DSC 190"
```

For each class, if there are multiple professors or sections, the tool asks you to pick the one you want. When you're done, it writes `schedule.ics` in your current directory.

Browse sections by professor without building a calendar:

```bash
ucsd-schedulizer SP26 -c "MATH 20E, DSC 190" --list
```

List supported quarters:

```bash
ucsd-schedulizer --list-terms
```

### Add to Google Calendar

1. Open [Google Calendar](https://calendar.google.com) → **Settings** → **Import & export** → **Import**
2. Select `schedule.ics`
3. Choose which calendar to add events to

### Install

```bash
uv add "git+https://github.com/<your-username>/ucsd-schedulizer.git"
```

Or clone and run locally:

```bash
git clone https://github.com/<your-username>/ucsd-schedulizer.git
cd ucsd-schedulizer
uv sync
uv run ucsd-schedulizer SP26 -c "DSC 190"
```
