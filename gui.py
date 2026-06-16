import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

from PIL import Image, ImageTk

from Admin import Admin
from Customer import Customer
from Ride import Ride
from TaxiDriver import TaxiDriver
from charts import (
    chart_daily_rides,
    chart_driver_status,
    chart_monthly_rides,
    chart_revenue_by_driver,
    chart_rides_per_driver,
)
from data_store import (
    authenticate_user,
    data_to_objects,
    load_data,
    objects_to_data,
    save_data,
    username_exists,
)
from fare_calculator import calculate_fare, fare_breakdown
from reports import generate_management_report
from theme import COLORS, setup_styles
from validators import (
    validate_age,
    validate_distance,
    validate_mobile,
    validate_name,
    validate_password,
    validate_postcode,
    validate_username,
    validate_vehicle_type,
)

STATUS_COLORS = {
    TaxiDriver.STATUS_AVAILABLE: COLORS["stat_available"],
    TaxiDriver.STATUS_ON_RIDE: COLORS["stat_on_ride"],
    TaxiDriver.STATUS_OFFLINE: COLORS["stat_offline"],
}


class TaxiManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Taxi Management System")
        self.root.geometry("1100x720")
        self.root.minsize(950, 640)
        self.root.configure(bg=COLORS["bg"])

        self.style = ttk.Style(root)
        setup_styles(self.style)

        self.data = load_data()
        self.admin, self.drivers, self.customers, self.rides, self.completed, self.users = (
            data_to_objects(self.data)
        )
        self.next_ride_id = self.data.get("next_ride_id", 1)
        self.current_user = None
        self._chart_photo = None

        self._build_login()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _persist(self):
        self.data = objects_to_data(
            self.admin,
            self.drivers,
            self.customers,
            self.rides,
            self.completed,
            self.users,
            self.next_ride_id,
        )
        save_data(self.data)

    def _on_close(self):
        self._persist()
        self.root.destroy()

    def _clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _make_card(self, parent, **kwargs):
        frame = tk.Frame(
            parent,
            bg=COLORS["card"],
            highlightbackground=COLORS["card_border"],
            highlightthickness=1,
            **kwargs,
        )
        return frame

    # ---- Login & Registration ----
    def _build_login(self):
        self._clear_root()
        self.root.configure(bg=COLORS["login_gradient_top"])

        outer = tk.Frame(self.root, bg=COLORS["login_gradient_top"])
        outer.pack(fill="both", expand=True)

        tk.Label(
            outer,
            text="TAXI MANAGEMENT",
            font=("Segoe UI", 28, "bold"),
            fg=COLORS["accent"],
            bg=COLORS["login_gradient_top"],
        ).pack(pady=(40, 4))
        tk.Label(
            outer,
            text="Fleet control, rides & reports in one place",
            font=("Segoe UI", 11),
            fg="#a8b2d1",
            bg=COLORS["login_gradient_top"],
        ).pack(pady=(0, 30))

        card = self._make_card(outer, padx=40, pady=36)
        card.pack(padx=80, pady=20)

        self.auth_notebook = ttk.Notebook(card)
        self.auth_notebook.pack(fill="both", expand=True)

        login_tab = tk.Frame(self.auth_notebook, bg=COLORS["card"])
        register_tab = tk.Frame(self.auth_notebook, bg=COLORS["card"])
        self.auth_notebook.add(login_tab, text="  Login  ")
        self.auth_notebook.add(register_tab, text="  Register  ")

        self._build_login_form(login_tab)
        self._build_register_form(register_tab)

    def _build_login_form(self, parent):
        inner = tk.Frame(parent, bg=COLORS["card"], padx=30, pady=20)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text="Welcome back", font=("Segoe UI", 16, "bold"),
                 fg=COLORS["header"], bg=COLORS["card"]).grid(row=0, column=0, columnspan=2, pady=(0, 16))

        tk.Label(inner, text="Username", bg=COLORS["card"], fg=COLORS["text"]).grid(
            row=1, column=0, sticky="w", pady=6
        )
        self.login_user = ttk.Entry(inner, width=32, font=("Segoe UI", 11))
        self.login_user.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.login_user.insert(0, "admin")

        tk.Label(inner, text="Password", bg=COLORS["card"], fg=COLORS["text"]).grid(
            row=3, column=0, sticky="w", pady=6
        )
        self.login_pass = ttk.Entry(inner, width=32, show="*", font=("Segoe UI", 11))
        self.login_pass.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        self.login_pass.insert(0, "123")
        self.login_pass.bind("<Return>", lambda _: self._do_login())

        ttk.Button(inner, text="Sign In", style="Accent.TButton", command=self._do_login).grid(
            row=5, column=0, columnspan=2, pady=8, sticky="ew"
        )

    def _build_register_form(self, parent):
        inner = tk.Frame(parent, bg=COLORS["card"], padx=30, pady=20)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text="Create an account", font=("Segoe UI", 16, "bold"),
                 fg=COLORS["header"], bg=COLORS["card"]).grid(row=0, column=0, columnspan=2, pady=(0, 12))

        fields = [
            ("Full Name", "reg_name"),
            ("Username", "reg_user"),
            ("Password", "reg_pass"),
            ("Confirm Password", "reg_pass2"),
        ]
        self.reg_vars = {}
        for i, (label, key) in enumerate(fields, start=1):
            tk.Label(inner, text=label, bg=COLORS["card"], fg=COLORS["text"]).grid(
                row=i * 2 - 1, column=0, sticky="w", pady=4
            )
            show = "*" if "pass" in key else None
            entry = ttk.Entry(inner, width=32, show=show, font=("Segoe UI", 11))
            entry.grid(row=i * 2, column=0, columnspan=2, sticky="ew", pady=(0, 6))
            self.reg_vars[key] = entry

        tk.Label(
            inner,
            text="New accounts are registered as Staff members.",
            bg=COLORS["card"],
            fg=COLORS["text_muted"],
            font=("Segoe UI", 9),
        ).grid(row=10, column=0, columnspan=2, pady=(4, 12))

        ttk.Button(inner, text="Create Account", style="Primary.TButton", command=self._do_register).grid(
            row=11, column=0, columnspan=2, sticky="ew", pady=4
        )

    def _do_login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get()
        user = authenticate_user(self.users, username, password)
        if user:
            self.current_user = user
            self._build_main()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")

    def _do_register(self):
        name = self.reg_vars["reg_name"].get().strip()
        ok, full_name = validate_name(name, "Full name")
        if not ok:
            return messagebox.showerror("Validation", full_name)

        ok, username = validate_username(self.reg_vars["reg_user"].get())
        if not ok:
            return messagebox.showerror("Validation", username)

        if username_exists(self.users, username):
            return messagebox.showerror("Duplicate", "Username already taken.")

        password = self.reg_vars["reg_pass"].get()
        confirm = self.reg_vars["reg_pass2"].get()
        if password != confirm:
            return messagebox.showerror("Validation", "Passwords do not match.")

        ok, password = validate_password(password)
        if not ok:
            return messagebox.showerror("Validation", password)

        self.users.append(
            {
                "username": username,
                "password": password,
                "role": "staff",
                "full_name": full_name,
                "address": "",
            }
        )
        self._persist()
        messagebox.showinfo("Registered", f"Account '{username}' created! You can now sign in.")
        self.auth_notebook.select(0)
        self.login_user.delete(0, tk.END)
        self.login_user.insert(0, username)
        self.login_pass.delete(0, tk.END)
        self.login_pass.focus()

    # ---- Main dashboard ----
    def _build_main(self):
        self._clear_root()
        self.root.configure(bg=COLORS["bg"])

        header = tk.Frame(self.root, bg=COLORS["header"], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Taxi Management Dashboard",
            font=("Segoe UI", 18, "bold"),
            fg=COLORS["accent"],
            bg=COLORS["header"],
        ).pack(side="left", padx=20, pady=18)

        role_label = "Admin" if self.current_user.get("role") == "admin" else "Staff"
        tk.Label(
            header,
            text=f"{self.current_user.get('full_name', 'User')}  ({role_label})",
            font=("Segoe UI", 10),
            fg="#a8b2d1",
            bg=COLORS["header"],
        ).pack(side="right", padx=(0, 12), pady=18)

        ttk.Button(header, text="Save", style="Success.TButton", command=self._save_clicked).pack(
            side="right", padx=4, pady=18
        )
        ttk.Button(header, text="Logout", style="Info.TButton", command=self._logout).pack(
            side="right", padx=8, pady=18
        )

        stats = tk.Frame(self.root, bg=COLORS["bg"], padx=16, pady=12)
        stats.pack(fill="x")
        self._stat_cards = {}
        for key, title, color in [
            ("drivers", "Drivers", COLORS["info"]),
            ("customers", "Customers", COLORS["primary"]),
            ("rides", "Total Rides", COLORS["success"]),
            ("available", "Available", COLORS["stat_available"]),
        ]:
            card = tk.Frame(stats, bg=color, padx=20, pady=14)
            card.pack(side="left", fill="x", expand=True, padx=6)
            tk.Label(card, text=title, font=("Segoe UI", 9), fg="white", bg=color).pack(anchor="w")
            val = tk.Label(card, text="0", font=("Segoe UI", 22, "bold"), fg="white", bg=color)
            val.pack(anchor="w")
            self._stat_cards[key] = val

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self._tab_drivers()
        self._tab_customers()
        self._tab_assign()
        self._tab_complete_ride()
        self._tab_reports()
        self._tab_charts()
        if self.current_user.get("role") == "admin":
            self._tab_admin()

        self._refresh_all()

    def _logout(self):
        self.current_user = None
        self._build_login()

    def _update_stat_cards(self):
        if not hasattr(self, "_stat_cards"):
            return
        avail = sum(1 for d in self.drivers if d.get_status() == TaxiDriver.STATUS_AVAILABLE)
        self._stat_cards["drivers"].config(text=str(len(self.drivers)))
        self._stat_cards["customers"].config(text=str(len(self.customers)))
        self._stat_cards["rides"].config(text=str(len(self.rides)))
        self._stat_cards["available"].config(text=str(avail))

    def _save_clicked(self):
        self._persist()
        messagebox.showinfo("Saved", "Data saved to data.json successfully.")

    def _refresh_all(self):
        self._refresh_drivers()
        self._refresh_customers()
        self._refresh_completed()
        self._refresh_rides_history()
        self._update_status_summary()
        self._update_stat_cards()

    # ---- Drivers tab ----
    def _tab_drivers(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  Drivers  ")

        form = ttk.LabelFrame(tab, text="Register / Update Driver", padding=12)
        form.pack(fill="x", pady=(0, 10))

        fields = [
            ("First Name", "drv_first"),
            ("Surname", "drv_surname"),
            ("Vehicle Type", "drv_vehicle"),
            ("Status", "drv_status"),
        ]
        self.drv_vars = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form, text=label + ":", style="Card.TLabel").grid(
                row=i // 2, column=(i % 2) * 2, sticky="e", padx=5, pady=4
            )
            if key == "drv_status":
                var = tk.StringVar(value=TaxiDriver.STATUS_AVAILABLE)
                cb = ttk.Combobox(
                    form, textvariable=var,
                    values=[TaxiDriver.STATUS_AVAILABLE, TaxiDriver.STATUS_ON_RIDE, TaxiDriver.STATUS_OFFLINE],
                    state="readonly", width=22,
                )
                cb.grid(row=i // 2, column=(i % 2) * 2 + 1, sticky="w", pady=4)
            else:
                var = tk.StringVar()
                ttk.Entry(form, textvariable=var, width=25).grid(
                    row=i // 2, column=(i % 2) * 2 + 1, sticky="w", pady=4
                )
            self.drv_vars[key] = var

        ttk.Label(form, text="Sedan, SUV, Van, Estate, Minibus", style="Muted.TLabel").grid(
            row=2, column=2, columnspan=2, sticky="w", padx=5
        )

        btn_row = ttk.Frame(form)
        btn_row.grid(row=3, column=0, columnspan=4, pady=10)
        ttk.Button(btn_row, text="Register", style="Success.TButton", command=self._register_driver).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Update", style="Accent.TButton", command=self._update_driver).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Delete", style="Primary.TButton", command=self._delete_driver).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Clear", command=self._clear_driver_form).pack(side="left", padx=4)

        list_frame = ttk.LabelFrame(tab, text="Driver List", padding=10)
        list_frame.pack(fill="both", expand=True)

        cols = ("id", "name", "vehicle", "status")
        self.driver_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        for c, t, w in [("id", "ID", 45), ("name", "Full Name", 200), ("vehicle", "Vehicle", 120), ("status", "Status", 120)]:
            self.driver_tree.heading(c, text=t)
            self.driver_tree.column(c, width=w)
        self.driver_tree.pack(fill="both", expand=True, side="left")
        self.driver_tree.bind("<<TreeviewSelect>>", self._on_driver_select)

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.driver_tree.yview)
        sb.pack(side="right", fill="y")
        self.driver_tree.configure(yscrollcommand=sb.set)

        self.driver_tree.tag_configure("available", foreground=STATUS_COLORS[TaxiDriver.STATUS_AVAILABLE])
        self.driver_tree.tag_configure("on_ride", foreground=STATUS_COLORS[TaxiDriver.STATUS_ON_RIDE])
        self.driver_tree.tag_configure("offline", foreground=STATUS_COLORS[TaxiDriver.STATUS_OFFLINE])

        status_bar = tk.Frame(tab, bg=COLORS["bg"])
        status_bar.pack(fill="x", pady=8)
        self.status_summary = tk.Label(status_bar, text="", font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["text"])
        self.status_summary.pack(anchor="w")
        for status, color in STATUS_COLORS.items():
            tk.Label(status_bar, text=f"● {status}", fg=color, bg=COLORS["bg"], font=("Segoe UI", 9, "bold")).pack(side="left", padx=10)

    def _status_tag(self, status):
        return {"Available": "available", "On Ride": "on_ride", "Offline": "offline"}.get(status, "offline")

    def _refresh_drivers(self):
        if not hasattr(self, "driver_tree"):
            return
        for item in self.driver_tree.get_children():
            self.driver_tree.delete(item)
        for i, d in enumerate(self.drivers):
            self.driver_tree.insert(
                "", "end", iid=str(i),
                values=(i + 1, d.full_name(), d.get_vehicle_type(), d.get_status()),
                tags=(self._status_tag(d.get_status()),),
            )
        self._update_status_summary()

    def _update_status_summary(self):
        if not hasattr(self, "status_summary"):
            return
        avail = sum(1 for d in self.drivers if d.get_status() == TaxiDriver.STATUS_AVAILABLE)
        on_ride = sum(1 for d in self.drivers if d.get_status() == TaxiDriver.STATUS_ON_RIDE)
        offline = sum(1 for d in self.drivers if d.get_status() == TaxiDriver.STATUS_OFFLINE)
        self.status_summary.config(
            text=f"Driver Status Summary — Available: {avail}  |  On Ride: {on_ride}  |  Offline: {offline}"
        )

    def _on_driver_select(self, _event=None):
        sel = self.driver_tree.selection()
        if not sel:
            return
        d = self.drivers[int(sel[0])]
        self.drv_vars["drv_first"].set(d.get_first_name())
        self.drv_vars["drv_surname"].set(d.get_surname())
        self.drv_vars["drv_vehicle"].set(d.get_vehicle_type())
        self.drv_vars["drv_status"].set(d.get_status())

    def _clear_driver_form(self):
        for k in self.drv_vars:
            self.drv_vars[k].set("" if k != "drv_status" else TaxiDriver.STATUS_AVAILABLE)
        self.driver_tree.selection_remove(self.driver_tree.selection())

    def _register_driver(self):
        ok, first = validate_name(self.drv_vars["drv_first"].get(), "First name")
        if not ok:
            return messagebox.showerror("Validation", first)
        ok, surname = validate_name(self.drv_vars["drv_surname"].get(), "Surname")
        if not ok:
            return messagebox.showerror("Validation", surname)
        ok, vehicle = validate_vehicle_type(self.drv_vars["drv_vehicle"].get())
        if not ok:
            return messagebox.showerror("Validation", vehicle)
        for d in self.drivers:
            if d.get_first_name() == first and d.get_surname() == surname:
                return messagebox.showerror("Duplicate", "A driver with this name already exists.")
        self.drivers.append(TaxiDriver(first, surname, vehicle, self.drv_vars["drv_status"].get()))
        self._refresh_all()
        self._clear_driver_form()
        messagebox.showinfo("Success", "Driver registered.")

    def _update_driver(self):
        sel = self.driver_tree.selection()
        if not sel:
            return messagebox.showwarning("Select", "Select a driver to update.")
        idx = int(sel[0])
        ok, first = validate_name(self.drv_vars["drv_first"].get(), "First name")
        if not ok:
            return messagebox.showerror("Validation", first)
        ok, surname = validate_name(self.drv_vars["drv_surname"].get(), "Surname")
        if not ok:
            return messagebox.showerror("Validation", surname)
        ok, vehicle = validate_vehicle_type(self.drv_vars["drv_vehicle"].get())
        if not ok:
            return messagebox.showerror("Validation", vehicle)
        d = self.drivers[idx]
        d.set_first_name(first)
        d.set_surname(surname)
        d.set_vehicle_type(vehicle)
        d.set_status(self.drv_vars["drv_status"].get())
        self._refresh_all()
        messagebox.showinfo("Success", "Driver updated.")

    def _delete_driver(self):
        sel = self.driver_tree.selection()
        if not sel:
            return messagebox.showwarning("Select", "Select a driver to delete.")
        if messagebox.askyesno("Confirm", "Delete selected driver?"):
            self.drivers.pop(int(sel[0]))
            self._refresh_all()
            self._clear_driver_form()

    # ---- Customers tab with registration ----
    def _tab_customers(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  Customers  ")

        form = ttk.LabelFrame(tab, text="Register New Customer", padding=12)
        form.pack(fill="x", pady=(0, 10))

        self.cust_vars = {}
        fields = [("First Name", "c_first"), ("Surname", "c_surname"), ("Age", "c_age"),
                  ("Mobile", "c_mobile"), ("Postcode", "c_postcode")]
        for i, (label, key) in enumerate(fields):
            ttk.Label(form, text=label + ":").grid(row=i // 3, column=(i % 3) * 2, sticky="e", padx=5, pady=4)
            var = tk.StringVar()
            ttk.Entry(form, textvariable=var, width=18).grid(row=i // 3, column=(i % 3) * 2 + 1, sticky="w", pady=4)
            self.cust_vars[key] = var

        btn_row = ttk.Frame(form)
        btn_row.grid(row=2, column=0, columnspan=6, pady=10)
        ttk.Button(btn_row, text="Register Customer", style="Success.TButton", command=self._register_customer).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Clear Form", command=self._clear_customer_form).pack(side="left", padx=4)

        ttk.Label(tab, text="Active Customers", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(4, 4))
        cols = ("id", "name", "driver", "age", "mobile", "postcode")
        self.customer_tree = ttk.Treeview(tab, columns=cols, show="headings", height=8)
        for c, t, w in [("id", "ID", 40), ("name", "Full Name", 180), ("driver", "Driver", 150),
                        ("age", "Age", 50), ("mobile", "Mobile", 120), ("postcode", "Postcode", 90)]:
            self.customer_tree.heading(c, text=t)
            self.customer_tree.column(c, width=w)
        self.customer_tree.pack(fill="both", expand=True)

        ttk.Label(tab, text="Completed Customers", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(12, 4))
        cols2 = ("id", "name", "age", "mobile", "postcode")
        self.completed_tree = ttk.Treeview(tab, columns=cols2, show="headings", height=5)
        for c, t, w in [("id", "ID", 40), ("name", "Full Name", 200), ("age", "Age", 50),
                        ("mobile", "Mobile", 120), ("postcode", "Postcode", 90)]:
            self.completed_tree.heading(c, text=t)
            self.completed_tree.column(c, width=w)
        self.completed_tree.pack(fill="both", expand=True)

    def _clear_customer_form(self):
        for var in self.cust_vars.values():
            var.set("")

    def _register_customer(self):
        ok, first = validate_name(self.cust_vars["c_first"].get(), "First name")
        if not ok:
            return messagebox.showerror("Validation", first)
        ok, surname = validate_name(self.cust_vars["c_surname"].get(), "Surname")
        if not ok:
            return messagebox.showerror("Validation", surname)
        ok, age = validate_age(self.cust_vars["c_age"].get())
        if not ok:
            return messagebox.showerror("Validation", age)
        ok, mobile = validate_mobile(self.cust_vars["c_mobile"].get())
        if not ok:
            return messagebox.showerror("Validation", mobile)
        ok, postcode = validate_postcode(self.cust_vars["c_postcode"].get())
        if not ok:
            return messagebox.showerror("Validation", postcode)

        for c in self.customers:
            if c.get_mobile() == mobile:
                return messagebox.showerror("Duplicate", "A customer with this mobile already exists.")

        self.customers.append(Customer(first, surname, age, mobile, postcode))
        self._refresh_all()
        self._clear_customer_form()
        messagebox.showinfo("Success", f"Customer {first} {surname} registered.")

    def _refresh_customers(self):
        if not hasattr(self, "customer_tree"):
            return
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        for i, c in enumerate(self.customers):
            self.customer_tree.insert("", "end", values=(
                i + 1, c.full_name(), c.get_taxi_driver(), c.get_age(), c.get_mobile(), c.get_postcode(),
            ))

    def _refresh_completed(self):
        if not hasattr(self, "completed_tree"):
            return
        for item in self.completed_tree.get_children():
            self.completed_tree.delete(item)
        for i, c in enumerate(self.completed):
            self.completed_tree.insert("", "end", values=(
                i + 1, c.full_name(), c.get_age(), c.get_mobile(), c.get_postcode(),
            ))

    # ---- Assign tab ----
    def _tab_assign(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  Assign Driver  ")

        card = self._make_card(tab, padx=20, pady=20)
        card.pack(fill="x")

        inner = tk.Frame(card, bg=COLORS["card"], padx=16, pady=16)
        inner.pack(fill="x")

        tk.Label(inner, text="Assign an available driver to a customer", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["card"], fg=COLORS["header"]).pack(anchor="w", pady=(0, 12))

        row = tk.Frame(inner, bg=COLORS["card"])
        row.pack(fill="x")
        tk.Label(row, text="Customer ID:", bg=COLORS["card"]).pack(side="left", padx=5)
        self.assign_customer_id = ttk.Entry(row, width=8)
        self.assign_customer_id.pack(side="left")
        tk.Label(row, text="Driver ID:", bg=COLORS["card"]).pack(side="left", padx=(20, 5))
        self.assign_driver_id = ttk.Entry(row, width=8)
        self.assign_driver_id.pack(side="left")
        ttk.Button(row, text="Assign", style="Accent.TButton", command=self._assign_driver).pack(side="left", padx=15)
        ttk.Button(row, text="Refresh", command=self._refresh_all).pack(side="left")

        tk.Label(inner, text="Only Available drivers can be assigned. Status changes to On Ride.",
                 bg=COLORS["card"], fg=COLORS["text_muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(10, 0))

    def _assign_driver(self):
        try:
            c_idx = int(self.assign_customer_id.get()) - 1
            d_idx = int(self.assign_driver_id.get()) - 1
        except ValueError:
            return messagebox.showerror("Validation", "Enter valid numeric IDs.")
        if c_idx not in range(len(self.customers)):
            return messagebox.showerror("Error", "Invalid customer ID.")
        if d_idx not in range(len(self.drivers)):
            return messagebox.showerror("Error", "Invalid driver ID.")
        driver = self.drivers[d_idx]
        if driver.get_status() != TaxiDriver.STATUS_AVAILABLE:
            return messagebox.showerror("Unavailable", f"Driver is '{driver.get_status()}'.")
        customer = self.customers[c_idx]
        customer.link(driver.full_name())
        driver.add_customer(customer)
        driver.set_status(TaxiDriver.STATUS_ON_RIDE)
        self._refresh_all()
        messagebox.showinfo("Assigned", f"{driver.full_name()} assigned to {customer.full_name()}.")

    # ---- Complete ride tab ----
    def _tab_complete_ride(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  Complete Ride  ")

        card = self._make_card(tab, padx=16, pady=12)
        card.pack(fill="x", pady=(0, 10))
        inner = tk.Frame(card, bg=COLORS["card"], padx=16, pady=14)
        inner.pack(fill="x")

        row = tk.Frame(inner, bg=COLORS["card"])
        row.pack(fill="x")
        tk.Label(row, text="Customer ID:", bg=COLORS["card"]).pack(side="left", padx=5)
        self.ride_customer_id = ttk.Entry(row, width=8)
        self.ride_customer_id.pack(side="left")
        tk.Label(row, text="Distance (km):", bg=COLORS["card"]).pack(side="left", padx=(20, 5))
        self.ride_distance = ttk.Entry(row, width=10)
        self.ride_distance.pack(side="left")
        ttk.Button(row, text="Calculate Fare", style="Info.TButton", command=self._calc_fare_preview).pack(side="left", padx=10)
        ttk.Button(row, text="Complete Ride", style="Success.TButton", command=self._complete_ride).pack(side="left", padx=4)

        self.fare_label = tk.Label(
            inner, text="Fare preview will appear here.", font=("Segoe UI", 11, "bold"),
            bg=COLORS["card"], fg=COLORS["primary"],
        )
        self.fare_label.pack(anchor="w", pady=(12, 0))

        ttk.Label(tab, text="Ride History", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(4, 4))
        cols = ("id", "customer", "driver", "distance", "fare", "date")
        self.rides_tree = ttk.Treeview(tab, columns=cols, show="headings", height=11)
        for c, t, w in [("id", "Ride #", 60), ("customer", "Customer", 150), ("driver", "Driver", 150),
                        ("distance", "Distance", 80), ("fare", "Fare", 80), ("date", "Completed", 140)]:
            self.rides_tree.heading(c, text=t)
            self.rides_tree.column(c, width=w)
        self.rides_tree.pack(fill="both", expand=True)

    def _calc_fare_preview(self):
        ok, distance = validate_distance(self.ride_distance.get())
        if not ok:
            return messagebox.showerror("Validation", distance)
        vehicle = "Sedan"
        try:
            c_idx = int(self.ride_customer_id.get()) - 1
            if c_idx in range(len(self.customers)):
                driver_name = self.customers[c_idx].get_taxi_driver()
                for d in self.drivers:
                    if d.full_name() == driver_name:
                        vehicle = d.get_vehicle_type()
                        break
        except ValueError:
            pass
        breakdown = fare_breakdown(distance, vehicle)
        self.fare_label.config(
            text=f"Vehicle: {vehicle}  |  Base: £{breakdown['base_fare']:.2f}  +  "
                 f"{distance} km × £{breakdown['rate_per_km']:.2f}  =  Total: £{breakdown['total']:.2f}",
            fg=COLORS["success"],
        )

    def _complete_ride(self):
        try:
            c_idx = int(self.ride_customer_id.get()) - 1
        except ValueError:
            return messagebox.showerror("Validation", "Enter a valid customer ID.")
        if c_idx not in range(len(self.customers)):
            return messagebox.showerror("Error", "Invalid customer ID.")
        ok, distance = validate_distance(self.ride_distance.get())
        if not ok:
            return messagebox.showerror("Validation", distance)

        customer = self.customers[c_idx]
        driver_name = customer.get_taxi_driver()
        if driver_name == "None":
            return messagebox.showerror("Error", "Customer has no assigned driver.")

        driver = next((d for d in self.drivers if d.full_name() == driver_name), None)
        vehicle = driver.get_vehicle_type() if driver else "Sedan"
        fare = calculate_fare(distance, vehicle)
        self.rides.append(Ride(
            customer.full_name(), driver_name, distance, fare, vehicle,
            completed_at=datetime.now(), ride_id=self.next_ride_id,
        ))
        self.next_ride_id += 1
        self.completed.append(customer)
        self.customers.pop(c_idx)
        if driver:
            driver.set_status(TaxiDriver.STATUS_AVAILABLE)

        self._refresh_all()
        self.ride_customer_id.delete(0, tk.END)
        self.ride_distance.delete(0, tk.END)
        self.fare_label.config(text=f"Ride completed. Fare charged: £{fare:.2f}", fg=COLORS["success"])
        messagebox.showinfo("Ride Complete", f"Fare: £{fare:.2f}\nDriver status set to Available.")

    def _refresh_rides_history(self):
        if not hasattr(self, "rides_tree"):
            return
        for item in self.rides_tree.get_children():
            self.rides_tree.delete(item)
        for r in self.rides:
            self.rides_tree.insert("", "end", values=(
                r.ride_id or "-", r.customer_name, r.driver_name,
                f"{r.distance_km:.1f} km", f"£{r.fare:.2f}", r.completed_at.strftime("%Y-%m-%d %H:%M"),
            ))

    # ---- Reports tab ----
    def _tab_reports(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  Reports  ")

        ttk.Button(tab, text="Generate Report", style="Accent.TButton", command=self._show_report).pack(anchor="w", pady=5)
        self.report_text = scrolledtext.ScrolledText(
            tab, height=28, font=("Consolas", 10),
            bg="#fafbfc", fg=COLORS["text"], relief="flat",
            highlightbackground=COLORS["card_border"], highlightthickness=1,
        )
        self.report_text.pack(fill="both", expand=True, pady=5)

    def _show_report(self):
        report = generate_management_report(self.drivers, self.customers, self.rides, self.completed)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, report)

    # ---- Charts tab ----
    def _tab_charts(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  Charts  ")

        btn_row = ttk.Frame(tab)
        btn_row.pack(fill="x", pady=5)
        charts = [
            ("Daily Rides", "daily", "Info.TButton"),
            ("Monthly Rides", "monthly", "Info.TButton"),
            ("Driver Status", "status", "Accent.TButton"),
            ("Rides per Driver", "rides_driver", "Primary.TButton"),
            ("Revenue", "revenue", "Success.TButton"),
        ]
        for label, key, style in charts:
            ttk.Button(btn_row, text=label, style=style, command=lambda k=key: self._show_chart(k)).pack(side="left", padx=4)

        chart_frame = self._make_card(tab, padx=8, pady=8)
        chart_frame.pack(fill="both", expand=True, pady=8)
        self.chart_label = tk.Label(chart_frame, bg=COLORS["card"])
        self.chart_label.pack(fill="both", expand=True, padx=10, pady=10)

    def _show_chart(self, chart_type):
        try:
            paths = {
                "daily": chart_daily_rides,
                "monthly": chart_monthly_rides,
                "status": lambda _: chart_driver_status(self.drivers),
                "rides_driver": chart_rides_per_driver,
                "revenue": chart_revenue_by_driver,
            }
            path = paths[chart_type](self.rides) if chart_type != "status" else paths[chart_type](None)
            img = Image.open(path)
            img.thumbnail((920, 480), Image.Resampling.LANCZOS)
            self._chart_photo = ImageTk.PhotoImage(img)
            self.chart_label.config(image=self._chart_photo, text="")
        except Exception as exc:
            messagebox.showerror("Chart Error", str(exc))

    # ---- Admin tab ----
    def _tab_admin(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="  Admin  ")

        form = ttk.LabelFrame(tab, text="Admin Account Settings", padding=16)
        form.pack(anchor="w", fill="x")

        admin_user = next((u for u in self.users if u.get("role") == "admin"), self.current_user)

        ttk.Label(form, text="Username:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.admin_user = ttk.Entry(form, width=30)
        self.admin_user.grid(row=0, column=1, pady=5)
        self.admin_user.insert(0, admin_user.get("username", ""))

        ttk.Label(form, text="New Password:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.admin_pass = ttk.Entry(form, width=30, show="*")
        self.admin_pass.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="Confirm Password:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.admin_pass2 = ttk.Entry(form, width=30, show="*")
        self.admin_pass2.grid(row=2, column=1, pady=5)

        ttk.Label(form, text="Address (postcode):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.admin_address = ttk.Entry(form, width=30)
        self.admin_address.grid(row=3, column=1, pady=5)
        self.admin_address.insert(0, admin_user.get("address", ""))

        ttk.Button(form, text="Save Admin Details", style="Accent.TButton", command=self._save_admin).grid(
            row=4, column=0, columnspan=2, pady=15
        )

        ttk.Label(tab, text="Registered Users", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(20, 6))
        cols = ("username", "name", "role")
        self.users_tree = ttk.Treeview(tab, columns=cols, show="headings", height=6)
        for c, t, w in [("username", "Username", 150), ("name", "Full Name", 200), ("role", "Role", 100)]:
            self.users_tree.heading(c, text=t)
            self.users_tree.column(c, width=w)
        self.users_tree.pack(fill="x")
        self._refresh_users_list()

    def _refresh_users_list(self):
        if not hasattr(self, "users_tree"):
            return
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        for u in self.users:
            self.users_tree.insert("", "end", values=(u["username"], u.get("full_name", ""), u.get("role", "staff")))

    def _save_admin(self):
        ok, username = validate_username(self.admin_user.get())
        if not ok:
            return messagebox.showerror("Validation", username)

        pw = self.admin_pass.get()
        admin_user = next((u for u in self.users if u.get("role") == "admin"), None)
        if not admin_user:
            return messagebox.showerror("Error", "No admin account found.")

        if pw:
            if pw != self.admin_pass2.get():
                return messagebox.showerror("Validation", "Passwords do not match.")
            ok, pw = validate_password(pw)
            if not ok:
                return messagebox.showerror("Validation", pw)
            admin_user["password"] = pw

        ok, address = validate_postcode(self.admin_address.get())
        if not ok:
            return messagebox.showerror("Validation", address)

        admin_user["username"] = username
        admin_user["address"] = address
        self.admin.set_username(username)
        if pw:
            self.admin.set_password(pw)
        self.admin.set_address(address)
        self._persist()
        self._refresh_users_list()
        messagebox.showinfo("Saved", "Admin details updated.")


def run_gui():
    root = tk.Tk()
    setup_styles(ttk.Style(root))
    TaxiManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
