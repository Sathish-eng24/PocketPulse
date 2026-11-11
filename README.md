# 💳 PocketPulse — Personal Finance, Budget & Survival Tracker

> *A lightweight, offline-first personal finance desktop application in Python featuring SQLite persistence, friend bill-splitting, recurring EMI/subscription tracking, daily survival budgeting, and randomized cashflow simulation.*

---

## 🚀 Overview

**PocketPulse** is a beginner-friendly, full-featured desktop expense and budget tracker built entirely with Python's standard library (`tkinter`, `sqlite3`, `random`, `csv`, and `datetime`). It requires zero external third-party packages to run, stores all financial records locally in an automatically generated SQLite database (`finance_data.db`), and calculates how much you can safely spend per day until your next salary or pocket money payout.

---

## ✨ Key Features

* **Modern 4-View Sidebar Interface:** Clean navigation across **📊 Dashboard Overview**, **📝 Income & Expenses**, **⚙️ Budget, EMIs & Goal**, and **🎲 Simulator & Report** built on a crisp White (`#FFFFFF`) background with semantic Sky Blue, Green, Orange, Purple, and Brown accents.
* **Complete CRUD Operations with Input Validation:** Add, edit, and delete both **Income** and **Expense** records with strict validation for dates (`YYYY-MM-DD`) and positive amounts.
* **Friend Bill-Splitting & Refund Mapping:** Enter the total bill paid and any friend split reimbursement so only your true net share (`gross_amount - friend_split`) counts against your budget.
* **Search & Multi-Filter Transaction History:** Instantly search notes, dates, or categories and filter records by transaction type (`All`, `Expense`, `Income`) or specific category.
* **Weekly & Monthly Spending Summaries:** Tracks both your last 7 days of spending and total monthly outflow, triggering automatic visual alerts when variable expenses exceed your monthly budget limit.
* **Recurring Subscriptions & EMI Tracker:** Dedicated manager for fixed monthly commitments (EMIs, rent, OTT subscriptions, mobile plans) that automatically deducts from your disposable balance.
* **Savings Goal & Safe Daily Spending Limit Calculator:** Locks away your target monthly savings first and divides the remaining spendable balance by the exact number of days left until your next salary or pocket money day:
  $$\text{Safe Daily Limit} = \frac{\text{Total Income} - \text{Variable Expenses} - \text{EMIs \& Subscriptions} - \text{Savings Goal}}{\text{Days Until Next Salary}}$$
* **Custom Canvas Visualizations:**
  * **Category-Wise Donut Pie Chart:** Displays exact spending percentages per category.
  * **Monthly Spending Bar Graph:** Compares monthly totals against a dashed horizontal budget limit line.
* **Stochastic Runway Simulator (`random` module):**
  * **1-Click Random Expense Generator:** Populates realistic sample transactions using `random.choice()` and `random.randint()` for quick testing.
  * **Day-by-Day Survival Simulator:** Uses `random.uniform()` and `random.random()` to compare a **Careful Spending Curve (Green)** against an **Unplanned Shocks Curve (Orange)** over the remaining days of the month.
* **Local SQLite Persistence & CSV Import/Export:** Automatically saves all changes to `finance_data.db` and supports 1-click CSV import and export.
* **Printable Monthly Financial Report:** Generates a clean, formatted summary of income, obligations, friend splits recovered, survival runway, and actionable lifestyle recommendations.

---

## 🛠️ Tech Stack & Requirements

* **Language:** Python 3.x
* **GUI Framework:** `tkinter` & `tkinter.ttk` (Standard Library)
* **Database:** `sqlite3` (Standard Library — auto-creates `finance_data.db`)
* **Simulation & Data I/O:** `random`, `csv`, `datetime` (Standard Library)

---

## 📂 Project Structure

```text
PocketPulse/
├── code/
│   └── pocket_pulse.py      # Complete application (SQLite, Math Engine, Simulator & Tkinter UI)
├── finance_data.db          # Auto-generated SQLite database (created on first run)
└── README.md                # Project documentation
```

---

## 🏃‍♂️ How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mallidimohan41297/PocketPulse.git
   cd PocketPulse
   ```

2. **Run the application:**
   ```bash
   python3 code/pocket_pulse.py
   ```
   *(No `pip install` is required — the application runs out-of-the-box on any standard Python 3 installation.)*

3. **Exploring the App:**
   * **📊 Dashboard Overview:** View your 6 KPI cards, budget alert banner, category donut chart, and monthly bar graph.
   * **📝 Income & Expenses:** Add new transactions, log friend bill-splits, click any row to edit/delete, or filter by category and keyword.
   * **⚙️ Budget, EMIs & Goal:** Update your monthly variable budget limit, savings goal, days until next salary, and recurring EMIs/subscriptions.
   * **🎲 Simulator & Report:** Click **Re-Run Random Simulation** to test your remaining cashflow against random expense shocks and view your formatted Monthly Summary Report.
   * **Sidebar Quick Actions:** Click **🎲 +5 Random Spends** to generate test data, or use **📂 Import CSV** / **💾 Export CSV** to back up your ledger.

---

## 👤 Author

**Mallidi Mohan Siva Venkata Rama Reddy**  
*Indian Institute of Technology Goa*  
GitHub: [@mallidimohan41297](https://github.com/mallidimohan41297)
