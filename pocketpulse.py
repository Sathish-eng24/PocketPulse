import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import random
import csv
from datetime import datetime, timedelta

# ==============================================================================
# COLOR PALETTE (Pure White Primary + 5 Semantic Sub-Colors)
# ==============================================================================
COLORS = {
    "WHITE": "#FFFFFF",        # Main background & card
    "SIDEBAR_BG": "#F8FAFC",   # Clean light sidebar background
    "BORDER": "#E2E8F0",       # Card borders and dividers
    "TEXT_DARK": "#0F172A",    # Main headings and numbers
    "TEXT_MUTED": "#64748B",   # Subtitles and captions
    "SKY_BLUE": "#0284C7",     # Primary buttons, Income, Balance
    "ORANGE": "#EA580C",       # Expenses, Warnings, Over-budget alerts
    "GREEN": "#16A34A",        # Safe daily limit, Savings goal
    "PURPLE": "#7C3AED",       # Subscriptions, EMIs, Simulator
    "BROWN": "#78350F"         # Weekly summary, Daily limit label, Filters
}

CATEGORY_COLORS = {
    "Food & Dining": COLORS["SKY_BLUE"],
    "Party & Outings": COLORS["ORANGE"],
    "Transport": COLORS["BROWN"],
    "Shopping": COLORS["PURPLE"],
    "Groceries": COLORS["GREEN"],
    "Bills & Recharge": "#64748B",
    "Salary / Pocket Money": COLORS["GREEN"],
    "Extra Income": COLORS["SKY_BLUE"]
}

EXPENSE_CATEGORIES = [
    "Food & Dining",
    "Party & Outings",
    "Transport",
    "Shopping",
    "Groceries",
    "Bills & Recharge"
]

INCOME_CATEGORIES = [
    "Salary / Pocket Money",
    "Extra Income"
]

DB_FILE = "finance_data.db"


# ==============================================================================
# PART 1: SQLITE DATABASE & CSV IMPORT/EXPORT MODULE (Member 1)
# ==============================================================================
def init_db():
    """Creates SQLite tables for transactions, recurring bills, and settings."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            t_date TEXT NOT NULL,
            t_type TEXT NOT NULL,
            category TEXT NOT NULL,
            gross_amount REAL NOT NULL,
            friend_split REAL DEFAULT 0.0,
            net_amount REAL NOT NULL,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS recurring (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            r_type TEXT NOT NULL,
            amount REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value REAL NOT NULL
        )
    """)

    # Insert default settings if not present
    default_settings = {
        "monthly_budget_limit": 8000.0,
        "savings_goal": 2500.0,
        "days_until_salary": 18.0
    }
    for k, v in default_settings.items():
        cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    # Seed starter data if the transactions table is empty
    cur.execute("SELECT COUNT(*) FROM transactions")
    if cur.fetchone()[0] == 0:
        seed_sample_data(conn)

    conn.commit()
    conn.close()


