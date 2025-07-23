import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class CashFlow:
    amount: float
    party: str
    date: str

    def __str__(self):
        return f"{self.date} | {self.party} | {self.amount}"

@dataclass
class Project:
    name: str
    inflows: list[CashFlow] = field(default_factory=list)
    outflows: list[CashFlow] = field(default_factory=list)

    def total_in(self):
        return sum(f.amount for f in self.inflows)

    def total_out(self):
        return sum(f.amount for f in self.outflows)

    def net_return(self):
        return self.total_in() - self.total_out()

    def roi(self):
        total_out = self.total_out()
        return (self.net_return() / total_out * 100) if total_out else 0.0

class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Finance Project Evaluator")
        self.projects: list[Project] = []
        self.create_widgets()

    def create_widgets(self):
        self.project_list = tk.Listbox(self, height=6)
        self.project_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Project", command=self.add_project).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Open Project", command=self.open_project).pack(side=tk.LEFT, padx=5)

    def add_project(self):
        name = simpledialog.askstring("Project Name", "Enter project name:")
        if name:
            self.projects.append(Project(name=name))
            self.refresh_projects()

    def open_project(self):
        selection = self.project_list.curselection()
        if not selection:
            messagebox.showinfo("Info", "Select a project to open")
            return
        index = selection[0]
        project = self.projects[index]
        ProjectWindow(self, project)

    def refresh_projects(self):
        self.project_list.delete(0, tk.END)
        for proj in self.projects:
            self.project_list.insert(tk.END, proj.name)

class ProjectWindow(tk.Toplevel):
    def __init__(self, master, project: Project):
        super().__init__(master)
        self.project = project
        self.title(project.name)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text=f"Project: {self.project.name}").pack()
        flow_frame = tk.Frame(self)
        flow_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.inflow_list = tk.Listbox(flow_frame, height=8)
        self.outflow_list = tk.Listbox(flow_frame, height=8)
        tk.Label(flow_frame, text="Inflows").grid(row=0, column=0)
        tk.Label(flow_frame, text="Outflows").grid(row=0, column=1)
        self.inflow_list.grid(row=1, column=0, padx=5)
        self.outflow_list.grid(row=1, column=1, padx=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Inflow", command=self.add_inflow).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Add Outflow", command=self.add_outflow).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Report", command=self.show_report).pack(side=tk.LEFT, padx=5)
        self.refresh_lists()

    def add_inflow(self):
        self.add_flow(self.project.inflows, "Inflow Source")

    def add_outflow(self):
        self.add_flow(self.project.outflows, "Outflow Destination")

    def add_flow(self, flow_list, prompt):
        party = simpledialog.askstring(prompt, f"Enter {prompt.lower()}:")
        amount_str = simpledialog.askstring("Amount", "Enter amount:")
        date_str = simpledialog.askstring("Date", "Enter date (YYYY-MM-DD):", initialvalue=datetime.today().strftime("%Y-%m-%d"))
        if not party or not amount_str:
            return
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        flow_list.append(CashFlow(amount=amount, party=party, date=date_str))
        self.refresh_lists()

    def refresh_lists(self):
        self.inflow_list.delete(0, tk.END)
        self.outflow_list.delete(0, tk.END)
        for f in self.project.inflows:
            self.inflow_list.insert(tk.END, str(f))
        for f in self.project.outflows:
            self.outflow_list.insert(tk.END, str(f))

    def show_report(self):
        total_in = self.project.total_in()
        total_out = self.project.total_out()
        net = self.project.net_return()
        roi = self.project.roi()
        report = (f"Project: {self.project.name}\n"
                  f"Total Inflow: {total_in}\n"
                  f"Total Outflow: {total_out}\n"
                  f"Net Return: {net}\n"
                  f"ROI: {roi:.2f}%")
        messagebox.showinfo("Report", report)

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
