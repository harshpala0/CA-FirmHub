"""Database layer using sqlite3 with WAL mode for LAN concurrency."""
import sqlite3
from config import DB_PATH

def get_db():
    try:
        from flask import g
        if 'db' not in g:
            g.db = _make_connection()
        return g.db
    except RuntimeError:
        return _make_connection()

def _make_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn

def close_db(exc=None):
    try:
        from flask import g
        db = g.pop('db', None)
        if db:
            db.close()
    except RuntimeError:
        pass

def dict_row(row):
    if row is None:
        return None
    return dict(row)

def dict_rows(rows):
    return [dict(r) for r in rows]

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'Member' CHECK(role IN ('Admin','Team Leader','Member','Client')),
        is_active INTEGER DEFAULT 1,
        client_id INTEGER REFERENCES clients(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, pan TEXT, gstin TEXT, address TEXT,
        contact_person TEXT, contact_phone TEXT, contact_email TEXT,
        is_active INTEGER DEFAULT 1,
        created_by_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS engagements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL REFERENCES clients(id),
        title TEXT NOT NULL, engagement_type TEXT NOT NULL,
        financial_year TEXT NOT NULL, period_from TEXT, period_to TEXT,
        team_leader_id INTEGER REFERENCES users(id),
        status TEXT DEFAULT 'Active', notes TEXT,
        created_by_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS engagement_teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        engagement_id INTEGER NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES users(id),
        role_in_engagement TEXT DEFAULT 'Member'
    );
    CREATE TABLE IF NOT EXISTS audit_programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, engagement_type TEXT NOT NULL, description TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS audit_checklist_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER NOT NULL REFERENCES audit_programs(id) ON DELETE CASCADE,
        sr_no INTEGER NOT NULL, area TEXT NOT NULL, description TEXT NOT NULL,
        reference TEXT, priority TEXT DEFAULT 'Medium'
    );
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        engagement_id INTEGER NOT NULL REFERENCES engagements(id),
        checklist_item_id INTEGER REFERENCES audit_checklist_items(id),
        title TEXT NOT NULL, description TEXT, area TEXT,
        assignee_id INTEGER REFERENCES users(id),
        status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','In Progress','Completed','Under Review','Approved','Rejected')),
        priority TEXT DEFAULT 'Medium', due_date TEXT, completed_at TIMESTAMP,
        working_paper_ref TEXT,
        created_by_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        author_id INTEGER NOT NULL REFERENCES users(id),
        content TEXT NOT NULL, is_query INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        engagement_id INTEGER NOT NULL REFERENCES engagements(id),
        comment_id INTEGER REFERENCES comments(id),
        sr_no INTEGER NOT NULL, query_text TEXT NOT NULL, response TEXT,
        status TEXT DEFAULT 'Open' CHECK(status IN ('Open','Responded','Closed')),
        raised_by_id INTEGER NOT NULL REFERENCES users(id),
        raised_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        responded_by_id INTEGER REFERENCES users(id),
        responded_date TIMESTAMP, task_reference TEXT
    );
    CREATE TABLE IF NOT EXISTS file_uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        filename TEXT NOT NULL, original_filename TEXT NOT NULL,
        file_path TEXT NOT NULL, file_size INTEGER, mime_type TEXT,
        uploaded_by_id INTEGER NOT NULL REFERENCES users(id),
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        reviewer_id INTEGER NOT NULL REFERENCES users(id),
        action TEXT NOT NULL CHECK(action IN ('Approved','Rejected')),
        remarks TEXT, reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        action TEXT NOT NULL, entity_type TEXT, entity_id INTEGER,
        details TEXT, ip_address TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_tasks_engagement ON tasks(engagement_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
    CREATE INDEX IF NOT EXISTS idx_comments_task ON comments(task_id);
    CREATE INDEX IF NOT EXISTS idx_queries_engagement ON queries(engagement_id);
    CREATE INDEX IF NOT EXISTS idx_audit_logs_ts ON audit_logs(timestamp);
    """)
    db.commit()

    cols = [r[1] for r in db.execute("PRAGMA table_info(users)").fetchall()]
    if 'client_id' not in cols:
        db.execute("ALTER TABLE users ADD COLUMN client_id INTEGER REFERENCES clients(id)")
        db.commit()

    needs_rebuild = False
    try:
        db.execute("SAVEPOINT role_test")
        db.execute("INSERT INTO users (username,full_name,password_hash,role) VALUES ('__role_test__','t','t','Client')")
        db.execute("DELETE FROM users WHERE username='__role_test__'")
        db.execute("RELEASE SAVEPOINT role_test")
        db.commit()
    except Exception:
        db.execute("ROLLBACK TO SAVEPOINT role_test")
        db.execute("RELEASE SAVEPOINT role_test")
        needs_rebuild = True

    if needs_rebuild:
        db.execute("PRAGMA foreign_keys=OFF")
        db.executescript("""
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL, full_name TEXT NOT NULL, email TEXT,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Member' CHECK(role IN ('Admin','Team Leader','Member','Client')),
            is_active INTEGER DEFAULT 1, client_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO users_new (id,username,full_name,email,password_hash,role,is_active,client_id,created_at)
            SELECT id,username,full_name,email,password_hash,role,is_active,
                   CASE WHEN EXISTS(SELECT 1 FROM pragma_table_info('users') WHERE name='client_id') THEN client_id ELSE NULL END,
                   created_at FROM users;
        DROP TABLE users; ALTER TABLE users_new RENAME TO users;
        """)
        db.execute("PRAGMA foreign_keys=ON")
        db.commit()


def init_subscriptions_table(db):
    """
    Enhanced subscription table (v4).
    New vs v3: firm_name, firm_reg_no, expires_at, activated.
    - activated=0 means first-run: app will prompt for Subscription ID once only.
    - expires_at: 'YYYY-MM-DD'; NULL = unlimited. Renewal just extends this date.
    - Data is NEVER erased on renewal.
    """
    db.executescript("""
    CREATE TABLE IF NOT EXISTS subscription_ids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sub_id TEXT UNIQUE NOT NULL,
        label TEXT,
        firm_name TEXT NOT NULL DEFAULT '',
        firm_reg_no TEXT NOT NULL DEFAULT '',
        is_active INTEGER DEFAULT 1,
        expires_at TEXT,
        activated INTEGER DEFAULT 0,
        created_by_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_used_at TIMESTAMP,
        use_count INTEGER DEFAULT 0
    );
    CREATE INDEX IF NOT EXISTS idx_sub_ids_active ON subscription_ids(sub_id, is_active);
    """)
    db.commit()

    # Migration: add new columns for existing v3 databases
    existing = [r[1] for r in db.execute("PRAGMA table_info(subscription_ids)").fetchall()]
    migrations = {
        "firm_name":  "ALTER TABLE subscription_ids ADD COLUMN firm_name TEXT NOT NULL DEFAULT ''",
        "firm_reg_no":"ALTER TABLE subscription_ids ADD COLUMN firm_reg_no TEXT NOT NULL DEFAULT ''",
        "expires_at": "ALTER TABLE subscription_ids ADD COLUMN expires_at TEXT",
        "activated":  "ALTER TABLE subscription_ids ADD COLUMN activated INTEGER DEFAULT 0",
    }
    for col, sql in migrations.items():
        if col not in existing:
            db.execute(sql)
    db.commit()


def init_v5_tables(db):
    """New tables for v5 upgrade: time tracking, invoices, doc register, compliance calendar, alerts."""
    db.executescript("""
    -- Time tracking per task
    CREATE TABLE IF NOT EXISTS time_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES users(id),
        date TEXT NOT NULL,
        hours REAL NOT NULL,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_time_logs_task ON time_logs(task_id);
    CREATE INDEX IF NOT EXISTS idx_time_logs_user ON time_logs(user_id);

    -- Invoice / fee management
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        engagement_id INTEGER NOT NULL REFERENCES engagements(id),
        client_id INTEGER NOT NULL REFERENCES clients(id),
        invoice_no TEXT NOT NULL,
        invoice_date TEXT NOT NULL,
        description TEXT,
        amount REAL NOT NULL,
        gst_percent REAL DEFAULT 18.0,
        gst_amount REAL DEFAULT 0,
        total_amount REAL NOT NULL,
        payment_status TEXT DEFAULT 'Unpaid' CHECK(payment_status IN ('Unpaid','Partial','Paid')),
        payment_date TEXT,
        payment_note TEXT,
        created_by_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_invoices_engagement ON invoices(engagement_id);
    CREATE INDEX IF NOT EXISTS idx_invoices_client ON invoices(client_id);

    -- Document inward/outward register
    CREATE TABLE IF NOT EXISTS doc_register (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        engagement_id INTEGER REFERENCES engagements(id),
        client_id INTEGER REFERENCES clients(id),
        doc_type TEXT NOT NULL CHECK(doc_type IN ('Inward','Outward')),
        doc_name TEXT NOT NULL,
        doc_category TEXT,
        doc_date TEXT NOT NULL,
        received_from TEXT,
        sent_to TEXT,
        reference_no TEXT,
        status TEXT DEFAULT 'Received' CHECK(status IN ('Received','Acknowledged','Dispatched','Returned','Pending')),
        remarks TEXT,
        created_by_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_doc_reg_engagement ON doc_register(engagement_id);
    CREATE INDEX IF NOT EXISTS idx_doc_reg_client ON doc_register(client_id);

    -- Compliance / statutory calendar
    CREATE TABLE IF NOT EXISTS compliance_calendar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        due_date TEXT NOT NULL,
        description TEXT,
        financial_year TEXT,
        engagement_id INTEGER REFERENCES engagements(id),
        is_recurring INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Upcoming' CHECK(status IN ('Upcoming','Completed','Missed')),
        created_by_id INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_compliance_due ON compliance_calendar(due_date);

    -- Multi-assignee support for tasks
    CREATE TABLE IF NOT EXISTS task_assignees (
        task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (task_id, user_id)
    );
    CREATE INDEX IF NOT EXISTS idx_task_assignees_task ON task_assignees(task_id);
    CREATE INDEX IF NOT EXISTS idx_task_assignees_user ON task_assignees(user_id);
    """)
    db.commit()

    # Migration: add estimated_hours to tasks if missing
    cols = [r[1] for r in db.execute("PRAGMA table_info(tasks)").fetchall()]
    if 'estimated_hours' not in cols:
        db.execute("ALTER TABLE tasks ADD COLUMN estimated_hours REAL")
        db.commit()
