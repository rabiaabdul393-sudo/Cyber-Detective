"""Cyber Detective: The Midnight Breach — a self-contained Tkinter mystery game."""
import json
import tkinter as tk
from tkinter import messagebox, ttk
from collections import deque
from dataclasses import dataclass, asdict
from pathlib import Path

SAVE = Path(__file__).with_name('savegame.json')
BG, PANEL, PANEL2, FG, MUTED, ACCENT, GREEN, RED = '#0b1220','#152238','#1d304a','#e6f1ff','#91a9c4','#4cc9f0','#65e4ac','#ff6b82'

@dataclass(frozen=True)
class Evidence:
    code: int
    title: str
    timestamp: tuple
    description: str
    suspect: str
    clue: str

    @property
    def time_text(self):
        return f'{self.timestamp[0]:02d}:{self.timestamp[1]:02d}'

class DigitalEvidence(Evidence):
    def category(self):
        return 'Digital Forensics'

class Suspect:
    def __init__(self, name, role, statement):
        self.name, self.role, self.statement = name, role, statement

class Detective:
    def __init__(self, name='Agent Cipher'):
        self.name = name
        self.discovered = set()
        self.history = []  # stack, last-in first-out
        self.analysis_queue = deque()  # first-in first-out
        self.processed = set()
        self.attempts = 0

