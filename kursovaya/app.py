import os
import re
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, Response, flash, redirect, render_template, request, session, url_for


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "events.db"
PHONE_RE = re.compile(r"\D")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "12345678")
SUPPORTED_LANGS = ("ru", "kk", "en")

I18N = {
    "ru": {
        "status_closed": "Регистрация закрыта",
        "status_sold_out": "Мест нет",
        "status_open": "Регистрация открыта",
        "tag_closed": "Завершено",
        "tag_sold_out": "Sold Out",
        "tag_open": "Открыто",
        "flash_invalid_event": "Проверьте форму создания: дата должна быть в будущем, цена и лимит мест корректные.",
        "flash_event_created": "Мероприятие успешно создано.",
        "flash_invalid_reg": "Проверьте форму регистрации: имя, телефон и email обязательны.",
        "flash_event_not_found": "Мероприятие не найдено.",
        "flash_reg_closed": "Время регистрации истекло. Это мероприятие уже началось.",
        "flash_no_spots": "Свободных мест больше нет.",
        "flash_reg_success": "Вы успешно зарегистрированы",
        "flash_auth_error": "Неверный логин или пароль.",
        "flash_admin_update_error": "Не удалось обновить: проверьте поля мероприятия.",
        "flash_admin_updated": "Мероприятие обновлено.",
        "flash_admin_deleted": "Мероприятие удалено.",
    },
    "kk": {
        "status_closed": "Тіркелу жабық",
        "status_sold_out": "Орын жоқ",
        "status_open": "Тіркелу ашық",
        "tag_closed": "Аяқталды",
        "tag_sold_out": "Sold Out",
        "tag_open": "Ашық",
        "flash_invalid_event": "Форманы тексеріңіз: күн болашақта болуы керек, баға мен орын саны дұрыс болуы тиіс.",
        "flash_event_created": "Іс-шара сәтті құрылды.",
        "flash_invalid_reg": "Тіркеу формасын тексеріңіз: аты, телефон және email міндетті.",
        "flash_event_not_found": "Іс-шара табылмады.",
        "flash_reg_closed": "Тіркелу уақыты аяқталды. Іс-шара басталып кетті.",
        "flash_no_spots": "Бос орын қалмады.",
        "flash_reg_success": "Сіз сәтті тіркелдіңіз",
        "flash_auth_error": "Логин немесе құпия сөз қате.",
        "flash_admin_update_error": "Жаңарту сәтсіз: өрістерді тексеріңіз.",
        "flash_admin_updated": "Іс-шара жаңартылды.",
        "flash_admin_deleted": "Іс-шара өшірілді.",
    },
    "en": {
        "status_closed": "Registration closed",
        "status_sold_out": "Sold out",
        "status_open": "Registration open",
        "tag_closed": "Closed",
        "tag_sold_out": "Sold Out",
        "tag_open": "Open",
        "flash_invalid_event": "Check the event form: date must be in the future and price/capacity must be valid.",
        "flash_event_created": "Event created successfully.",
        "flash_invalid_reg": "Check registration form: name, phone and email are required.",
        "flash_event_not_found": "Event not found.",
        "flash_reg_closed": "Registration time is over. This event has already started.",
        "flash_no_spots": "No spots left.",
        "flash_reg_success": "You have successfully registered",
        "flash_auth_error": "Invalid username or password.",
        "flash_admin_update_error": "Update failed: please verify event fields.",
        "flash_admin_updated": "Event updated.",
        "flash_admin_deleted": "Event deleted.",
    },
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_lang():
    lang = request.args.get("lang")
    if lang in SUPPORTED_LANGS:
        session["lang"] = lang
        return lang
    session_lang = session.get("lang", "ru")
    if session_lang in SUPPORTED_LANGS:
        return session_lang
    header_lang = (request.headers.get("Accept-Language") or "").lower()
    if header_lang.startswith("kk"):
        session["lang"] = "kk"
        return "kk"
    if header_lang.startswith("en"):
        session["lang"] = "en"
        return "en"
    return "ru"


def tr(key: str) -> str:
    lang = get_lang()
    return I18N.get(lang, I18N["ru"]).get(key, I18N["ru"].get(key, key))


@app.context_processor
def inject_i18n():
    lang = get_lang()
    return {"lang": lang, "t": tr, "supported_langs": SUPPORTED_LANGS}


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_datetime TEXT NOT NULL,
            description TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
        """
    )
    conn.commit()
    ensure_event_columns(conn)

    count = cur.execute("SELECT COUNT(*) AS c FROM events").fetchone()["c"]
    if count == 0:
        seed = [
            (
                "Startup Meetup Almaty",
                "2026-05-08T18:30",
                "Нетворкинг, питч-сессии и практические кейсы от локальных IT-команд.",
                "Алматы, Smart Point",
                5000,
                120,
            ),
            (
                "Frontend Day",
                "2026-05-15T11:00",
                "Интенсив по современному React, UX-паттернам и производительности интерфейсов.",
                "Алматы, Tech Garden",
                7000,
                90,
            ),
            (
                "Business Strategy Workshop",
                "2026-05-20T14:00",
                "Мастер-класс по разработке бизнес-стратегий и масштабированию компании.",
                "Алматы, Astana Hub",
                12000,
                45,
            ),
            (
                "Community Hackathon",
                "2026-05-25T09:00",
                "48-часовой хакатон для решения социальных проблем города.",
                "Алматы, Digital Khan",
                3000,
                150,
            ),
            (
                "Creative Design Summit",
                "2026-06-01T10:30",
                "Саммит дизайнеров с мастер-классами по UI/UX и графическому дизайну.",
                "Алматы, Art Space",
                8500,
                75,
            ),
            (
                "AI & Machine Learning Conference",
                "2026-06-05T13:00",
                "Конференция по искусственному интеллекту и машинному обучению.",
                "Алматы, Nazarbayev University",
                15000,
                200,
            ),
            (
                "Marketing Masterclass",
                "2026-06-10T16:00",
                "Интенсивный курс по цифровому маркетингу и продвижению.",
                "Алматы, Business Center",
                6500,
                60,
            ),
            (
                "Blockchain & Crypto Meetup",
                "2026-06-15T18:00",
                "Встреча энтузиастов блокчейна и обсуждение трендов крипторынка.",
                "Алматы, Crypto Hub",
                4000,
                80,
            ),
            (
                "Photography Workshop",
                "2026-06-20T11:00",
                "Практический мастер-класс по фотографированию и обработке снимков.",
                "Алматы, Photo Studio",
                5500,
                25,
            ),
            (
                "Startup Pitch Day",
                "2026-06-25T15:00",
                "День питчинга стартапов перед инвесторами и экспертами.",
                "Алматы, Innovation Center",
                18000,
                100,
            ),
        ]
        cur.executemany(
            """
            INSERT INTO events (title, event_datetime, description, location, price, capacity)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            seed,
        )
        conn.commit()
    conn.close()


