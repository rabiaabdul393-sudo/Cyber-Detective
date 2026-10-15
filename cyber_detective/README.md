# Cyber Detective — The Midnight Breach

A playable, dark-themed Python Tkinter digital-forensics mystery. No third-party Python packages required.

## Run

1. Install Python 3.10 or newer from https://www.python.org/downloads/ (on Windows, enable **Add Python to PATH**).
2. Extract the ZIP, open the `cyber_detective` folder in VS Code, and open a terminal.
3. Windows: `py main.py` (or `python main.py`). macOS/Linux: `python3 main.py`.
4. On Ubuntu/Debian, if Tkinter is missing: `sudo apt update && sudo apt install python3-tk`.

## How to play

- Open **Evidence Board**, select an evidence row, click **Discover Selected**.
- Click **Queue for Analysis** on discovered evidence.
- Open **Forensic Queue** and click **Process Next Analysis** (FIFO).
- Review suspects and their statements.
- Discover and analyze evidence **103**, **107**, and **108**; then accuse **Leo**.
- Save and load progress with the top-right buttons.

## Assessment mapping

| Requirement | Where |
| --- | --- |
| Lists | `Investigation.evidence`, `Detective.history`, search results |
| Dictionaries | `Investigation.evidence_by_id`, `suspects_by_name` |
| Tuples | `Evidence.timestamp` e.g. `(23, 47)` |
| Sets | `Detective.discovered`, `processed` |
| Linear search | `Investigation.linear_search` |
| Binary search | `Investigation.binary_search` (sorted ID lookup) |
| Bubble sort | `Investigation.bubble_sort_by_time` |
| Stack / LIFO | `Detective.history`, `Investigation.undo` |
| Queue / FIFO | `Detective.analysis_queue` using `collections.deque` |
| OOP | `Evidence`, `Suspect`, `Detective`, `Investigation`, `App` |
| Inheritance | `DigitalEvidence(Evidence)`, `App(tk.Tk)` |
| Objects | Instances of `DigitalEvidence`, `Suspect`, `Detective` |
| File handling | `Investigation.save/load` JSON |
| Exception handling | Input checks and save/load error handling |

## Notes

- The game is a fictional, offline simulation; no real systems are accessed.
- Save data is stored in `savegame.json` beside `main.py`.
- Binary search sorts a copy by ID before searching. Its search phase is O(log n); total lookup including sorting is O(n log n).