def seed_sample_data(conn):
    """Populates realistic starter income, expenses, and recurring EMIs."""
    cur = conn.cursor()
    today = datetime.now()

    starter_tx = [
        ((today - timedelta(days=12)).strftime("%Y-%m-%d"), "Income", "Salary / Pocket Money", 15000, 0, 15000, "Monthly Pocket Money"),
        ((today - timedelta(days=10)).strftime("%Y-%m-%d"), "Income", "Extra Income", 1500, 0, 1500, "Lab TA / Coding Gig"),
        ((today - timedelta(days=9)).strftime("%Y-%m-%d"), "Expense", "Food & Dining", 180, 0, 180, "Canteen lunch & juice"),
        ((today - timedelta(days=7)).strftime("%Y-%m-%d"), "Expense", "Party & Outings", 1200, 800, 400, "Pizza night (Split w/ 2 friends)"),
        ((today - timedelta(days=5)).strftime("%Y-%m-%d"), "Expense", "Transport", 220, 0, 220, "Shared auto to town"),
        ((today - timedelta(days=3)).strftime("%Y-%m-%d"), "Expense", "Groceries", 450, 0, 450, "Fruits, milk & oats"),
        ((today - timedelta(days=2)).strftime("%Y-%m-%d"), "Expense", "Shopping", 650, 0, 650, "USB-C cable & notebook"),
        ((today - timedelta(days=1)).strftime("%Y-%m-%d"), "Expense", "Food & Dining", 90, 0, 90, "Evening tea & samosa")
    ]
    cur.executemany("""
        INSERT INTO transactions (t_date, t_type, category, gross_amount, friend_split, net_amount, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, starter_tx)

    starter_rec = [
        ("Phone / Laptop EMI", "EMI", 2200.0),
        ("Hostel Gym / Mess Add-on", "EMI", 800.0),
        ("Spotify & Netflix Plan", "Subscription", 299.0),
        ("Mobile Data Pack", "Subscription", 249.0)
    ]
    cur.executemany("INSERT INTO recurring (name, r_type, amount) VALUES (?, ?, ?)", starter_rec)


def get_setting(key):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return float(row[0]) if row else 0.0


def update_setting(key, value):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, float(value)))
    conn.commit()
    conn.close()


def fetch_transactions(search_text="", category_filter="All", type_filter="All"):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    query = "SELECT id, t_date, t_type, category, gross_amount, friend_split, net_amount, notes FROM transactions WHERE 1=1"
    params = []

    if category_filter != "All":
        query += " AND category = ?"
        params.append(category_filter)
    if type_filter != "All":
        query += " AND t_type = ?"
        params.append(type_filter)
    if search_text.strip():
        query += " AND (LOWER(notes) LIKE ? OR LOWER(category) LIKE ? OR t_date LIKE ?)"
        like_str = f"%{search_text.strip().lower()}%"
        params.extend([like_str, like_str, like_str])

    query += " ORDER BY t_date DESC, id DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def fetch_recurring():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, name, r_type, amount FROM recurring ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


# ==============================================================================
# PART 2: ACCURATE BUDGET, WEEKLY/MONTHLY SUMMARY & SURVIVAL MATH (Member 2)
# ==============================================================================
def calculate_all_metrics():
    """
    Computes simple, accurate arithmetic for:
    - Total Income, Total Variable Expenses, Total EMIs/Subscriptions
    - Weekly Spending (last 7 days) & Monthly Spending
    - Remaining Balance, Safe Daily Spending Limit, and Survival What-To-Avoid advice
    """
    rows = fetch_transactions()
    rec_rows = fetch_recurring()

    budget_limit = get_setting("monthly_budget_limit")
    savings_goal = get_setting("savings_goal")
    days_left = max(1, int(get_setting("days_until_salary")))

    total_income = 0.0
    total_variable_expense = 0.0
    weekly_expense = 0.0
    total_friend_refunds = 0.0

    cat_totals = {c: 0.0 for c in EXPENSE_CATEGORIES}
    inc_cat_totals = {c: 0.0 for c in INCOME_CATEGORIES}
    monthly_buckets = {}

    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    for r in rows:
        _, t_date, t_type, cat, gross, split, net, _ = r
        month_key = t_date[:7]  # YYYY-MM

        if t_type == "Income":
            total_income += net
            inc_cat_totals[cat] = inc_cat_totals.get(cat, 0.0) + net
        else:
            total_variable_expense += net
            total_friend_refunds += split
            cat_totals[cat] = cat_totals.get(cat, 0.0) + net
            monthly_buckets[month_key] = monthly_buckets.get(month_key, 0.0) + net
            if t_date >= seven_days_ago:
                weekly_expense += net

    total_emi = sum(r[3] for r in rec_rows if r[2] == "EMI")
    total_subs = sum(r[3] for r in rec_rows if r[2] == "Subscription")
    total_recurring = total_emi + total_subs

    # Total Outflow = Variable Expenses + Recurring EMIs & Subscriptions
    total_expenses_all = total_variable_expense + total_recurring

    # Remaining Balance = Total Income - Total Expenses (All)
    remaining_balance = total_income - total_expenses_all

    # Spendable Pool After Locking Savings Goal
    spendable_after_savings = remaining_balance - savings_goal

    # Basic Daily Spending Limit = Spendable Pool / Days Until Next Salary
    daily_limit = round(spendable_after_savings / days_left, 2)

    # Simple Budget Alert Status
    budget_used_pct = round((total_variable_expense / max(1.0, budget_limit)) * 100, 1)
    is_over_budget = total_variable_expense > budget_limit

    # Simple Survival Advice ("What to Avoid")
    if daily_limit <= 0:
        survival_status = "CRITICAL: Rs.0/day left"
        avoid_advice = (
            "Your Expenses + EMIs + Savings Goal exceed your Income! "
            "Avoid ALL eating out, parties, shopping, and cab rides, or reduce your savings goal temporarily."
        )
    elif daily_limit < 200:
        survival_status = f"TIGHT BUDGET: Rs.{daily_limit:.0f}/day"
        avoid_advice = (
            f"You only have Rs.{daily_limit:.0f} per day for the next {days_left} days. "
            "AVOID: Weekend parties, Zomato/Swiggy orders, and solo autos. Stick to mess/home meals."
        )
    elif daily_limit < 450:
        survival_status = f"MODERATE: Rs.{daily_limit:.0f}/day"
        avoid_advice = (
            f"You have Rs.{daily_limit:.0f} per day for the next {days_left} days. "
            "AVOID: Group dinner bills over Rs.300 and impulse online shopping."
        )
    else:
        survival_status = f"SAFE RUNWAY: Rs.{daily_limit:.0f}/day"
        avoid_advice = (
            f"Comfortable buffer of Rs.{daily_limit:.0f} per day for {days_left} days! "
            "AVOID: Unplanned gadget/luxury splurges (>Rs.1,500) so you easily hit your savings goal."
        )

    return {
        "total_income": round(total_income, 2),
        "total_variable_expense": round(total_variable_expense, 2),
        "total_emi": round(total_emi, 2),
        "total_subs": round(total_subs, 2),
        "total_recurring": round(total_recurring, 2),
        "total_expenses_all": round(total_expenses_all, 2),
        "weekly_expense": round(weekly_expense, 2),
        "remaining_balance": round(remaining_balance, 2),
        "spendable_after_savings": round(spendable_after_savings, 2),
        "daily_limit": daily_limit,
        "days_left": days_left,
        "budget_limit": budget_limit,
        "budget_used_pct": budget_used_pct,
        "is_over_budget": is_over_budget,
        "savings_goal": savings_goal,
        "total_friend_refunds": round(total_friend_refunds, 2),
        "cat_totals": cat_totals,
        "inc_cat_totals": inc_cat_totals,
        "monthly_buckets": monthly_buckets,
        "tx_count": len(rows),
        "rec_count": len(rec_rows),
        "survival_status": survival_status,
        "avoid_advice": avoid_advice
    }


# ==============================================================================
# PART 3: RANDOM EXPENSE SIMULATOR & GENERATOR (`random` library) (Member 3)
# ==============================================================================
RANDOM_EVENT_POOL = [
    ("Food & Dining", "Late-night food delivery", 140, 280),
    ("Party & Outings", "Birthday treat / cafe hangout", 250, 600),
    ("Transport", "Rainy day cab / auto fare", 90, 220),
    ("Shopping", "Stationery & college supplies", 120, 350),
    ("Groceries", "Hostel room snacks & fruit", 100, 260),
    ("Bills & Recharge", "Extra mobile data booster", 65, 180)
]


def add_random_sample_expenses(count=5):
    """
    Uses Python's `random` module to insert `count` realistic transactions
    across the last 60 days so the user can test charts and filters immediately.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    today = datetime.now()

    for _ in range(count):
        cat, note, low, high = random.choice(RANDOM_EVENT_POOL)
        days_ago = random.randint(0, 45)
        t_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        gross = float(random.randint(low, high))

        # 25% chance the bill was split with a friend
        friend_split = float(random.randint(40, int(gross * 0.5))) if random.random() < 0.25 else 0.0
        net = round(gross - friend_split, 2)

        cur.execute("""
            INSERT INTO transactions (t_date, t_type, category, gross_amount, friend_split, net_amount, notes)
            VALUES (?, 'Expense', ?, ?, ?, ?, ?)
        """, (t_date, cat, gross, friend_split, net, note))

    conn.commit()
    conn.close()


def simulate_remaining_days(spendable_pool, days_left, daily_limit):
    """
    Uses `random.uniform` and `random.choice` to simulate day-by-day spending
    from Day 1 to `days_left` under two easy-to-understand scenarios:
    1. Careful Mode: Stays near the daily limit with very few impulse buys.
    2. Unplanned Shocks Mode: Includes random party/outing/delivery surprises.
    """
    days_left = max(1, int(days_left))
    base_daily = max(100.0, daily_limit if daily_limit > 0 else 200.0)

    careful_balances = [round(spendable_pool, 2)]
    shock_balances = [round(spendable_pool, 2)]
    shock_log = []

    bal_careful = float(spendable_pool)
    bal_shock = float(spendable_pool)

    for d in range(1, days_left + 1):
        # 1. Careful daily spend (70% to 95% of daily allowance)
        spend_c = base_daily * random.uniform(0.70, 0.95)
        bal_careful -= spend_c
        careful_balances.append(round(bal_careful, 2))

        # 2. Unplanned Shock spend (85% to 110% of daily allowance + 25% chance of random event)
        spend_s = base_daily * random.uniform(0.85, 1.10)
        if random.random() < 0.25:
            cat, note, low, high = random.choice(RANDOM_EVENT_POOL)
            extra = random.randint(low, high)
            spend_s += extra
            shock_log.append(f"Day {d}: {note} ({cat}) -> -Rs.{extra}")

        bal_shock -= spend_s
        shock_balances.append(round(bal_shock, 2))

    return careful_balances, shock_balances, shock_log


# ==============================================================================
# PART 4: MODERN TKINTER GUI WITH CLEAN SIDEBAR & 4 VIEWS (Member 4)
# ==============================================================================
class PocketPulseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PocketPulse — Personal Finance, Budget & Survival Tracker")
        self.root.geometry("1240x780")
        self.root.configure(bg=COLORS["WHITE"])

        init_db()
        self.selected_tx_id = None

        self.setup_styles()
        self.build_shell()
        self.show_view("dashboard")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=COLORS["WHITE"],
            fieldbackground=COLORS["WHITE"],
            foreground=COLORS["TEXT_DARK"],
            rowheight=26,
            font=("Arial", 9)
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["SKY_BLUE"],
            foreground=COLORS["WHITE"],
            font=("Arial", 9, "bold")
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["SKY_BLUE"])],
            foreground=[("selected", COLORS["WHITE"])]
        )

    def build_shell(self):
        # --- LEFT SIDEBAR ---
        self.sidebar = tk.Frame(
            self.root, bg=COLORS["SIDEBAR_BG"], width=230,
            highlightthickness=1, highlightbackground=COLORS["BORDER"]
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # App Brand Title
        brand_box = tk.Frame(self.sidebar, bg=COLORS["SIDEBAR_BG"], padx=18, pady=20)
        brand_box.pack(fill=tk.X)
        tk.Label(
            brand_box, text="💳 PocketPulse",
            font=("Arial", 17, "bold"), bg=COLORS["SIDEBAR_BG"], fg=COLORS["SKY_BLUE"]
        ).pack(anchor="w")
        tk.Label(
            brand_box, text="Smart Budget & Survival App",
            font=("Arial", 9, "bold"), bg=COLORS["SIDEBAR_BG"], fg=COLORS["BROWN"]
        ).pack(anchor="w", pady=(2, 0))

        # Sidebar Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊  Dashboard Overview"),
            ("transactions", "📝  Income & Expenses"),
            ("budget", "⚙️  Budget, EMIs & Goal"),
            ("simulator", "🎲  Simulator & Report")
        ]
        for key, label in nav_items:
            btn = tk.Button(
                self.sidebar, text=label, anchor="w",
                font=("Arial", 10, "bold"), bg=COLORS["SIDEBAR_BG"], fg=COLORS["TEXT_DARK"],
                relief=tk.FLAT, padx=20, pady=11, cursor="hand2",
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(fill=tk.X, padx=10, pady=3)
            self.nav_buttons[key] = btn

        # Quick Action Footer inside Sidebar
        side_footer = tk.Frame(self.sidebar, bg=COLORS["SIDEBAR_BG"], padx=14, pady=14)
        side_footer.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(
            side_footer, text="🎲 +5 Random Spends",
            command=self.quick_random_populate,
            bg=COLORS["PURPLE"], fg=COLORS["WHITE"], font=("Arial", 9, "bold"),
            relief=tk.FLAT, pady=6, cursor="hand2"
        ).pack(fill=tk.X, pady=(0, 6))

        tk.Button(
            side_footer, text="📂 Import CSV", command=self.import_csv,
            bg=COLORS["SKY_BLUE"], fg=COLORS["WHITE"], font=("Arial", 9, "bold"),
            relief=tk.FLAT, pady=5, cursor="hand2"
        ).pack(fill=tk.X, pady=(0, 6))

        tk.Button(
            side_footer, text="💾 Export CSV", command=self.export_csv,
            bg=COLORS["GREEN"], fg=COLORS["WHITE"], font=("Arial", 9, "bold"),
            relief=tk.FLAT, pady=5, cursor="hand2"
        ).pack(fill=tk.X)

        # --- MAIN RIGHT CONTENT AREA ---
        self.main_area = tk.Frame(self.root, bg=COLORS["WHITE"], padx=22, pady=16)
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def make_card(self, parent, border_col=COLORS["BORDER"], padx=14, pady=12):
        return tk.Frame(
            parent, bg=COLORS["WHITE"], padx=padx, pady=pady,
            highlightthickness=1, highlightbackground=border_col
        )

    def show_view(self, view_key):
        # Highlight active sidebar button
        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.config(bg=COLORS["SKY_BLUE"], fg=COLORS["WHITE"])
            else:
                btn.config(bg=COLORS["SIDEBAR_BG"], fg=COLORS["TEXT_DARK"])

        # Clear main area
        for w in self.main_area.winfo_children():
            w.destroy()

        if view_key == "dashboard":
            self.build_dashboard_view()
        elif view_key == "transactions":
            self.build_transactions_view()
        elif view_key == "budget":
            self.build_budget_view()
        elif view_key == "simulator":
            self.build_simulator_view()

    # ==========================================================================
    # VIEW 1: MODERN DASHBOARD (6 KPI Cards + Pie Chart + Bar Graph + Alerts)
    # ==========================================================================
    def build_dashboard_view(self):
        m = calculate_all_metrics()

        # Top Header Row
        hdr = tk.Frame(self.main_area, bg=COLORS["WHITE"])
        hdr.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            hdr, text="Financial Dashboard",
            font=("Arial", 20, "bold"), bg=COLORS["WHITE"], fg=COLORS["TEXT_DARK"]
        ).pack(side=tk.LEFT)

        pill_color = COLORS["ORANGE"] if m["is_over_budget"] or m["daily_limit"] < 200 else COLORS["GREEN"]
        tk.Label(
            hdr, text=f"🔔 {m['survival_status']}  |  Budget Used: {m['budget_used_pct']}%",
            font=("Arial", 10, "bold"), bg=pill_color, fg=COLORS["WHITE"], padx=12, pady=5
        ).pack(side=tk.RIGHT)

        # Row 1: 6 KPI Cards (FinancialAha Inspired)
        kpi_row = tk.Frame(self.main_area, bg=COLORS["WHITE"])
        kpi_row.pack(fill=tk.X, pady=(0, 12))

        self.create_kpi_card(
            kpi_row, "REMAINING BALANCE", f"Rs.{m['remaining_balance']:,.0f}",
            f"After all expenses & EMIs", COLORS["SKY_BLUE"]
        )
        self.create_kpi_card(
            kpi_row, "TOTAL INCOME", f"Rs.{m['total_income']:,.0f}",
            f"{m['days_left']} days until next salary", COLORS["GREEN"]
        )
        self.create_kpi_card(
            kpi_row, "MONTHLY EXPENSES", f"Rs.{m['total_variable_expense']:,.0f}",
            f"Last 7 Days: Rs.{m['weekly_expense']:,.0f}", COLORS["ORANGE"]
        )
        self.create_kpi_card(
            kpi_row, "SAVINGS GOAL", f"Rs.{m['savings_goal']:,.0f}",
            f"Locked for this month", COLORS["PURPLE"]
        )
        self.create_kpi_card(
            kpi_row, "EMIs & SUBS", f"Rs.{m['total_recurring']:,.0f}",
            f"{m['rec_count']} active recurring bills", COLORS["BROWN"]
        )
        limit_col = COLORS["GREEN"] if m["daily_limit"] >= 200 else COLORS["ORANGE"]
        self.create_kpi_card(
            kpi_row, "SAFE DAILY LIMIT", f"Rs.{m['daily_limit']:,.0f}/day",
            f"Pool after savings: Rs.{m['spendable_after_savings']:,.0f}", limit_col
        )

        # Row 2: Budget Alert Banner + What To Avoid Survival Box
        alert_card = self.make_card(
            self.main_area,
            border_col=COLORS["ORANGE"] if m["is_over_budget"] else COLORS["GREEN"],
            padx=14, pady=10
        )
        alert_card.pack(fill=tk.X, pady=(0, 12))

        budget_msg = (
            f"🚨 BUDGET EXCEEDED ALERT: You have spent Rs.{m['total_variable_expense']:,.0f} "
            f"(Limit: Rs.{m['budget_limit']:,.0f})!"
            if m["is_over_budget"] else
            f"✅ BUDGET ON TRACK: Spent Rs.{m['total_variable_expense']:,.0f} of Rs.{m['budget_limit']:,.0f} "
            f"({m['budget_used_pct']}%)  |  Friend Bill-Splits Recovered: Rs.{m['total_friend_refunds']:,.0f}"
        )
        tk.Label(
            alert_card, text=budget_msg,
            font=("Arial", 10, "bold"), bg=COLORS["WHITE"],
            fg=COLORS["ORANGE"] if m["is_over_budget"] else COLORS["GREEN"]
        ).pack(anchor="w")

        tk.Label(
            alert_card, text=f"💡 Survival Advisor: {m['avoid_advice']}",
            font=("Arial", 9), bg=COLORS["WHITE"], fg=COLORS["TEXT_DARK"]
        ).pack(anchor="w", pady=(3, 0))

        # Row 3: 3-Column Analytics Section (Top Categories + Donut Chart + Monthly Bar Graph)
        charts_row = tk.Frame(self.main_area, bg=COLORS["WHITE"])
        charts_row.pack(fill=tk.BOTH, expand=True)

        # Column A: Top Categories Table
        cat_card = self.make_card(charts_row, border_col=COLORS["BORDER"], padx=14, pady=12)
        cat_card.configure(width=290)
        cat_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        cat_card.pack_propagate(False)

        tk.Label(
            cat_card, text="TOP EXPENSE CATEGORIES",
            font=("Arial", 10, "bold"), bg=COLORS["WHITE"], fg=COLORS["BROWN"]
        ).pack(anchor="w", pady=(0, 8))

        sorted_cats = sorted(m["cat_totals"].items(), key=lambda x: x[1], reverse=True)
        total_var = max(1.0, m["total_variable_expense"])
        for cat_name, amt in sorted_cats:
            pct = (amt / total_var) * 100.0 if m["total_variable_expense"] > 0 else 0.0
            r_frame = tk.Frame(cat_card, bg=COLORS["WHITE"], pady=5)
            r_frame.pack(fill=tk.X)
            dot_col = CATEGORY_COLORS.get(cat_name, COLORS["SKY_BLUE"])
            tk.Label(r_frame, text="●", font=("Arial", 11), bg=COLORS["WHITE"], fg=dot_col).pack(side=tk.LEFT)
            tk.Label(r_frame, text=cat_name, font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["TEXT_DARK"]).pack(side=tk.LEFT, padx=4)
            tk.Label(r_frame, text=f"{pct:.1f}%", font=("Arial", 8), bg=COLORS["WHITE"], fg=COLORS["TEXT_MUTED"]).pack(side=tk.RIGHT)
            tk.Label(r_frame, text=f"Rs.{amt:,.0f}", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["ORANGE"]).pack(side=tk.RIGHT, padx=8)

        # Column B: Category-Wise Donut Pie Chart
        pie_card = self.make_card(charts_row, border_col=COLORS["BORDER"], padx=12, pady=12)
        pie_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(
            pie_card, text="CATEGORY-WISE SPENDING PIE CHART",
            font=("Arial", 10, "bold"), bg=COLORS["WHITE"], fg=COLORS["SKY_BLUE"]
        ).pack(anchor="w")

        pie_canvas = tk.Canvas(pie_card, width=320, height=280, bg=COLORS["WHITE"], highlightthickness=0)
        pie_canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_donut_pie_chart(pie_canvas, sorted_cats, m["total_variable_expense"])

        # Column C: Monthly Spending Bar Graph
        bar_card = self.make_card(charts_row, border_col=COLORS["BORDER"], padx=12, pady=12)
        bar_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            bar_card, text="MONTHLY SPENDING BAR GRAPH",
            font=("Arial", 10, "bold"), bg=COLORS["WHITE"], fg=COLORS["PURPLE"]
        ).pack(anchor="w")

        bar_canvas = tk.Canvas(bar_card, width=320, height=280, bg=COLORS["WHITE"], highlightthickness=0)
        bar_canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_monthly_bar_graph(bar_canvas, m["monthly_buckets"], m["budget_limit"])

    def create_kpi_card(self, parent, title, main_val, sub_text, accent_color):
        card = self.make_card(parent, border_col=COLORS["BORDER"], padx=10, pady=10)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        tk.Label(card, text=title, font=("Arial", 8, "bold"), bg=COLORS["WHITE"], fg=COLORS["TEXT_MUTED"]).pack(anchor="w")
        tk.Label(card, text=main_val, font=("Arial", 16, "bold"), bg=COLORS["WHITE"], fg=accent_color).pack(anchor="w", pady=(4, 2))
        tk.Label(card, text=sub_text, font=("Arial", 8), bg=COLORS["WHITE"], fg=COLORS["TEXT_MUTED"]).pack(anchor="w")

    def draw_donut_pie_chart(self, canvas, sorted_cats, total_spent):
        cx, cy, r_out, r_in = 115, 145, 92, 40
        x1, y1, x2, y2 = cx - r_out, cy - r_out, cx + r_out, cy + r_out

        if total_spent <= 0:
            canvas.create_oval(x1, y1, x2, y2, fill="#F1F5F9", outline=COLORS["BORDER"])
            canvas.create_text(cx, cy, text="No Data", font=("Arial", 9, "bold"), fill=COLORS["TEXT_MUTED"])
            return

        start_ang = 90.0
        leg_y = 45
        for cat_name, amt in sorted_cats:
            if amt <= 0:
                continue
            extent = (amt / total_spent) * 360.0
            pct = (amt / total_spent) * 100.0
            col = CATEGORY_COLORS.get(cat_name, COLORS["SKY_BLUE"])

            if extent >= 359.9:
                canvas.create_oval(x1, y1, x2, y2, fill=col, outline=COLORS["WHITE"], width=2)
            else:
                canvas.create_arc(x1, y1, x2, y2, start=start_ang, extent=-extent, fill=col, outline=COLORS["WHITE"], width=2)

            canvas.create_rectangle(222, leg_y, 232, leg_y + 10, fill=col, outline="")
            canvas.create_text(238, leg_y + 5, text=f"{cat_name[:12]} ({pct:.0f}%)", anchor="w", font=("Arial", 8, "bold"), fill=COLORS["TEXT_DARK"])
            leg_y += 24
            start_ang -= extent

        canvas.create_oval(cx - r_in, cy - r_in, cx + r_in, cy + r_in, fill=COLORS["WHITE"], outline=COLORS["WHITE"])
        canvas.create_text(cx, cy, text=f"Rs.{total_spent:,.0f}", font=("Arial", 9, "bold"), fill=COLORS["TEXT_DARK"])

    def draw_monthly_bar_graph(self, canvas, monthly_buckets, budget_limit):
        gx1, gy1, gx2, gy2 = 42, 30, 315, 235
        canvas.create_line(gx1, gy2, gx2, gy2, fill=COLORS["BROWN"], width=2)
        canvas.create_line(gx1, gy1, gx1, gy2, fill=COLORS["BROWN"], width=2)

        # Ensure at least 4 months are shown for a clean bar chart
        now_m = datetime.now().strftime("%Y-%m")
        default_months = ["2026-08", "2026-09", "2026-10", now_m]
        for dm in default_months:
            if dm not in monthly_buckets:
                monthly_buckets[dm] = 0.0

        sorted_m = sorted(monthly_buckets.items())[-5:]
        max_val = max([v for _, v in sorted_m] + [budget_limit, 1000.0]) * 1.15

        # Draw Budget Limit Horizontal Dashed Line
        b_y = gy2 - int((budget_limit / max_val) * (gy2 - gy1 - 15))
        canvas.create_line(gx1, b_y, gx2, b_y, fill=COLORS["ORANGE"], dash=(4, 4), width=1.5)
        canvas.create_text(gx2 - 4, b_y - 8, text=f"Budget: Rs.{budget_limit:,.0f}", anchor="e", font=("Arial", 7, "bold"), fill=COLORS["ORANGE"])

        num_bars = len(sorted_m)
        slot_w = (gx2 - gx1 - 20) / max(1, num_bars)
        bar_w = min(36, int(slot_w * 0.6))

        for i, (m_str, val) in enumerate(sorted_m):
            bx1 = int(gx1 + 15 + i * slot_w)
            bx2 = bx1 + bar_w
            bh = int((val / max_val) * (gy2 - gy1 - 15))
            by1 = gy2 - bh

            bar_col = COLORS["ORANGE"] if val > budget_limit else COLORS["SKY_BLUE"]
            canvas.create_rectangle(bx1, by1, bx2, gy2 - 1, fill=bar_col, outline="")
            canvas.create_text((bx1 + bx2) // 2, by1 - 8, text=f"Rs.{val:,.0f}", font=("Arial", 7, "bold"), fill=COLORS["TEXT_DARK"])
            canvas.create_text((bx1 + bx2) // 2, gy2 + 12, text=m_str[5:], font=("Arial", 8, "bold"), fill=COLORS["BROWN"])

    # ==========================================================================
    # VIEW 2: INCOME & EXPENSE CRUD + SEARCH & FILTERS + BILL SPLITTING
    # ==========================================================================
    def build_transactions_view(self):
        hdr = tk.Frame(self.main_area, bg=COLORS["WHITE"])
        hdr.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            hdr, text="Add, Edit & Delete Transactions (With Friend Bill-Splitting)",
            font=("Arial", 16, "bold"), bg=COLORS["WHITE"], fg=COLORS["TEXT_DARK"]
        ).pack(side=tk.LEFT)

        # Form Card (Add / Edit)
        form_card = self.make_card(self.main_area, border_col=COLORS["SKY_BLUE"], padx=14, pady=12)
        form_card.pack(fill=tk.X, pady=(0, 12))

        self.tx_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.tx_type_var = tk.StringVar(value="Expense")
        self.tx_cat_var = tk.StringVar(value="Food & Dining")
        self.tx_gross_var = tk.StringVar(value="")
        self.tx_split_var = tk.StringVar(value="0")
        self.tx_notes_var = tk.StringVar(value="")

        r1 = tk.Frame(form_card, bg=COLORS["WHITE"])
        r1.pack(fill=tk.X)

        tk.Label(r1, text="Date (YYYY-MM-DD):", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["BROWN"]).grid(row=0, column=0, sticky="w", padx=4)
        tk.Entry(r1, textvariable=self.tx_date_var, width=12, font=("Arial", 9)).grid(row=1, column=0, padx=4, pady=3)

        tk.Label(r1, text="Type:", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["BROWN"]).grid(row=0, column=1, sticky="w", padx=4)
        type_cb = ttk.Combobox(r1, textvariable=self.tx_type_var, values=["Expense", "Income"], state="readonly", width=10)
        type_cb.grid(row=1, column=1, padx=4, pady=3)
        type_cb.bind("<<ComboboxSelected>>", self.on_tx_type_change)

        tk.Label(r1, text="Category:", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["BROWN"]).grid(row=0, column=2, sticky="w", padx=4)
        self.tx_cat_cb = ttk.Combobox(r1, textvariable=self.tx_cat_var, values=EXPENSE_CATEGORIES, state="readonly", width=18)
        self.tx_cat_cb.grid(row=1, column=2, padx=4, pady=3)

        tk.Label(r1, text="Total Paid (Rs):", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["SKY_BLUE"]).grid(row=0, column=3, sticky="w", padx=4)
        tk.Entry(r1, textvariable=self.tx_gross_var, width=11, font=("Arial", 9)).grid(row=1, column=3, padx=4, pady=3)

        tk.Label(r1, text="Friend Split Refund (Rs):", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["GREEN"]).grid(row=0, column=4, sticky="w", padx=4)
        tk.Entry(r1, textvariable=self.tx_split_var, width=13, font=("Arial", 9)).grid(row=1, column=4, padx=4, pady=3)

        tk.Label(r1, text="Notes / Description:", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["TEXT_DARK"]).grid(row=0, column=5, sticky="w", padx=4)
        tk.Entry(r1, textvariable=self.tx_notes_var, width=22, font=("Arial", 9)).grid(row=1, column=5, padx=4, pady=3)

        btn_bar = tk.Frame(form_card, bg=COLORS["WHITE"], pady=6)
        btn_bar.pack(fill=tk.X)

        tk.Button(
            btn_bar, text="➕ Add New Record", command=self.add_tx_record,
            bg=COLORS["SKY_BLUE"], fg=COLORS["WHITE"], font=("Arial", 9, "bold"), relief=tk.FLAT, padx=12, pady=5
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_bar, text="✏️ Update Selected", command=self.update_tx_record,
            bg=COLORS["GREEN"], fg=COLORS["WHITE"], font=("Arial", 9, "bold"), relief=tk.FLAT, padx=12, pady=5
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_bar, text="🗑️ Delete Selected", command=self.delete_tx_record,
            bg=COLORS["ORANGE"], fg=COLORS["WHITE"], font=("Arial", 9, "bold"), relief=tk.FLAT, padx=12, pady=5
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_bar, text="Clear Form", command=self.clear_tx_form,
            bg=COLORS["BORDER"], fg=COLORS["TEXT_DARK"], font=("Arial", 9, "bold"), relief=tk.FLAT, padx=10, pady=5
        ).pack(side=tk.LEFT, padx=4)

        # Search & Filter Card
        list_card = self.make_card(self.main_area, border_col=COLORS["BORDER"], padx=14, pady=12)
        list_card.pack(fill=tk.BOTH, expand=True)

        f_bar = tk.Frame(list_card, bg=COLORS["WHITE"])
        f_bar.pack(fill=tk.X, pady=(0, 8))

        self.search_var = tk.StringVar()
        self.filter_cat_var = tk.StringVar(value="All")
        self.filter_type_var = tk.StringVar(value="All")

        tk.Label(f_bar, text="🔍 Search:", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["BROWN"]).pack(side=tk.LEFT)
        s_ent = tk.Entry(f_bar, textvariable=self.search_var, width=22, font=("Arial", 9))
        s_ent.pack(side=tk.LEFT, padx=6)
        s_ent.bind("<KeyRelease>", lambda e: self.refresh_tx_table())

        tk.Label(f_bar, text="Type:", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["BROWN"]).pack(side=tk.LEFT, padx=(8, 2))
        ft_cb = ttk.Combobox(f_bar, textvariable=self.filter_type_var, values=["All", "Expense", "Income"], state="readonly", width=10)
        ft_cb.pack(side=tk.LEFT, padx=4)
        ft_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_tx_table())

        tk.Label(f_bar, text="Category:", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["BROWN"]).pack(side=tk.LEFT, padx=(8, 2))
        fc_cb = ttk.Combobox(f_bar, textvariable=self.filter_cat_var, values=["All"] + EXPENSE_CATEGORIES + INCOME_CATEGORIES, state="readonly", width=18)
        fc_cb.pack(side=tk.LEFT, padx=4)
        fc_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_tx_table())

        cols = ("ID", "Date", "Type", "Category", "Total Paid", "Friend Split", "Your Net Share", "Notes")
        self.tx_tree = ttk.Treeview(list_card, columns=cols, show="headings", height=14)
        widths = {"ID": 40, "Date": 90, "Type": 75, "Category": 140, "Total Paid": 90, "Friend Split": 90, "Your Net Share": 100, "Notes": 220}
        for c in cols:
            self.tx_tree.heading(c, text=c)
            self.tx_tree.column(c, width=widths[c], anchor="w" if c in ["Category", "Notes"] else "center")
        self.tx_tree.pack(fill=tk.BOTH, expand=True)
        self.tx_tree.bind("<<TreeviewSelect>>", self.on_tx_row_select)

        self.refresh_tx_table()

    def on_tx_type_change(self, event=None):
        if self.tx_type_var.get() == "Income":
            self.tx_cat_cb.config(values=INCOME_CATEGORIES)
            self.tx_cat_var.set(INCOME_CATEGORIES[0])
            self.tx_split_var.set("0")
        else:
            self.tx_cat_cb.config(values=EXPENSE_CATEGORIES)
            self.tx_cat_var.set(EXPENSE_CATEGORIES[0])

    def validate_tx_inputs(self):
        date_str = self.tx_date_var.get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter Date in YYYY-MM-DD format (e.g., 2026-11-15).")
            return None

        try:
            gross = float(self.tx_gross_var.get())
            split = float(self.tx_split_var.get() or 0.0)
            if gross <= 0 or split < 0 or split >= gross:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Amount",
                "Total Paid must be > 0, and Friend Split Refund must be between 0 and Total Paid."
            )
            return None

        t_type = self.tx_type_var.get()
        if t_type == "Income":
            split = 0.0
        net = round(gross - split, 2)
        notes = self.tx_notes_var.get().strip() or self.tx_cat_var.get()
        return date_str, t_type, self.tx_cat_var.get(), gross, split, net, notes

    def add_tx_record(self):
        validated = self.validate_tx_inputs()
        if not validated:
            return
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO transactions (t_date, t_type, category, gross_amount, friend_split, net_amount, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, validated)
        conn.commit()
        conn.close()
        self.clear_tx_form()
        self.refresh_tx_table()

    def update_tx_record(self):
        if not self.selected_tx_id:
            messagebox.showwarning("Select Record", "Click a transaction row in the table first to edit it.")
            return
        validated = self.validate_tx_inputs()
        if not validated:
            return
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("""
            UPDATE transactions
            SET t_date=?, t_type=?, category=?, gross_amount=?, friend_split=?, net_amount=?, notes=?
            WHERE id=?
        """, (*validated, self.selected_tx_id))
        conn.commit()
        conn.close()
        self.clear_tx_form()
        self.refresh_tx_table()

    def delete_tx_record(self):
        if not self.selected_tx_id:
            messagebox.showwarning("Select Record", "Click a transaction row in the table first to delete it.")
            return
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("DELETE FROM transactions WHERE id=?", (self.selected_tx_id,))
        conn.commit()
        conn.close()
        self.clear_tx_form()
        self.refresh_tx_table()

    def clear_tx_form(self):
        self.selected_tx_id = None
        self.tx_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.tx_gross_var.set("")
        self.tx_split_var.set("0")
        self.tx_notes_var.set("")

    def on_tx_row_select(self, event=None):
        sel = self.tx_tree.selection()
        if not sel:
            return
        vals = self.tx_tree.item(sel[0], "values")
        self.selected_tx_id = int(vals[0])
        self.tx_date_var.set(vals[1])
        self.tx_type_var.set(vals[2])
        self.on_tx_type_change()
        self.tx_cat_var.set(vals[3])
        self.tx_gross_var.set(vals[4].replace("Rs.", ""))
        self.tx_split_var.set(vals[5].replace("Rs.", ""))
        self.tx_notes_var.set(vals[7])

    def refresh_tx_table(self):
        for r in self.tx_tree.get_children():
            self.tx_tree.delete(r)
        rows = fetch_transactions(self.search_var.get(), self.filter_cat_var.get(), self.filter_type_var.get())
        for r in rows:
            tid, t_date, t_type, cat, gross, split, net, notes = r
            self.tx_tree.insert("", tk.END, values=(
                tid, t_date, t_type, cat, f"Rs.{gross:.0f}", f"Rs.{split:.0f}", f"Rs.{net:.0f}", notes
            ))

    # ==========================================================================
    # VIEW 3: BUDGET LIMITS, SAVINGS GOAL & RECURRING EMIs/SUBSCRIPTIONS
    # ==========================================================================
    def build_budget_view(self):
        m = calculate_all_metrics()

        tk.Label(
            self.main_area, text="Budget Limit, Savings Goal & Recurring EMIs / Subscriptions",
            font=("Arial", 16, "bold"), bg=COLORS["WHITE"], fg=COLORS["TEXT_DARK"]
        ).pack(anchor="w", pady=(0, 12))

        cols_frame = tk.Frame(self.main_area, bg=COLORS["WHITE"])
        cols_frame.pack(fill=tk.BOTH, expand=True)

        # Left Card: Monthly Budget Limit, Savings Goal & Salary Countdown
        left_card = self.make_card(cols_frame, border_col=COLORS["GREEN"], padx=16, pady=14)
        left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(left_card, text="1. Monthly Targets & Salary Countdown", font=("Arial", 12, "bold"), bg=COLORS["WHITE"], fg=COLORS["GREEN"]).pack(anchor="w", pady=(0, 10))

        self.set_budget_var = tk.StringVar(value=str(int(m["budget_limit"])))
        self.set_savings_var = tk.StringVar(value=str(int(m["savings_goal"])))
        self.set_days_var = tk.StringVar(value=str(int(m["days_left"])))

        tk.Label(left_card, text="Monthly Variable Expense Budget Limit (Rs):", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["BROWN"]).pack(anchor="w", pady=(4, 2))
        tk.Entry(left_card, textvariable=self.set_budget_var, font=("Arial", 11, "bold"), bg=COLORS["WHITE"], highlightthickness=1, highlightbackground=COLORS["SKY_BLUE"]).pack(fill=tk.X, ipady=3)

        tk.Label(left_card, text="Monthly Target Savings Goal (Rs):", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["BROWN"]).pack(anchor="w", pady=(10, 2))
        tk.Entry(left_card, textvariable=self.set_savings_var, font=("Arial", 11, "bold"), bg=COLORS["WHITE"], highlightthickness=1, highlightbackground=COLORS["GREEN"]).pack(fill=tk.X, ipady=3)

        tk.Label(left_card, text="Days Remaining Until Next Salary / Pocket Money:", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["BROWN"]).pack(anchor="w", pady=(10, 2))
        tk.Entry(left_card, textvariable=self.set_days_var, font=("Arial", 11, "bold"), bg=COLORS["WHITE"], highlightthickness=1, highlightbackground=COLORS["PURPLE"]).pack(fill=tk.X, ipady=3)

        tk.Button(
            left_card, text="💾 Save Budget & Goal Settings", command=self.save_budget_settings,
            bg=COLORS["GREEN"], fg=COLORS["WHITE"], font=("Arial", 10, "bold"), relief=tk.FLAT, pady=7, cursor="hand2"
        ).pack(fill=tk.X, pady=(14, 10))

        # Visual Progress Bars for Budget & Savings
        tk.Label(left_card, text=f"Budget Used: Rs.{m['total_variable_expense']:,.0f} / Rs.{m['budget_limit']:,.0f} ({m['budget_used_pct']}%)", font=("Arial", 9, "bold"), bg=COLORS["WHITE"], fg=COLORS["ORANGE"] if m["is_over_budget"] else COLORS["SKY_BLUE"]).pack(anchor="w", pady=(8, 2))
        b_canvas = tk.Canvas(left_card, height=22, bg="#F1F5F9", highlightthickness=0)
        b_canvas.pack(fill=tk.X)
        fill_w = min(400, int((m["budget_used_pct"] / 100.0) * 400))
        b_canvas.create_rectangle(0, 0, fill_w, 22, fill=COLORS["ORANGE"] if m["is_over_budget"] else COLORS["SKY_BLUE"], outline="")

        # Right Card: Recurring EMIs & Subscriptions Manager
        right_card = self.make_card(cols_frame, border_col=COLORS["PURPLE"], padx=16, pady=14)
        right_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(right_card, text="2. Recurring Subscriptions & EMIs", font=("Arial", 12, "bold"), bg=COLORS["WHITE"], fg=COLORS["PURPLE"]).pack(anchor="w", pady=(0, 8))

        rec_form = tk.Frame(right_card, bg=COLORS["WHITE"])
        rec_form.pack(fill=tk.X, pady=(0, 8))

        self.rec_name_var = tk.StringVar()
        self.rec_type_var = tk.StringVar(value="Subscription")
        self.rec_amt_var = tk.StringVar()

        tk.Entry(rec_form, textvariable=self.rec_name_var, width=18, font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Combobox(rec_form, textvariable=self.rec_type_var, values=["Subscription", "EMI"], state="readonly", width=12).pack(side=tk.LEFT, padx=4)
        tk.Entry(rec_form, textvariable=self.rec_amt_var, width=9, font=("Arial", 9)).pack(side=tk.LEFT, padx=4)
        tk.Button(rec_form, text="+ Add", command=self.add_recurring_item, bg=COLORS["PURPLE"], fg=COLORS["WHITE"], font=("Arial", 9, "bold"), relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=4)
        tk.Button(rec_form, text="Delete", command=self.delete_recurring_item, bg=COLORS["ORANGE"], fg=COLORS["WHITE"], font=("Arial", 9, "bold"), relief=tk.FLAT, padx=8).pack(side=tk.LEFT)

        r_cols = ("ID", "Name", "Type", "Monthly Cost")
        self.rec_tree = ttk.Treeview(right_card, columns=r_cols, show="headings", height=10)
        for c in r_cols:
            self.rec_tree.heading(c, text=c)
            self.rec_tree.column(c, width=60 if c == "ID" else 130, anchor="center" if c != "Name" else "w")
        self.rec_tree.pack(fill=tk.BOTH, expand=True)

        for r in fetch_recurring():
            self.rec_tree.insert("", tk.END, values=(r[0], r[1], r[2], f"Rs.{r[3]:,.0f}"))

    def save_budget_settings(self):
        try:
            b = float(self.set_budget_var.get())
            s = float(self.set_savings_var.get())
            d = int(float(self.set_days_var.get()))
            if b <= 0 or s < 0 or d <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter positive numbers for Budget Limit, Savings Goal, and Days (>=1).")
            return

        update_setting("monthly_budget_limit", b)
        update_setting("savings_goal", s)
        update_setting("days_until_salary", d)
        messagebox.showinfo("Saved", "Budget limit, savings goal, and salary countdown updated!")
        self.show_view("budget")

    def add_recurring_item(self):
        name = self.rec_name_var.get().strip()
        try:
            amt = float(self.rec_amt_var.get())
            if not name or amt <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a bill name and positive monthly amount.")
            return

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("INSERT INTO recurring (name, r_type, amount) VALUES (?, ?, ?)", (name, self.rec_type_var.get(), amt))
        conn.commit()
        conn.close()
        self.show_view("budget")

    def delete_recurring_item(self):
        sel = self.rec_tree.selection()
        if not sel:
            return
        rid = int(self.rec_tree.item(sel[0], "values")[0])
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("DELETE FROM recurring WHERE id=?", (rid,))
        conn.commit()
        conn.close()
        self.show_view("budget")

    # ==========================================================================
    # VIEW 4: RANDOM SURVIVAL SIMULATOR & SIMPLE MONTHLY REPORT
    # ==========================================================================
    def build_simulator_view(self):
        m = calculate_all_metrics()
        careful_curve, shock_curve, shock_log = simulate_remaining_days(
            m["spendable_after_savings"], m["days_left"], m["daily_limit"]
        )

        hdr = tk.Frame(self.main_area, bg=COLORS["WHITE"])
        hdr.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            hdr, text="Expense Runway Simulator (`random`) & Monthly Report",
            font=("Arial", 16, "bold"), bg=COLORS["WHITE"], fg=COLORS["TEXT_DARK"]
        ).pack(side=tk.LEFT)

        tk.Button(
            hdr, text="🎲 Re-Run Random Simulation", command=lambda: self.show_view("simulator"),
            bg=COLORS["PURPLE"], fg=COLORS["WHITE"], font=("Arial", 9, "bold"), relief=tk.FLAT, padx=12, pady=5
        ).pack(side=tk.RIGHT)

        split_frame = tk.Frame(self.main_area, bg=COLORS["WHITE"])
        split_frame.pack(fill=tk.BOTH, expand=True)

        # Left Card: Visual Day-by-Day Runway Simulation Graph
        sim_card = self.make_card(split_frame, border_col=COLORS["PURPLE"], padx=14, pady=12)
        sim_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(
            sim_card, text=f"Simulated {m['days_left']}-Day Balance Until Next Salary (Green = Careful | Orange = Random Shocks)",
            font=("Arial", 10, "bold"), bg=COLORS["WHITE"], fg=COLORS["PURPLE"]
        ).pack(anchor="w", pady=(0, 6))

        sim_canvas = tk.Canvas(sim_card, width=520, height=340, bg=COLORS["WHITE"], highlightthickness=0)
        sim_canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_simulation_lines(sim_canvas, careful_curve, shock_curve, m["days_left"])

        shock_str = "\n".join(shock_log[:4]) if shock_log else "No major unexpected shocks occurred in this run."
        tk.Label(
            sim_card, text="Random Unexpected Events Simulated:\n" + shock_str,
            justify=tk.LEFT, font=("Consolas", 8), bg=COLORS["WHITE"], fg=COLORS["BROWN"]
        ).pack(anchor="w", pady=(6, 0))

        # Right Card: Simple Printable Monthly Financial Report
        rep_card = self.make_card(split_frame, border_col=COLORS["SKY_BLUE"], padx=14, pady=12)
        rep_card.configure(width=400)
        rep_card.pack(side=tk.LEFT, fill=tk.Y)
        rep_card.pack_propagate(False)

        tk.Label(rep_card, text="📄 Simple Monthly Financial Report", font=("Arial", 11, "bold"), bg=COLORS["WHITE"], fg=COLORS["SKY_BLUE"]).pack(anchor="w", pady=(0, 8))

        report_lines = [
            "==========================================",
            f"   POCKETPULSE MONTHLY SUMMARY REPORT",
            f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "==========================================",
            f"1. INCOME & OBLIGATIONS",
            f"   • Total Monthly Income     : Rs.{m['total_income']:,.2f}",
            f"   • Fixed EMIs               : Rs.{m['total_emi']:,.2f}",
            f"   • Subscriptions            : Rs.{m['total_subs']:,.2f}",
            f"   • Variable Expenses        : Rs.{m['total_variable_expense']:,.2f}",
            f"   • Last 7 Days Spending     : Rs.{m['weekly_expense']:,.2f}",
            f"   • Friend Splits Recovered  : Rs.{m['total_friend_refunds']:,.2f}",
            "------------------------------------------",
            f"2. SAVINGS & SURVIVAL RUNWAY",
            f"   • Remaining Balance        : Rs.{m['remaining_balance']:,.2f}",
            f"   • Target Savings Goal      : Rs.{m['savings_goal']:,.2f}",
            f"   • Spendable After Savings  : Rs.{m['spendable_after_savings']:,.2f}",
            f"   • Days Until Next Salary   : {m['days_left']} days",
            f"   • SAFE DAILY SPEND LIMIT   : Rs.{m['daily_limit']:,.2f} / day",
            "------------------------------------------",
            f"3. NEXT MONTH ACTION PLAN",
            f"   • Status: {m['survival_status']}",
            f"   • {m['avoid_advice']}"
        ]

        rep_box = tk.Text(rep_card, font=("Consolas", 9), bg=COLORS["SIDEBAR_BG"], fg=COLORS["TEXT_DARK"], relief=tk.FLAT, padx=8, pady=8, height=22)
        rep_box.pack(fill=tk.BOTH, expand=True)
        rep_box.insert(tk.END, "\n".join(report_lines))
        rep_box.config(state=tk.DISABLED)

    def draw_simulation_lines(self, canvas, careful_curve, shock_curve, days_left):
        gx1, gy1, gx2, gy2 = 50, 20, 500, 300
        canvas.create_rectangle(gx1, gy1, gx2, gy2, fill=COLORS["WHITE"], outline=COLORS["BORDER"])

        all_pts = careful_curve + shock_curve + [0.0]
        max_v = max(500.0, max(all_pts) * 1.1)
        min_v = min(0.0, min(all_pts) * 1.1)
        span = max(1.0, max_v - min_v)

        def to_xy(idx, val):
            x = gx1 + int((idx / max(1, len(careful_curve) - 1)) * (gx2 - gx1))
            y = gy2 - int(((val - min_v) / span) * (gy2 - gy1 - 20)) - 10
            return x, y

        _, zero_y = to_xy(0, 0)
        canvas.create_line(gx1, zero_y, gx2, zero_y, fill=COLORS["BROWN"], dash=(4, 4), width=1.5)
        canvas.create_text(gx1 - 6, zero_y, text="Rs.0", anchor="e", font=("Arial", 8, "bold"), fill=COLORS["BROWN"])

        for i in range(len(careful_curve) - 1):
            x1, y1 = to_xy(i, careful_curve[i])
            x2, y2 = to_xy(i + 1, careful_curve[i + 1])
            canvas.create_line(x1, y1, x2, y2, fill=COLORS["GREEN"], width=2.5)

            sx1, sy1 = to_xy(i, shock_curve[i])
            sx2, sy2 = to_xy(i + 1, shock_curve[i + 1])
            canvas.create_line(sx1, sy1, sx2, sy2, fill=COLORS["ORANGE"], width=2.5)

        canvas.create_text((gx1 + gx2) // 2, gy2 + 15, text=f"Days Elapsed (Day 0 to Day {days_left})", font=("Arial", 8, "bold"), fill=COLORS["BROWN"])

    # ==========================================================================
    # SIDEBAR QUICK HELPERS (Random Populate & CSV Import/Export)
    # ==========================================================================
    def quick_random_populate(self):
        add_random_sample_expenses(count=5)
        self.show_view("dashboard")

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile="pocket_pulse_transactions.csv")
        if not path:
            return
        rows = fetch_transactions()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "t_date", "t_type", "category", "gross_amount", "friend_split", "net_amount", "notes"])
            writer.writerows(rows)
        messagebox.showinfo("Export Successful", f"Exported {len(rows)} transactions to {path}")

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            count = 0
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    gross = float(row.get("gross_amount", 0.0))
                    split = float(row.get("friend_split", 0.0))
                    net = float(row.get("net_amount", gross - split))
                    cur.execute("""
                        INSERT INTO transactions (t_date, t_type, category, gross_amount, friend_split, net_amount, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row.get("t_date", datetime.now().strftime("%Y-%m-%d")),
                        row.get("t_type", "Expense"),
                        row.get("category", "Food & Dining"),
                        gross, split, net,
                        row.get("notes", "Imported CSV item")
                    ))
                    count += 1
            conn.commit()
            conn.close()
            messagebox.showinfo("Import Successful", f"Imported {count} transactions into SQLite database!")
            self.show_view("dashboard")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import CSV: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PocketPulseApp(root)
    root.mainloop()