class Investigation:
    def __init__(self):
        self.detective = Detective()
        self.evidence = [
            DigitalEvidence(104,'VPN Login', (23, 47),'A remote login used a VPN token assigned to Maya. The token could have been stolen.', 'Maya', 'vpn'),
            DigitalEvidence(101,'Server Access Log',(23, 41),'An account named service_backup downloaded restricted files after hours.', 'Unknown', 'download'),
            DigitalEvidence(106,'Deleted Chat Fragment',(23, 55),'Message: “Use the maintenance window. I can cover the alerts.” Sent from an internal alias.', 'Unknown', 'chat'),
            DigitalEvidence(102,'Maintenance Roster',(22, 30),'Leo was assigned to monitor alerts during the scheduled maintenance window.', 'Leo', 'roster'),
            DigitalEvidence(105,'Keycard Log',(23, 38),'Noah entered the building, but the server-room door was never opened.', 'Noah', 'keycard'),
            DigitalEvidence(103,'Token Audit',(23, 44),'The VPN token was exported by the service_backup account; Maya did not initiate the export.', 'Unknown', 'token'),
            DigitalEvidence(107,'Admin Audit Trail',(23, 52),'Leo used his administrator account to disable security alerts for service_backup.', 'Leo', 'audit'),
            DigitalEvidence(108,'Backup Job Config',(23, 35),'The service_backup account was configured and controlled by Leo.', 'Leo', 'backup'),
        ]
        self.suspects = [
            Suspect('Maya','Network Engineer','My VPN token went missing. I reported it the next morning.'),
            Suspect('Leo','Systems Administrator','I was watching the dashboards all night. Nothing unusual happened.'),
            Suspect('Noah','IT Technician','I was in the building to replace a workstation, not access the servers.'),
            Suspect('Zara','Data Analyst','I left before maintenance started and had no administrator permissions.'),
        ]
        self.evidence_by_id = {item.code: item for item in self.evidence}  # dictionary
        self.suspects_by_name = {s.name: s for s in self.suspects}
        self.solved = False

    def discover(self, code):
        if code not in self.evidence_by_id:
            raise ValueError('Unknown evidence ID')
        if code in self.detective.discovered:
            return False
        self.detective.discovered.add(code)
        self.detective.history.append(code)
        return True

    def undo(self):
        if not self.detective.history:
            return None
        code = self.detective.history.pop()
        self.detective.discovered.remove(code)
        self.detective.processed.discard(code)
        self.detective.analysis_queue = deque(x for x in self.detective.analysis_queue if x != code)
        return self.evidence_by_id[code]

    def enqueue(self, code):
        if code not in self.detective.discovered:
            raise ValueError('Discover the evidence before requesting analysis.')
        if code in self.detective.processed or code in self.detective.analysis_queue:
            return False
        self.detective.analysis_queue.append(code)
        return True

    def process_next(self):
        if not self.detective.analysis_queue:
            return None
        code = self.detective.analysis_queue.popleft()
        self.detective.processed.add(code)
        return self.evidence_by_id[code]

    def linear_search(self, term):
        term = term.casefold().strip()
        return [e for e in self.evidence if term in e.title.casefold() or term in e.description.casefold() or term in str(e.code)]

    def binary_search(self, code):
        ordered = sorted(self.evidence, key=lambda e: e.code)
        lo, hi = 0, len(ordered) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if ordered[mid].code == code:
                return ordered[mid]
            if ordered[mid].code < code:
                lo = mid + 1
            else:
                hi = mid - 1
        return None

    def bubble_sort_by_time(self):
        ordered = self.evidence.copy()
        for i in range(len(ordered)):
            for j in range(len(ordered) - i - 1):
                if ordered[j].timestamp > ordered[j + 1].timestamp:
                    ordered[j], ordered[j + 1] = ordered[j + 1], ordered[j]
        return ordered

    def save(self):
        data = {'discovered': sorted(self.detective.discovered), 'history': self.detective.history,
                'queue': list(self.detective.analysis_queue), 'processed': sorted(self.detective.processed),
                'attempts': self.detective.attempts, 'solved': self.solved}
        SAVE.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def load(self):
        if not SAVE.exists():
            return False
        data = json.loads(SAVE.read_text(encoding='utf-8'))
        valid = set(self.evidence_by_id)
        history = data['history']
        discovered = set(data['discovered'])
        queue = data['queue']
        processed = set(data['processed'])
        if (not isinstance(history, list) or not isinstance(queue, list)
            or len(history) != len(set(history)) or set(history) != discovered
            or not discovered <= valid or not processed <= discovered
            or not set(queue) <= discovered or processed.intersection(queue)
            or len(queue) != len(set(queue))):
            raise ValueError('Save data is inconsistent')
        self.detective.discovered = discovered
        self.detective.history = history.copy()
        self.detective.analysis_queue = deque(queue)
        self.detective.processed = processed
        self.detective.attempts = max(0, int(data['attempts']))
        self.solved = bool(data['solved'])
        return True

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.case = Investigation()
        self.title('CYBER DETECTIVE | The Midnight Breach')
        self.geometry('1080x730')
        self.minsize(860, 620)
        self.configure(bg=BG)
        self._style()
        self._build()
        self.refresh()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Treeview', background=PANEL, foreground=FG, fieldbackground=PANEL, rowheight=32, borderwidth=0, font=('Consolas', 10))
        style.configure('Treeview.Heading', background=PANEL2, foreground=ACCENT, font=('Consolas', 10, 'bold'))
        style.map('Treeview', background=[('selected','#225875')], foreground=[('selected','#ffffff')])

    def label(self, parent, text, size=11, color=FG, bold=False, **kw):
        return tk.Label(parent, text=text, bg=kw.pop('bg', PANEL), fg=color,
                        font=('Consolas',size,'bold' if bold else 'normal'), **kw)

    def button(self, parent, text, command, bg=PANEL2):
        return tk.Button(parent, text=text, command=command, bg=bg, fg=FG,
                         activebackground='#276a86', activeforeground='white',
                         relief='flat', padx=12, pady=9, cursor='hand2', font=('Consolas',10,'bold'))

    def _build(self):
        top = tk.Frame(self, bg=BG, padx=22, pady=17)
        top.pack(fill='x')
        self.label(top,'◈  CYBER DETECTIVE',21,ACCENT,True,bg=BG).pack(side='left')
        self.status = self.label(top,'CASE #001  •  ACTIVE',10,GREEN,bg=BG)
        self.status.pack(side='right')
        subtitle = tk.Frame(self,bg=BG,padx=22)
        subtitle.pack(fill='x')
        self.label(subtitle,'THE MIDNIGHT BREACH  /  Trace the stolen files. Find the insider.',11,MUTED,bg=BG).pack(anchor='w')
        bar = tk.Frame(self,bg=BG,padx=22,pady=15)
        bar.pack(fill='x')
        for title, callback in [('Evidence Board',self.show_evidence),('Suspects',self.show_suspects),('Forensic Queue',self.show_queue),('Case Report',self.show_report)]:
            self.button(bar,title,callback).pack(side='left',padx=(0,7))
        self.button(bar,'Save',self.save).pack(side='right',padx=(7,0))
        self.button(bar,'Load',self.load).pack(side='right',padx=(7,0))
        self.button(bar,'New Case',self.reset).pack(side='right')
        self.content = tk.Frame(self,bg=PANEL,padx=18,pady=16)
        self.content.pack(fill='both',expand=True,padx=22,pady=(0,12))
        footer = tk.Frame(self,bg=BG,padx=22,pady=5)
        footer.pack(fill='x',side='bottom')
        self.progress = self.label(footer,'',10,MUTED,bg=BG)
        self.progress.pack(side='left')
        self.label(footer,'PYTHON • TKINTER • DATA STRUCTURES • ALGORITHMS',9,MUTED,bg=BG).pack(side='right')
        self.show_evidence()

    def clear(self, heading, sub=''):
        for child in self.content.winfo_children(): child.destroy()
        self.label(self.content,heading,17,ACCENT,True).pack(anchor='w',pady=(0,6))
        if sub: self.label(self.content,sub,10,MUTED,wraplength=850,justify='left').pack(anchor='w',pady=(0,13))

    def refresh(self):
        n = len(self.case.detective.discovered)
        self.progress.config(text=f'EVIDENCE DISCOVERED  {n}/{len(self.case.evidence)}    |    ANALYZED  {len(self.case.detective.processed)}    |    QUEUED  {len(self.case.detective.analysis_queue)}')
        self.status.config(text='CASE #001  •  SOLVED' if self.case.solved else 'CASE #001  •  ACTIVE', fg=GREEN)


    def show_evidence(self):
        self.clear(
            'EVIDENCE BOARD',
            'Select evidence to inspect it. Discover clues, then send them for forensic analysis.'
        )

        # Search and sorting tools
        tools = tk.Frame(self.content, bg=PANEL)
        tools.pack(fill='x', pady=(0, 10))

        self.query = tk.StringVar()

        entry = tk.Entry(
            tools,
            textvariable=self.query,
            bg=PANEL2,
            fg=FG,
            insertbackground=FG,
            relief='flat',
            font=('Consolas', 11),
            width=25
        )
        entry.pack(side='left', ipady=9, padx=(0, 8))

        self.button(
            tools, 'Linear Search', self.search_linear
        ).pack(side='left', padx=3)

        self.button(
            tools, 'Binary ID Search', self.search_binary
        ).pack(side='left', padx=3)

        self.button(
            tools, 'Bubble Sort: Time', self.sort_time
        ).pack(side='left', padx=3)

        # Action buttons: always visible
        controls = tk.Frame(self.content, bg=PANEL)
        controls.pack(side='bottom', fill='x', pady=(10, 0))

        self.button(
            controls,
            'Discover Selected',
            self.discover,
            bg='#175d69'
        ).pack(side='left', padx=(0, 8))

        self.button(
            controls,
            'Queue for Analysis',
            self.enqueue
        ).pack(side='left', padx=(0, 8))

        self.button(
            controls,
            'Undo Last Discovery',
            self.undo
        ).pack(side='left')

        # Evidence details: above action buttons
        detail_frame = tk.Frame(
            self.content,
            bg=PANEL2,
            padx=12,
            pady=10
        )
        detail_frame.pack(side='bottom', fill='x', pady=(10, 0))

        self.label(
            detail_frame,
            'EVIDENCE DETAILS',
            11,
            ACCENT,
            True,
            bg=PANEL2
        ).pack(anchor='w')

        self.detail = self.label(
            detail_frame,
            'Select an evidence row to inspect its description.',
            10,
            FG,
            wraplength=800,
            justify='left',
            bg=PANEL2
        )
        self.detail.pack(fill='x', pady=(5, 0))

        # Scrollable evidence table
        table_frame = tk.Frame(self.content, bg=PANEL)
        table_frame.pack(fill='both', expand=True)

        columns = ('id', 'time', 'title', 'status')

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            height=7
        )

        for col, width in [
            ('id', 65),
            ('time', 85),
            ('title', 400),
            ('status', 145)
        ]:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=width, anchor='w')

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient='vertical',
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(side='right', fill='y')
        self.tree.pack(
            side='left',
            fill='both',
            expand=True
        )

        # Selecting evidence shows its details
        self.tree.bind(
            '<<TreeviewSelect>>',
            lambda event: self.inspect()
        )

        # Double-click to inspect evidence
        self.tree.bind(
            '<Double-1>',
            lambda event: self.inspect()
        )

        self.populate(self.case.evidence)


    def populate(self, items):
        self.tree.delete(*self.tree.get_children())
        for e in items:
            status = 'ANALYZED' if e.code in self.case.detective.processed else ('DISCOVERED' if e.code in self.case.detective.discovered else 'UNEXAMINED')
            self.tree.insert('', 'end', iid=str(e.code),values=(e.code,e.time_text,e.title,status))
        self.refresh()

    def selected(self):
        ids = self.tree.selection()
        if not ids:
            messagebox.showinfo('Select evidence','Select an evidence row first.')
            return None
        return self.case.evidence_by_id[int(ids[0])]

    def inspect(self):
        ids = self.tree.selection()
        if ids:
            e = self.case.evidence_by_id[int(ids[0])]
            self.detail.config(text=f'[{e.code}] {e.description}')

    def discover(self):
        e = self.selected()
        if e:
            if self.case.discover(e.code): messagebox.showinfo('Evidence discovered',f'{e.title} added to your inventory.')
            else: messagebox.showinfo('Already discovered','This evidence is already in your inventory.')
            self.populate(self.case.evidence)

    def enqueue(self):
        e = self.selected()
        if e:
            try:
                if self.case.enqueue(e.code): messagebox.showinfo('Queued',f'{e.title} added to forensic analysis queue.')
                else: messagebox.showinfo('Already handled','Evidence already queued or analyzed.')
            except ValueError as exc: messagebox.showwarning('Cannot queue',str(exc))
            self.refresh()

    def undo(self):
        e = self.case.undo()
        messagebox.showinfo('Undo',f'Removed last discovery: {e.title}' if e else 'No discoveries to undo.')
        self.populate(self.case.evidence)

    def search_linear(self):
        self.populate(self.case.linear_search(self.query.get()))

    def search_binary(self):
        try: code = int(self.query.get().strip())
        except ValueError:
            messagebox.showwarning('Enter ID','Enter a numeric evidence ID, such as 107.')
            return
        result = self.case.binary_search(code)
        self.populate([result] if result else [])
        if not result: messagebox.showinfo('Not found','No evidence with that ID.')

    def sort_time(self):
        self.populate(self.case.bubble_sort_by_time())


    def show_suspects(self):
        self.clear(
            'SUSPECT DOSSIERS',
            'Interview suspects, compare their statements against the evidence, then submit your accusation.'
        )

        # Bottom accusation controls - always visible
        bottom = tk.Frame(self.content, bg=PANEL)
        bottom.pack(side='bottom', fill='x', pady=(12, 0))

        self.accused = tk.StringVar(
            value=self.case.suspects[0].name
        )

        self.label(
            bottom,
            'SELECT YOUR SUSPECT:',
            10,
            ACCENT,
            True
        ).pack(side='left', padx=(0, 10))

        suspect_dropdown = ttk.Combobox(
            bottom,
            textvariable=self.accused,
            values=[s.name for s in self.case.suspects],
            state='readonly',
            width=20
        )
        suspect_dropdown.pack(side='left', padx=(0, 12))

        self.button(
            bottom,
            'SUBMIT ACCUSATION',
            self.accuse,
            bg='#7d2d47'
        ).pack(side='left')

        # Scrollable suspect cards
        container = tk.Frame(self.content, bg=PANEL)
        container.pack(fill='both', expand=True)

        canvas = tk.Canvas(
            container,
            bg=PANEL,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            container,
            orient='vertical',
            command=canvas.yview
        )
        scroll_frame = tk.Frame(canvas, bg=PANEL)

        scroll_frame.bind(
            '<Configure>',
            lambda event: canvas.configure(
                scrollregion=canvas.bbox('all')
            )
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=scroll_frame,
            anchor='nw'
        )

        canvas.bind(
            '<Configure>',
            lambda event: canvas.itemconfigure(
                canvas_window,
                width=event.width
            )
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        # Display all four suspects
        for s in self.case.suspects:
            panel = tk.Frame(
                scroll_frame,
                bg=PANEL2,
                padx=15,
                pady=11
            )
            panel.pack(fill='x', pady=5)

            self.label(
                panel,
                f'{s.name.upper()}   /   {s.role}',
                12,
                ACCENT,
                True,
                bg=PANEL2
            ).pack(anchor='w')

            self.label(
                panel,
                '“' + s.statement + '”',
                10,
                FG,
                bg=PANEL2,
                wraplength=800,
                justify='left'
            ).pack(anchor='w', pady=(5, 0))

    def accuse(self):
        self.case.detective.attempts += 1
        if self.accused.get() == 'Leo' and {103,107,108} <= self.case.detective.processed:
            self.case.solved = True
            messagebox.showinfo('CASE SOLVED','Correct! Leo controlled the backup account, exported the token and disabled alerts. The digital audit trail proves the breach.')
        elif self.accused.get() == 'Leo':
            messagebox.showwarning('Insufficient proof','Your suspect is plausible, but you must DISCOVER and ANALYZE evidence #103, #107 and #108 before the case can be closed.')
        else:
            messagebox.showwarning('Wrong suspect','The evidence does not establish this suspect as the culprit. Review the logs and try again.')
        self.refresh()

    def show_queue(self):
        self.clear('FORENSIC ANALYSIS QUEUE','First-in, first-out (FIFO): evidence is processed in the order it was submitted.')
        queue = list(self.case.detective.analysis_queue)
        for i, code in enumerate(queue,1):
            self.label(self.content,f'{i:02d}  →  [{code}]  {self.case.evidence_by_id[code].title}',12).pack(anchor='w',pady=6)
        if not queue: self.label(self.content,'Queue is empty. Discover evidence and add it from the Evidence Board.',11,MUTED).pack(anchor='w',pady=15)
        self.button(self.content,'PROCESS NEXT ANALYSIS',self.process,bg='#175d69').pack(anchor='w',pady=18)
        self.label(self.content,'ANALYZED EVIDENCE',12,ACCENT,True).pack(anchor='w',pady=(15,6))
        for code in sorted(self.case.detective.processed):
            e = self.case.evidence_by_id[code]
            self.label(self.content,f'✓ [{code}] {e.title} — {e.description}',10,GREEN,wraplength=850,justify='left').pack(anchor='w',pady=4)

    def process(self):
        e = self.case.process_next()
        if e: messagebox.showinfo('Analysis complete',f'{e.title}\n\n{e.description}')
        else: messagebox.showinfo('Empty queue','No evidence waiting for analysis.')
        self.show_queue()
        self.refresh()

    def show_report(self):
        self.clear('INVESTIGATION REPORT','A live summary of the case and the data structures powering it.')
        d = self.case.detective
        lines = [f'Investigator: {d.name}',f'Case status: {"SOLVED" if self.case.solved else "ACTIVE"}',
                 f'Discovered evidence (set): {len(d.discovered)}/{len(self.case.evidence)}',
                 f'Analysis queue (deque): {list(d.analysis_queue)}',
                 f'Discovery history (stack): {d.history}',
                 f'Processed evidence (set): {sorted(d.processed)}',
                 f'Accusation attempts: {d.attempts}',
                 '', 'CASE OBJECTIVE:', 'Discover evidence #103, #107, #108; queue and process all three;',
                 'then use the Suspects tab to accuse the person responsible.',
                 '', 'ALGORITHMS:', 'Linear search scans all evidence (O(n)).',
                 'Binary search uses sorted IDs (O(log n) search after sorting).',
                 'Bubble sort orders timestamps (O(n²)).',
                 'Undo uses stack LIFO; analysis uses queue FIFO.']
        for line in lines:
            self.label(self.content,line,11,GREEN if line.startswith('Case status: SOLVED') else FG,wraplength=850,justify='left').pack(anchor='w',pady=3)

    def save(self):
        try:
            self.case.save()
            messagebox.showinfo('Saved',f'Progress saved to:\n{SAVE}')
        except OSError as exc: messagebox.showerror('Save error',str(exc))

    def load(self):
        try:
            if not self.case.load(): messagebox.showinfo('No save','No saved case found yet.')
            else: messagebox.showinfo('Loaded','Investigation progress restored.')
            self.show_evidence()
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            messagebox.showerror('Load error',f'Could not load saved data:\n{exc}')

    def reset(self):
        if messagebox.askyesno('New case','Start a new investigation? Unsaved progress will be lost.'):
            self.case = Investigation()
            self.show_evidence()

if __name__ == '__main__':
    app = App()
    app.mainloop()
