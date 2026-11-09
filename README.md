# ACP Brevet Control Time Calculator

A web app that calculates the open and close times of the controls (checkpoints)
on an ACP-sanctioned brevet. It replaces the RUSA calculator at
https://rusa.org/octime_acp.html. Times fill in automatically as you type,
using Flask on the server and AJAX (jQuery) in the browser.

**Author:** Nigel Epperson
**Email:** epperson@uoregon.edu
**Repository:** https://github.com/neppsypepsi/proj4-brevets

---

## Using the calculator

1. Choose the brevet distance: 200, 300, 400, 600, or 1000 km.
2. Set the start date and time.
3. Type each control's distance in either **Km** or **Miles**, then press enter or
   click elsewhere. The other unit fills in, and the **Open** and **Close** times
   appear.
4. If you change the brevet distance or start date/time, every row that already
   has a distance is recalculated.
5. If a distance is invalid, the times are cleared and the reason appears in the
   **Notes** column.

---

## Control time rules (specification)

Each control has an **open time** and a **close time**. The open time is when
the fastest allowed rider could arrive. The close time is when the slowest
allowed rider would arrive. Both are calculated from the control's distance
along the route and then added to the brevet's start time.

These rules follow the ACP algorithm described at
https://rusa.org/pages/acp-brevet-control-times-calculator, with the unclear
points settled below. All results were checked against the official RUSA
calculator.

### 1. Speed table

| Control distance (km) | Minimum speed (km/h), used for **close** | Maximum speed (km/h), used for **open** |
|---|---|---|
| 0 – 200    | 15     | 34 |
| 200 – 400  | 15     | 32 |
| 400 – 600  | 15     | 30 |
| 600 – 1000 | 11.428 | 28 |

- **Open times use the maximum speed. Close times use the minimum speed.**
- The official table also has a 1000–1300 km row. It is not used, because
  brevets here are at most 1000 km, and controls past the finish are treated as
  the finish (rule 4).
- 11.428 is used exactly as published, not 80/7, so that results match the
  official calculator to the minute.

### 2. Speeds apply by segment

Each speed applies only to the part of the distance that falls inside its own
band, the way tax brackets work. The time for each segment is added up.

**Example: control at 350 km**

- Open: 200/34 + 150/32 = 5.882 + 4.688 = 10.570 h → **10H34**
  (using 32 km/h for the whole 350 km would wrongly give 10H56)
- Close: 350/15 = 23.333 h → **23H20**

**Example: control at 890 km on a 1000 km brevet**

- Open: 200/34 + 200/32 + 200/30 + 290/28 = 29.156 h → **29H09**
- Close: 600/15 + 290/11.428 = 40 + 25.376 = 65.376 h → **65H23**

### 3. Rounding

The total time in hours is converted to minutes and **rounded to the nearest
minute**, not truncated. For example, a control at 60 km opens after
60/34 = 1.7647 h = 105.88 min, which rounds to **1H46** (truncating would
give 1H45).

### 4. Controls at or past the finish

- A control **up to 20% past** the brevet distance is treated as being exactly
  at the brevet distance. For example, 205 km on a 200 km brevet gives the same
  times as 200 km.
- A control **more than 20% past** the brevet distance, or a negative distance,
  is rejected with an error.

### 5. Fixed finish close times

The close time at the finish (rule 4) does not come from the speed table. It is
a fixed limit for each brevet distance:

| Brevet | 200 km | 300 km | 400 km | 600 km | 1000 km |
|---|---|---|---|---|---|
| Finish close | 13H30 | 20H00 | 27H00 | 40H00 | 75H00 |

For example, 200/15 would give 13H20, but the official limit for a 200 km
brevet is **13H30**.

### 6. Start and early controls (first 60 km)

- The start control (0 km) opens at the start time.
- For controls from **0 to 60 km**, the close time is
  **distance / 20 km/h + 1 hour**. This is the ACP rule for early controls,
  and it keeps them from closing almost immediately. It also makes the start
  control close **1 hour** after the start.
  - 0 km → 1H00
  - 20 km → 2H00 (plain 15 km/h would give 1H20)
  - 60 km → 4H00