def admin_required(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return handler(*args, **kwargs)

    return wrapper


def normalize_phone(phone: str) -> str:
    return PHONE_RE.sub("", phone or "")


def get_event_columns(conn):
    rows = conn.execute("PRAGMA table_info(events)").fetchall()
    return {row["name"] for row in rows}


def ensure_event_columns(conn):
    columns = get_event_columns(conn)
    if "location" not in columns:
        conn.execute("ALTER TABLE events ADD COLUMN location TEXT NOT NULL DEFAULT 'Онлайн'")
    if "price" not in columns:
        conn.execute("ALTER TABLE events ADD COLUMN price INTEGER NOT NULL DEFAULT 0")
    if "capacity" not in columns:
        conn.execute("ALTER TABLE events ADD COLUMN capacity INTEGER NOT NULL DEFAULT 50")
    if "theme" not in columns:
        conn.execute("ALTER TABLE events ADD COLUMN theme TEXT NOT NULL DEFAULT 'theme-tech'")
    conn.commit()


def parse_datetime(value: str):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def is_event_closed(event_datetime: str) -> bool:
    dt = parse_datetime(event_datetime)
    if not dt:
        return True
    return datetime.now() >= dt


def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_event_theme(event_id: int, price: int, saved_theme: str = None) -> str:
    # Используем сохраненную тему из базы данных, если она есть
    if saved_theme:
        return saved_theme
    # Для старых мероприятий без темы используем автоматическое определение
    if price >= 15000:
        return "theme-premium"
    themes = ["theme-tech", "theme-business", "theme-community", "theme-creative"]
    return themes[event_id % len(themes)]


def build_event_filters():
    q = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    availability = request.args.get("availability", "all").strip()
    sort = request.args.get("sort", "soon").strip()
    return q, location, availability, sort, get_lang()


def valid_event_payload(title: str, event_datetime: str, description: str, location: str, price: str, capacity: str) -> bool:
    if not title or len(title) < 3:
        return False
    if not description or len(description) < 10:
        return False
    if not location or len(location) < 3:
        return False
    if not event_datetime:
        return False
    dt = parse_datetime(event_datetime)
    if not dt:
        return False
    if dt <= datetime.now():
        return False
    try:
        p = int(price)
        c = int(capacity)
    except ValueError:
        return False
    if p < 0 or c < 1:
        return False
    return True


def valid_registration_payload(name: str, phone: str, email: str) -> bool:
    if not name or len(name) < 2:
        return False
    if len(normalize_phone(phone)) < 10:
        return False
    if not EMAIL_RE.match(email or ""):
        return False
    return True


@app.get("/")
def index():
    q, location, availability, sort, _ = build_event_filters()
    sort_expr = {
        "soon": "e.event_datetime ASC",
        "late": "e.event_datetime DESC",
        "price_low": "e.price ASC",
        "price_high": "e.price DESC",
    }.get(sort, "e.event_datetime ASC")

    where_parts = []
    params = []
    if q:
        where_parts.append("(e.title LIKE ? OR e.description LIKE ?)")
        like_q = f"%{q}%"
        params.extend([like_q, like_q])
    if location:
        where_parts.append("e.location = ?")
        params.append(location)
    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

    conn = get_db()
    events = conn.execute(
        f"""
        SELECT
            e.id,
            e.title,
            e.event_datetime,
            e.description,
            e.location,
            e.price,
            e.capacity,
            e.theme,
            COUNT(r.id) AS registrations_count
        FROM events e
        LEFT JOIN registrations r ON r.event_id = e.id
        {where_sql}
        GROUP BY e.id
        ORDER BY {sort_expr}
        """,
        params,
    ).fetchall()
    total_regs = conn.execute("SELECT COUNT(*) AS c FROM registrations").fetchone()["c"]
    locations = conn.execute("SELECT DISTINCT location FROM events ORDER BY location ASC").fetchall()
    prepared_events = []
    for event in events:
        event_dict = dict(event)
        event_dict["closed"] = is_event_closed(event_dict["event_datetime"])
        spots_left = max(event_dict["capacity"] - event_dict["registrations_count"], 0)
        event_dict["spots_left"] = spots_left
        event_dict["theme"] = get_event_theme(event_dict["id"], event_dict["price"], event_dict.get("theme"))
        if event_dict["closed"]:
            event_dict["status_text"] = tr("status_closed")
            event_dict["event_tag"] = tr("tag_closed")
        elif spots_left == 0:
            event_dict["status_text"] = tr("status_sold_out")
            event_dict["event_tag"] = tr("tag_sold_out")
        else:
            event_dict["status_text"] = tr("status_open")
            event_dict["event_tag"] = tr("tag_open")
        if availability == "open" and (event_dict["closed"] or spots_left == 0):
            continue
        if availability == "closed" and not (event_dict["closed"] or spots_left == 0):
            continue
        prepared_events.append(event_dict)

    conn.close()
    return render_template(
        "index.html",
        events=prepared_events,
        total_regs=total_regs,
        locations=[row["location"] for row in locations],
        filters={"q": q, "location": location, "availability": availability, "sort": sort},
    )


@app.post("/events")
def create_event():
    title = request.form.get("title", "").strip()
    event_datetime = request.form.get("event_datetime", "").strip()
    description = request.form.get("description", "").strip()
    location = request.form.get("location", "").strip()
    price = request.form.get("price", "0").strip()
    capacity = request.form.get("capacity", "50").strip()
    theme = request.form.get("theme", "theme-tech").strip()

    if not valid_event_payload(title, event_datetime, description, location, price, capacity):
        flash(tr("flash_invalid_event"), "error")
        return redirect(url_for("index", lang=get_lang()) + "#create")

    conn = get_db()
    ensure_event_columns(conn)
    conn.execute(
        """
        INSERT INTO events (title, event_datetime, description, location, price, capacity, theme)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (title, event_datetime, description, location, int(price), int(capacity), theme),
    )
    conn.commit()
    conn.close()

    flash(tr("flash_event_created"), "success")
    return redirect(url_for("index", lang=get_lang()) + "#events")


@app.post("/register/<int:event_id>")
def register(event_id: int):
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()

    if not valid_registration_payload(name, phone, email):
        flash(tr("flash_invalid_reg"), "error")
        return redirect(url_for("index", lang=get_lang()) + "#events")

    conn = get_db()
    event = conn.execute(
        """
        SELECT e.id, e.event_datetime, e.capacity, COUNT(r.id) AS registrations_count
        FROM events e
        LEFT JOIN registrations r ON r.event_id = e.id
        WHERE e.id = ?
        GROUP BY e.id
        """,
        (event_id,),
    ).fetchone()
    if not event:
        conn.close()
        flash(tr("flash_event_not_found"), "error")
        return redirect(url_for("index", lang=get_lang()) + "#events")
    if is_event_closed(event["event_datetime"]):
        conn.close()
        flash(tr("flash_reg_closed"), "error")
        return redirect(url_for("index", lang=get_lang()) + "#events")
    if event["registrations_count"] >= event["capacity"]:
        conn.close()
        flash(tr("flash_no_spots"), "error")
        return redirect(url_for("index", lang=get_lang()) + "#events")

    conn.execute(
        """
        INSERT INTO registrations (event_id, name, phone, email, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (event_id, name, phone, email, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()

    flash(tr("flash_reg_success"), "success")
    return redirect(url_for("index", lang=get_lang()) + "#events")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin_registrations", lang=get_lang()))
        flash(tr("flash_auth_error"), "error")
    return render_template("admin_login.html")


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("index", lang="ru"))


@app.get("/admin/registrations")
@admin_required
def admin_registrations():
    search = request.args.get("q", "").strip()
    where_sql = ""
    params = []
    if search:
        where_sql = "WHERE r.name LIKE ? OR r.email LIKE ? OR r.phone LIKE ? OR e.title LIKE ?"
        like_search = f"%{search}%"
        params = [like_search, like_search, like_search, like_search]

    conn = get_db()
    rows = conn.execute(
        f"""
        SELECT
            r.name,
            r.phone,
            r.email,
            r.created_at,
            e.title AS event_title,
            e.event_datetime,
            e.price
        FROM registrations r
        JOIN events e ON e.id = r.event_id
        {where_sql}
        ORDER BY r.created_at DESC
        """,
        params,
    ).fetchall()
    total_events = conn.execute("SELECT COUNT(*) AS c FROM events").fetchone()["c"]
    total_regs = conn.execute("SELECT COUNT(*) AS c FROM registrations").fetchone()["c"]
    revenue = conn.execute(
        """
        SELECT COALESCE(SUM(e.price), 0) AS total
        FROM registrations r
        JOIN events e ON e.id = r.event_id
        """
    ).fetchone()["total"]
    conn.close()
    return render_template(
        "admin_registrations.html",
        registrations=rows,
        total_events=total_events,
        total_regs=total_regs,
        revenue=revenue,
        search=search,
    )


@app.get("/admin/registrations/export.csv")
@admin_required
def admin_export_registrations():
    conn = get_db()
    rows = conn.execute(
        """
        SELECT
            r.name,
            r.phone,
            r.email,
            r.created_at,
            e.title AS event_title,
            e.event_datetime,
            e.price
        FROM registrations r
        JOIN events e ON e.id = r.event_id
        ORDER BY r.created_at DESC
        """
    ).fetchall()
    conn.close()

    lines = [
        "name,phone,email,event_title,event_datetime,price,created_at",
    ]
    for row in rows:
        values = [
            row["name"],
            row["phone"],
            row["email"],
            row["event_title"],
            row["event_datetime"],
            str(row["price"]),
            row["created_at"],
        ]
        escaped = ['"' + str(v).replace('"', '""') + '"' for v in values]
        lines.append(",".join(escaped))
    csv_data = "\n".join(lines)
    return Response(
        csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=registrations.csv"},
    )


@app.get("/admin/events")
@admin_required
def admin_events():
    conn = get_db()
    rows = conn.execute(
        """
        SELECT
            e.id,
            e.title,
            e.event_datetime,
            e.location,
            e.price,
            e.capacity,
            e.theme,
            COUNT(r.id) AS registrations_count
        FROM events e
        LEFT JOIN registrations r ON r.event_id = e.id
        GROUP BY e.id
        ORDER BY e.event_datetime ASC
        """
    ).fetchall()
    conn.close()
    return render_template("admin_events.html", events=rows)


@app.post("/admin/events/<int:event_id>/update")
@admin_required
def admin_update_event(event_id: int):
    title = request.form.get("title", "").strip()
    event_datetime = request.form.get("event_datetime", "").strip()
    description = request.form.get("description", "").strip()
    location = request.form.get("location", "").strip()
    price = request.form.get("price", "0").strip()
    capacity = request.form.get("capacity", "1").strip()
    theme = request.form.get("theme", "theme-tech").strip()
    if not valid_event_payload(title, event_datetime, description, location, price, capacity):
        flash(tr("flash_admin_update_error"), "error")
        return redirect(url_for("admin_events", lang=get_lang()))

    conn = get_db()
    conn.execute(
        """
        UPDATE events
        SET title = ?, event_datetime = ?, description = ?, location = ?, price = ?, capacity = ?, theme = ?
        WHERE id = ?
        """,
        (title, event_datetime, description, location, parse_int(price), parse_int(capacity, 1), theme, event_id),
    )
    conn.commit()
    conn.close()
    flash(tr("flash_admin_updated"), "success")
    return redirect(url_for("admin_events", lang=get_lang()))


@app.post("/admin/events/<int:event_id>/delete")
@admin_required
def admin_delete_event(event_id: int):
    conn = get_db()
    conn.execute("DELETE FROM registrations WHERE event_id = ?", (event_id,))
    conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    flash(tr("flash_admin_deleted"), "success")
    return redirect(url_for("admin_events", lang=get_lang()))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
