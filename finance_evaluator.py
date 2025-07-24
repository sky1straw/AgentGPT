import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
from dataclasses import dataclass, field
from datetime import datetime

import os
import mysql.connector

DB_CONFIG = {"host": "localhost", "user": os.getenv("MYSQL_USER", "root"), "password": os.getenv("MYSQL_PASSWORD", ""), "database": os.getenv("MYSQL_DB", "finance_evaluator")}

@dataclass
class CashFlow:
    amount: float
    party: str
    date: str

    id: int | None = None
    def __str__(self):
        return f"{self.date} | {self.party} | {self.amount}"

@dataclass
class Project:
    name: str
    project_id: int | None = None
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
        self.conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        self.init_db()
        self.projects: list[Project] = self.load_projects()
        self.create_widgets()

    def init_db(self):
        cur = self.conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        self.conn.database = DB_CONFIG["database"]
        cur.execute(
            """CREATE TABLE IF NOT EXISTS projects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS inflows (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT,
            amount DOUBLE,
            party VARCHAR(255),
            date VARCHAR(20)
        )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS outflows (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT,
            amount DOUBLE,
            party VARCHAR(255),
            date VARCHAR(20)
        )"""
        )
        self.conn.commit()
        cur.close()

    def load_projects(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM projects")
        projects = [Project(name=name, project_id=pid) for pid, name in cur.fetchall()]
        cur.close()
        return projects

    def create_widgets(self):
        self.project_list = tk.Listbox(self, height=6)
        self.project_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Project", command=self.add_project).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Open Project", command=self.open_project).pack(side=tk.LEFT, padx=5)
        self.refresh_projects()

    def add_project(self):
        name = simpledialog.askstring("Project Name", "Enter project name:")
        if name:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO projects (name) VALUES (%s)", (name,))
            self.conn.commit()
            pid = cur.lastrowid
            cur.close()
            self.projects.append(Project(name=name, project_id=pid))
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
        self.load_flows()
        self.create_widgets()

    def load_flows(self):
        cur = self.master.conn.cursor()
        cur.execute(
            "SELECT id, amount, party, date FROM inflows WHERE project_id=%s",
            (self.project.project_id,),
        )
        self.project.inflows = [
            CashFlow(amount=a, party=p, date=d, id=i) for i, a, p, d in cur.fetchall()
        ]
        cur.execute(
            "SELECT id, amount, party, date FROM outflows WHERE project_id=%s",
            (self.project.project_id,),
        )
        self.project.outflows = [
            CashFlow(amount=a, party=p, date=d, id=i) for i, a, p, d in cur.fetchall()
        ]
        cur.close()

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
        self.add_flow(self.project.inflows, "Inflow Source", "inflows")

    def add_outflow(self):
        self.add_flow(self.project.outflows, "Outflow Destination", "outflows")

    def add_flow(self, flow_list, prompt, table):
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
        cur = self.master.conn.cursor()
        cur.execute(
            f"INSERT INTO {table} (project_id, amount, party, date) VALUES (%s, %s, %s, %s)",
            (self.project.project_id, amount, party, date_str),
        )
        self.master.conn.commit()
        flow_id = cur.lastrowid
        cur.close()
        flow_list.append(CashFlow(amount=amount, party=party, date=date_str, id=flow_id))
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
