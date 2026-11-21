import json
import os
import time

APP_DIR = os.path.join(os.path.expanduser("~"), ".doza_apk_data")
os.makedirs(APP_DIR, exist_ok=True)

USERS_FILE = os.path.join(APP_DIR, "users.json")
MESSAGES_FILE = os.path.join(APP_DIR, "messages.json")
ROOMS_FILE = os.path.join(APP_DIR, "rooms.json")
STORIES_FILE = os.path.join(APP_DIR, "stories.json")
STATUS_FILE = os.path.join(APP_DIR, "status.json")

GIFTS_CATALOG = [
    {"id": "bear", "icon": "🧸", "name": "Плюшевый мишка", "price": 15},
    {"id": "rose", "icon": "🌹", "name": "Алая роза", "price": 25},
    {"id": "cake", "icon": "🎂", "name": "Праздничный торт", "price": 50},
    {"id": "diamond", "icon": "💎", "name": "Редкий алмаз", "price": 100},
    {"id": "rocket", "icon": "🚀", "name": "Космо-ракета", "price": 250},
    {"id": "crown", "icon": "👑", "name": "Корона Doza", "price": 500},
]

TEXTS = {
    "ru": {
        "login": "Вход в Doza", "reg": "Регистрация в Doza", "nick": "Никнейм", "pwd": "Пароль",
        "enter": "Войти", "create": "Создать аккаунт", "no_acc": "Нет аккаунта? Регистрация",
        "has_acc": "Уже есть аккаунт? Войти", "search": "Поиск в Doza...", "all": "Все",
        "dm": "Личные", "groups": "Группы", "channels": "Каналы", "saved": "Избранное",
        "settings": "Настройки", "lang": "Язык", "logout": "Выйти", "online": "в сети",
        "last_seen": "был(а) в", "msg_ph": "Сообщение (/calc, /flip, /dice)...", "new_room": "Создать",
        "room_name": "Название", "group": "Группа", "channel": "Канал",
        "join": "Вступить / Подписаться", "only_admin": "Только админ может писать",
        "premium_btn": "Активировать Doza Premium (Бесплатно)", "premium_on": "Doza Premium Активен ⭐",
        "add_stars": "+100 Звезд (Бесплатно)", "bio": "О себе", "save": "Сохранить",
        "add_story": "История", "gifts_title": "Мои подарки:"
    },
    "uk": {
        "login": "Вхід у Doza", "reg": "Реєстрація в Doza", "nick": "Нікнейм", "pwd": "Пароль",
        "enter": "Увійти", "create": "Створити акаунт", "no_acc": "Немає акаунту? Реєстрація",
        "has_acc": "Вже є акаунт? Увійти", "search": "Пошук у Doza...", "all": "Усі",
        "dm": "Особисті", "groups": "Групи", "channels": "Канали", "saved": "Вибране",
        "settings": "Налаштування", "lang": "Мова", "logout": "Вийти", "online": "в мережі",
        "last_seen": "був(ла) о", "msg_ph": "Повідомлення (/calc, /flip, /dice)...", "new_room": "Створити",
        "room_name": "Назва", "group": "Група", "channel": "Канал",
        "join": "Вступити / Підписатися", "only_admin": "Тільки адмін може писати",
        "premium_btn": "Активувати Doza Premium (Безкоштовно)", "premium_on": "Doza Premium Активний ⭐",
        "add_stars": "+100 Зірок (Безкоштовно)", "bio": "Про себе", "save": "Зберегти",
        "add_story": "Історія", "gifts_title": "Мої подарунки:"
    },
    "en": {
        "login": "Login to Doza", "reg": "Register in Doza", "nick": "Nickname", "pwd": "Password",
        "enter": "Sign In", "create": "Create Account", "no_acc": "No account? Register",
        "has_acc": "Have account? Login", "search": "Search Doza...", "all": "All",
        "dm": "Chats", "groups": "Groups", "channels": "Channels", "saved": "Saved",
        "settings": "Settings", "lang": "Language", "logout": "Log Out", "online": "online",
        "last_seen": "last seen at", "msg_ph": "Message (/calc, /flip, /dice)...", "new_room": "Create",
        "room_name": "Name", "group": "Group", "channel": "Channel",
        "join": "Join / Subscribe", "only_admin": "Admin only",
        "premium_btn": "Activate Doza Premium (Free)", "premium_on": "Doza Premium Active ⭐",
        "add_stars": "+100 Stars (Free)", "bio": "Bio", "save": "Save",
        "add_story": "Story", "gifts_title": "My gifts:"
    }
}

def load_json(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_data(nick):
    users = load_json(USERS_FILE, {})
    if nick not in users:
        return None
    if isinstance(users[nick], str):
        users[nick] = {"pwd": users[nick], "stars": 200, "premium": False, "bio": "Привет! Я в Doza", "gifts": [], "avatar": None}
        save_json(USERS_FILE, users)
    return users[nick]

def update_user_data(nick, updates):
    users = load_json(USERS_FILE, {})
    if nick in users:
        data = get_user_data(nick)
        data.update(updates)
        users[nick] = data
        save_json(USERS_FILE, users)

def get_dm_id(u1, u2):
    return "dm_" + "_".join(sorted([u1, u2]))

def update_last_seen(username):
    if username:
        st = load_json(STATUS_FILE, {})
        st[username] = time.time()
        save_json(STATUS_FILE, st)

def get_status_text(username, lang="ru"):
    ts = load_json(STATUS_FILE, {}).get(username, 0)
    if not ts:
        return ""
    if time.time() - ts < 10:
        return TEXTS[lang]["online"]
    return f"{TEXTS[lang]['last_seen']} {time.strftime('%H:%M', time.localtime(ts))}"
