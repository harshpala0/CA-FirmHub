"""Seed Data: Default users and predefined audit program checklists."""
from database import get_db
from auth import hash_password

def seed(db):
    # ─── Users ───
    users = [
        ("admin", "System Administrator", "admin@firm.local", hash_password("admin123"), "Admin"),
        ("team.leader", "Team Leader", "tl@firm.local", hash_password("audit123"), "Team Leader"),
        ("member1", "Audit Member 1", "m1@firm.local", hash_password("audit123"), "Member"),
    ]
    for uname, fname, email, pwd, role in users:
        existing = db.execute("SELECT id FROM users WHERE username=?", (uname,)).fetchone()
        if not existing:
            db.execute("INSERT INTO users (username, full_name, email, password_hash, role) VALUES (?,?,?,?,?)",
                       (uname, fname, email, pwd, role))
            print(f"  [SEED] User: {uname} / {'admin123' if uname=='admin' else 'audit123'}")

    # ─── Statutory Audit Program ───
    if not db.execute("SELECT id FROM audit_programs WHERE name='Statutory Audit - Standard'").fetchone():
        db.execute("INSERT INTO audit_programs (name, engagement_type, description) VALUES (?,?,?)",
                   ("Statutory Audit - Standard", "Statutory Audit",
                    "Standard statutory audit checklist as per Companies Act, 2013 and applicable Standards on Auditing"))
        pid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        items = [
            (1,"Planning","Obtain engagement letter and understand terms of engagement","SA 210","High"),
            (2,"Planning","Understand the entity and its environment including internal controls","SA 315","High"),
            (3,"Planning","Perform risk assessment procedures and identify significant risks","SA 315","High"),
            (4,"Planning","Determine materiality levels for the audit","SA 320","High"),
            (5,"Planning","Develop overall audit strategy and detailed audit plan","SA 300","High"),
            (6,"Cash & Bank","Obtain bank confirmation letters for all bank accounts","SA 505","High"),
            (7,"Cash & Bank","Verify bank reconciliation statements as at year-end","","High"),
            (8,"Cash & Bank","Perform cash count and verify cash book balances","","Medium"),
            (9,"Cash & Bank","Review fixed deposits, interest accrued and TDS thereon","","Medium"),
            (10,"Trade Receivables","Obtain age-wise analysis of trade receivables","","High"),
            (11,"Trade Receivables","Send balance confirmation letters to significant debtors","SA 505","High"),
            (12,"Trade Receivables","Review provision for doubtful debts and write-offs","Ind AS 109","High"),
            (13,"Trade Receivables","Verify subsequent realisations post year-end","","Medium"),
            (14,"Inventory","Attend physical stock verification / review management count","SA 501","High"),
            (15,"Inventory","Verify inventory valuation method (cost or NRV whichever lower)","Ind AS 2","High"),
            (16,"Inventory","Review slow-moving and obsolete inventory provisions","","Medium"),
            (17,"Fixed Assets","Verify additions to fixed assets with supporting documents","","High"),
            (18,"Fixed Assets","Check depreciation calculation as per Companies Act and IT Act","Sch II","High"),
            (19,"Fixed Assets","Verify disposals and impairment assessments","Ind AS 36","Medium"),
            (20,"Trade Payables","Obtain age-wise analysis of trade payables","","High"),
            (21,"Trade Payables","Send balance confirmation to significant creditors","SA 505","Medium"),
            (22,"Trade Payables","Verify MSME dues and interest liability under MSMED Act","MSMED Act","High"),
            (23,"Loans & Borrowings","Verify loan agreements, sanction letters and security details","","High"),
            (24,"Loans & Borrowings","Check interest calculation and repayment schedule","","Medium"),
            (25,"Revenue","Verify revenue recognition policy as per applicable standards","Ind AS 115","High"),
            (26,"Revenue","Perform cut-off testing for revenue transactions around year-end","","High"),
            (27,"Revenue","Test sales with supporting invoices, delivery challans and POs","","High"),
            (28,"Expenses","Vouch significant expense items with supporting documentation","","Medium"),
            (29,"Expenses","Review related party transactions and disclosures","Ind AS 24","High"),
            (30,"Expenses","Verify employee benefit obligations (gratuity, leave encashment)","Ind AS 19","High"),
            (31,"Tax","Verify income tax computation and provision for current tax","","High"),
            (32,"Tax","Review deferred tax asset / liability calculation","Ind AS 12","High"),
            (33,"Tax","Check GST reconciliation (GSTR-1 vs GSTR-3B vs books)","","High"),
            (34,"Tax","Verify TDS compliance and reconcile with Form 26AS / AIS","","Medium"),
            (35,"Statutory Compliance","Check compliance with CARO 2020 reporting requirements","CARO 2020","High"),
            (36,"Statutory Compliance","Verify compliance with provisions of Companies Act, 2013","Co. Act 2013","High"),
            (37,"Statutory Compliance","Review minutes of Board meetings and general meetings","","Medium"),
            (38,"Financial Statements","Review draft financial statements for completeness","","High"),
            (39,"Financial Statements","Verify notes to accounts and disclosure requirements","","High"),
            (40,"Financial Statements","Obtain management representation letter","SA 580","High"),
            (41,"Completion","Perform subsequent events review","SA 560","High"),
            (42,"Completion","Evaluate going concern assumption","SA 570","High"),
            (43,"Completion","Perform analytical review procedures at completion stage","SA 520","Medium"),
            (44,"Completion","Prepare audit summary memorandum and form audit opinion","SA 700","High"),
            (45,"Completion","Issue audit report in prescribed format","SA 700/705/706","High"),
        ]
        for sr, area, desc, ref, pri in items:
            db.execute("INSERT INTO audit_checklist_items (program_id, sr_no, area, description, reference, priority) VALUES (?,?,?,?,?,?)",
                       (pid, sr, area, desc, ref, pri))
        print(f"  [SEED] Statutory Audit program: {len(items)} checklist items")

    # ─── Tax Audit Program ───
    if not db.execute("SELECT id FROM audit_programs WHERE name='Tax Audit - 44AB'").fetchone():
        db.execute("INSERT INTO audit_programs (name, engagement_type, description) VALUES (?,?,?)",
                   ("Tax Audit - 44AB", "Tax Audit",
                    "Tax audit checklist as per Section 44AB of the Income Tax Act, 1961"))
        pid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        tax = [
            (1,"Preliminary","Verify applicability of tax audit (turnover threshold)","Sec 44AB","High"),
            (2,"Preliminary","Obtain previous year tax audit report for comparison","","Medium"),
            (3,"Form 3CA/3CB","Determine applicable form (3CA for company, 3CB for others)","","High"),
            (4,"Form 3CD","Clause 1-5: Basic information and registration details","Form 3CD","High"),
            (5,"Form 3CD","Clause 8-9: Previous year details and partners/members info","Form 3CD","Medium"),
            (6,"Form 3CD","Clause 11: Details of changes in accounting policies","Form 3CD","High"),
            (7,"Form 3CD","Clause 12-13: Method of accounting and valuation of closing stock","Form 3CD","High"),
            (8,"Form 3CD","Clause 14: Details under section 43B (disallowances)","Sec 43B","High"),
            (9,"Form 3CD","Clause 17: Amounts debited to P&L - capital vs revenue","Form 3CD","High"),
            (10,"Form 3CD","Clause 20-21: Depreciation details and amounts admissible","Sec 32","High"),
            (11,"Form 3CD","Clause 26: TDS/TCS compliance details","Ch XVII-B","High"),
            (12,"Form 3CD","Clause 27-30: Tax deducted details and specified persons","Form 3CD","High"),
            (13,"Form 3CD","Clause 31: Deemed income details (Sec 32AC, 33AB, etc.)","Form 3CD","Medium"),
            (14,"Form 3CD","Clause 34-36: GST reporting, receipt exceeding limits","Form 3CD","High"),
            (15,"Form 3CD","Clause 40-44: TDS defaults and secondary adjustments","Form 3CD","High"),
            (16,"Completion","Prepare and file Form 3CA/3CB and 3CD on IT portal","","High"),
        ]
        for sr, area, desc, ref, pri in tax:
            db.execute("INSERT INTO audit_checklist_items (program_id, sr_no, area, description, reference, priority) VALUES (?,?,?,?,?,?)",
                       (pid, sr, area, desc, ref, pri))
        print(f"  [SEED] Tax Audit program: {len(tax)} checklist items")

    # ─── Internal Audit ───
    if not db.execute("SELECT id FROM audit_programs WHERE name='Internal Audit - General'").fetchone():
        db.execute("INSERT INTO audit_programs (name, engagement_type, description) VALUES (?,?,?)",
                   ("Internal Audit - General", "Internal Audit",
                    "General internal audit checklist for evaluating internal controls"))
        pid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        internal = [
            (1,"Governance","Review organizational structure and delegation of authority","","High"),
            (2,"Governance","Evaluate adequacy of internal control framework","","High"),
            (3,"Procurement","Review purchase order authorisation process and limits","","High"),
            (4,"Procurement","Verify vendor empanelment and evaluation procedures","","Medium"),
            (5,"Procurement","Check three-quotation policy compliance","","Medium"),
            (6,"HR & Payroll","Verify payroll processing controls and segregation of duties","","High"),
            (7,"HR & Payroll","Review attendance and leave management system","","Medium"),
            (8,"Finance","Evaluate accounts payable and receivable management","","High"),
            (9,"Finance","Review bank reconciliation procedures","","High"),
            (10,"Finance","Check petty cash management controls","","Medium"),
            (11,"IT Controls","Review IT access controls and password policies","","High"),
            (12,"IT Controls","Evaluate data backup and disaster recovery procedures","","High"),
            (13,"Compliance","Review statutory compliance tracker and status","","High"),
            (14,"Reporting","Prepare internal audit report with findings and recommendations","","High"),
        ]
        for sr, area, desc, ref, pri in internal:
            db.execute("INSERT INTO audit_checklist_items (program_id, sr_no, area, description, reference, priority) VALUES (?,?,?,?,?,?)",
                       (pid, sr, area, desc, ref, pri))
        print(f"  [SEED] Internal Audit program: {len(internal)} checklist items")

    db.commit()
    print("  [SEED] Database seeding complete.")