- Open times have no special rule here. They always use the speed table.

### Worked examples (start at 00:00)

| Brevet | Control | Open | Close | Rule shown |
|---|---|---|---|---|
| 200  | 0   | 0H00  | 1H00  | Start control |
| 200  | 20  | 0H35  | 2H00  | First 60 km |
| 200  | 60  | 1H46  | 4H00  | Rounding |
| 200  | 175 | 5H09  | 11H40 | Basic calculation |
| 200  | 205 | 5H53  | 13H30 | Overshoot + fixed finish |
| 400  | 350 | 10H34 | 23H20 | Segments |
| 600  | 205 | 6H02  | 13H40 | Same distance, not the finish |
| 600  | 550 | 17H08 | 36H40 | Segments |
| 1000 | 890 | 29H09 | 65H23 | 11.428 km/h past 600 km |
| 200  | 300 | —     | —     | Error: more than 20% past finish |

---

## Running the app

### With Docker (recommended)

From the `brevets` directory:

```bash
docker build -t brevets .
docker run --rm -p 5001:5000 brevets
```

Then open http://localhost:5001. The app listens on port 5000 inside the
container. Port 5001 is used on the host because macOS often reserves 5000 for
AirPlay Receiver.

### Locally

From the `brevets` directory:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python flask_brevets.py -P 5001
```

Add `-D` to turn on debug mode, which reloads templates and code when you save
changes.

---

## Running the tests

From the `brevets` directory:

```bash
nosetests -v
```

Or inside the Docker image:

```bash
docker run --rm --entrypoint nosetests brevets -v
```

The test suite (`brevets/test_acp_times.py`) uses the values from the worked
examples above. Each test is chosen to catch a specific wrong interpretation of
the rules: one speed for the whole distance instead of segments, truncating
instead of rounding, a missing fixed finish time, a missing 20% rule, the wrong
minimum speed past 600 km, and a missing start/first-60-km rule.

The project uses `pynose`, a maintained fork of `nose` that runs on current
Python versions and provides the same `nosetests` command.

---

## For developers

### Project layout

| File | Purpose |
|---|---|
| `brevets/acp_times.py` | Control time logic: `open_time()` and `close_time()` |
| `brevets/flask_brevets.py` | Flask server: serves the page and the `/_calc_times` AJAX endpoint |
| `brevets/templates/calc.html` | The page, plus the JavaScript that calls the server |
| `brevets/test_acp_times.py` | Nose test suite |
| `brevets/config.py` | Reads settings from `credentials.ini` and the command line |
| `brevets/Dockerfile` | Container build (Python 3.13) |

### `acp_times` interface

```python
open_time(control_dist_km, brevet_dist_km, brevet_start_time)
close_time(control_dist_km, brevet_dist_km, brevet_start_time)
```

- `control_dist_km`: number, the control's distance from the start in km
- `brevet_dist_km`: one of 200, 300, 400, 600, 1000
- `brevet_start_time`: ISO 8601 date-time string
- Returns an ISO 8601 string in the same time zone as the start time
- Raises `ValueError` for a negative distance or a control more than 20% past
  the brevet distance

### AJAX endpoint

`GET /_calc_times?km=60&brevet_dist_km=200&begin_date=2017-01-01&begin_time=00:00`

Success (200):

```json
{"result": {"open": "2017-01-01T01:46:00+00:00", "close": "2017-01-01T04:00:00+00:00"}}
```

Invalid input (400):

```json
{"error": "Control is more than 20% past the brevet distance"}
```

### Implementation notes

- The page displays times in the brevet's own time zone, not the browser's.
  The bundled moment.js (2.15.1) has a bug in `parseZone` with `+00:00`
  offsets, so the page uses `moment.utc(t).utcOffset(t)` instead.
- Without `-D`, Flask caches templates, so restart the server after editing
  `calc.html`.
