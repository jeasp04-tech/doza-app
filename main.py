import flet as ft
import json
import os
import time
import random
import asyncio

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
def build_settings_view(page, state, tr, show_menu, show_auth):
    page.clean()
    udata = get_user_data(state["user"])

    async def pick_avatar(e):
        files = await ft.FilePicker().pick_files(allow_multiple=False)
        if files and len(files) > 0:
            update_user_data(state["user"], {"avatar": files[0].path})
            build_settings_view(page, state, tr, show_menu, show_auth)

    def toggle_premium(e):
        update_user_data(state["user"], {"premium": True})
        build_settings_view(page, state, tr, show_menu, show_auth)

    def add_free_stars(e):
        cur = get_user_data(state["user"]).get("stars", 0)
        update_user_data(state["user"], {"stars": cur + 100})
        build_settings_view(page, state, tr, show_menu, show_auth)

    bio_tf = ft.TextField(label=tr("bio"), value=udata.get("bio", ""), width=300)

    def save_bio(e):
        update_user_data(state["user"], {"bio": bio_tf.value.strip()})
        sb = ft.SnackBar(ft.Text("Сохранено!"))
        page.overlay.append(sb)
        sb.open = True
        page.update()

    def change_lang(e):
        state["lang"] = e.control.value
        build_settings_view(page, state, tr, show_menu, show_auth)

    lang_dd = ft.Dropdown(
        label=tr("lang"), width=300, value=state["lang"], on_select=change_lang,
        options=[ft.dropdown.Option("ru", "Русский"), ft.dropdown.Option("uk", "Українська"), ft.dropdown.Option("en", "English")]
    )

    gifts_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)
    for g in udata.get("gifts", []):
        gifts_row.controls.append(
            ft.Container(
                bgcolor="#1c242f", padding=8, border_radius=10,
                content=ft.Column([ft.Text(g["icon"], size=24), ft.Text(f"от {g['from']}", size=10)], horizontal_alignment="center")
            )
        )

    prem_badge = " ⭐" if udata.get("premium") else ""
    prem_btn = ft.Button(
        tr("premium_on") if udata.get("premium") else tr("premium_btn"),
        bgcolor="#9b59b6" if udata.get("premium") else "#2aabee",
        color="white", width=300, on_click=toggle_premium
    )

    header = ft.Container(bgcolor="#1c242f", padding=5, content=ft.Row([
        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: show_menu()),
        ft.Text(tr("settings"), size=18, weight="bold")
    ]))

    content = ft.ListView(expand=True, padding=15, spacing=12, controls=[
        ft.Column([
            ft.CircleAvatar(radius=45, foreground_image_src=udata.get("avatar"), content=ft.Icon(ft.Icons.PERSON, size=40)),
            ft.Text(f"{state['user']}{prem_badge}", size=22, weight="bold"),
            ft.Text(f"Баланс: {udata.get('stars', 0)} ⭐", size=16, color="#f1c40f", weight="bold"),
            ft.Row([
                ft.Button("Фото", on_click=pick_avatar),
                ft.Button(tr("add_stars"), bgcolor="#f39c12", color="white", on_click=add_free_stars)
            ], alignment=ft.MainAxisAlignment.CENTER),
            prem_btn, bio_tf,
            ft.Button(tr("save"), width=300, on_click=save_bio),
            lang_dd,
            ft.Text(tr("gifts_title"), weight="bold"),
            gifts_row if gifts_row.controls else ft.Text("Пока нет подарков", color="gray", size=12),
            ft.Button(tr("logout"), bgcolor="#e74c3c", color="white", width=300, on_click=lambda _: show_auth())
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12)
    ])
    page.add(header, content)

def build_create_room_view(page, state, tr, show_menu, open_room):
    page.clean()
    name_tf = ft.TextField(label=tr("room_name"), width=300)
    type_rg = ft.RadioGroup(value="group", content=ft.Column([
        ft.Radio(value="group", label=tr("group")),
        ft.Radio(value="channel", label=tr("channel"))
    ]))

    def create_submit(e):
        if not name_tf.value.strip():
            return
        rooms = load_json(ROOMS_FILE, {})
        rid = f"room_{int(time.time() * 1000)}"
        rooms[rid] = {"name": name_tf.value.strip(), "type": type_rg.value, "owner": state["user"], "members": [state["user"]]}
        save_json(ROOMS_FILE, rooms)
        open_room(rid)

    header = ft.Container(bgcolor="#1c242f", padding=5, content=ft.Row([
        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: show_menu()),
        ft.Text(tr("new_room"), size=18, weight="bold")
    ]))
    page.add(header, ft.Container(ft.Column([
        name_tf, type_rg,
        ft.Button(tr("create"), bgcolor="#2aabee", color="white", width=300, on_click=create_submit)
    ], spacing=20), padding=20))

def open_gift_dialog(page, state, partner, on_sent):
    udata = get_user_data(state["user"])
    my_stars = udata.get("stars", 0)

    def buy_gift(gift):
        if my_stars < gift["price"]:
            dlg.title = ft.Text("Недостаточно звезд! Пополните в настройках", color="red", size=14)
            page.update()
            return
        update_user_data(state["user"], {"stars": my_stars - gift["price"]})
        pdata = get_user_data(partner)
        pgifts = pdata.get("gifts", [])
        pgifts.append({"icon": gift["icon"], "name": gift["name"], "from": state["user"]})
        update_user_data(partner, {"gifts": pgifts})
        dlg.open = False
        page.update()
        on_sent(f"🎁 Отправлен подарок в Doza: {gift['icon']} {gift['name']} ({gift['price']}⭐)")

    grid = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=280)
    for g in GIFTS_CATALOG:
        grid.controls.append(
            ft.ListTile(
                leading=ft.Text(g["icon"], size=28), title=ft.Text(g["name"], weight="bold"),
                subtitle=ft.Text(f"{g['price']} ⭐", color="#f1c40f"), bgcolor="#1c242f",
                on_click=lambda _, item=g: buy_gift(item)
            )
        )

    dlg = ft.AlertDialog(
        title=ft.Text(f"Подарок для {partner} (Баланс: {my_stars}⭐)", size=15), content=grid,
        actions=[ft.TextButton("Закрыть", on_click=lambda _: setattr(dlg, "open", False) or page.update())]
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()

def open_story_dialog(page, state, show_menu):
    st_tf = ft.TextField(label="Текст вашей истории (24ч)", width=260)

    def post_story(e):
        if not st_tf.value.strip():
            return
        stories = load_json(STORIES_FILE, [])
        stories.append({"user": state["user"], "text": st_tf.value.strip(), "ts": time.time()})
        save_json(STORIES_FILE, stories)
        dlg.open = False
        page.update()
        show_menu()

    dlg = ft.AlertDialog(
        title=ft.Text("Новая история в Doza"), content=st_tf,
        actions=[
            ft.TextButton("Отмена", on_click=lambda _: setattr(dlg, "open", False) or page.update()),
            ft.Button("Опубликовать", bgcolor="#2aabee", color="white", on_click=post_story)
        ]
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()
def show_menu_screen(page, state, tr, show_auth):
    state["target"] = None
    page.clean()
    udata = get_user_data(state["user"])
    prem_badge = " ⭐" if udata.get("premium") else ""

    stories_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=10)
    stories_row.controls.append(
        ft.GestureDetector(
            on_tap=lambda _: open_story_dialog(page, state, lambda: show_menu_screen(page, state, tr, show_auth)),
            content=ft.Column([
                ft.CircleAvatar(bgcolor="#2aabee", content=ft.Icon(ft.Icons.ADD, color="white")),
                ft.Text(tr("add_story"), size=11)
            ], horizontal_alignment="center")
        )
    )
    for st in reversed(load_json(STORIES_FILE, [])):
        if time.time() - st["ts"] < 86400:
            def view_st(s=st):
                d = ft.AlertDialog(title=ft.Text(f"История: {s['user']}"), content=ft.Text(s["text"], size=16))
                page.overlay.append(d)
                d.open = True
                page.update()
            stories_row.controls.append(
                ft.GestureDetector(
                    on_tap=lambda _, item=st: view_st(item),
                    content=ft.Column([
                        ft.CircleAvatar(bgcolor="#9b59b6", content=ft.Text(st["user"][0].upper(), weight="bold")),
                        ft.Text(st["user"][:8], size=11)
                    ], horizontal_alignment="center")
                )
            )

    def set_tab(k):
        state["tab"] = k
        show_menu_screen(page, state, tr, show_auth)

    tabs_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=5)
    for t_key in ["all", "dm", "groups", "channels", "saved"]:
        is_act = state["tab"] == t_key
        tabs_row.controls.append(
            ft.Button(tr(t_key), bgcolor="#2aabee" if is_act else "#1c242f", color="white", on_click=lambda _, k=t_key: set_tab(k))
        )

    chat_list = ft.ListView(expand=True, spacing=4)
    search_tf = ft.TextField(hint_text=tr("search"), border_radius=20, bgcolor="#1c242f", border_width=0, height=40)

    def open_dm(partner):
        state["target"] = {"type": "dm", "id": get_dm_id(state["user"], partner), "partner": partner}
        state["last_msg_count"] = -1
        show_chat_screen(page, state, tr, show_auth)

    def open_room(rid):
        state["target"] = {"type": "room", "id": rid}
        state["last_msg_count"] = -1
        show_chat_screen(page, state, tr, show_auth)

    def build_list(e=None):
        chat_list.controls.clear()
        q = search_tf.value.strip().lower()
        users = load_json(USERS_FILE, {})
        msgs = load_json(MESSAGES_FILE, {})
        rooms = load_json(ROOMS_FILE, {})

        if state["tab"] == "saved" and not q:
            chat_list.controls.append(
                ft.ListTile(
                    leading=ft.CircleAvatar(bgcolor="#2aabee", content=ft.Icon(ft.Icons.BOOKMARK, color="white")),
                    title=ft.Text(tr("saved"), weight="bold"), subtitle=ft.Text("Ваши личные заметки"),
                    bgcolor="#1c242f", on_click=lambda _: open_dm(state["user"])
                )
            )
            page.update()
            return

        if q:
            for u in users:
                if u != state["user"] and q in u.lower():
                    ud = get_user_data(u)
                    b = " ⭐" if ud.get("premium") else ""
                    chat_list.controls.append(
                        ft.ListTile(
                            leading=ft.CircleAvatar(foreground_image_src=ud.get("avatar"), content=ft.Icon(ft.Icons.PERSON)),
                            title=ft.Text(f"{u}{b}", weight="bold"), subtitle=ft.Text(get_status_text(u, state["lang"])),
                            bgcolor="#1c242f", on_click=lambda _, user=u: open_dm(user)
                        )
                    )
            for rid, r in rooms.items():
                if q in r["name"].lower():
                    ic = ft.Icons.CAMPAIGN if r["type"] == "channel" else ft.Icons.GROUP
                    chat_list.controls.append(
                        ft.ListTile(
                            leading=ft.CircleAvatar(bgcolor="#2b5278", content=ft.Icon(ic, color="white")),
                            title=ft.Text(r["name"], weight="bold"), subtitle=ft.Text(f"{len(r['members'])} уч."),
                            bgcolor="#1c242f", on_click=lambda _, room_id=rid: open_room(room_id)
                        )
                    )
        else:
            if state["tab"] in ["all", "groups", "channels"]:
                for rid, r in rooms.items():
                    if state["user"] in r.get("members", []):
                        if state["tab"] == "groups" and r["type"] != "group":
                            continue
                        if state["tab"] == "channels" and r["type"] != "channel":
                            continue
                        ic = ft.Icons.CAMPAIGN if r["type"] == "channel" else ft.Icons.GROUP
                        rm = msgs.get(rid, [])
                        sub = f"{rm[-1]['sender']}: {rm[-1]['text']}" if rm else r["type"]
                        chat_list.controls.append(
                            ft.ListTile(
                                leading=ft.CircleAvatar(bgcolor="#2b5278", content=ft.Icon(ic, color="white")),
                                title=ft.Text(r["name"], weight="bold"), subtitle=ft.Text(sub, max_lines=1),
                                bgcolor="#1c242f", on_click=lambda _, room_id=rid: open_room(room_id)
                            )
                        )
            if state["tab"] in ["all", "dm"]:
                for cid, cm in msgs.items():
                    if cid.startswith("dm_") and cm:
                        parts = cid[3:].split("_")
                        if len(parts) == 2 and state["user"] in parts:
                            partner = parts[1] if parts[0] == state["user"] else parts[0]
                            if partner == state["user"]:
                                continue
                            ud = get_user_data(partner)
                            b = " ⭐" if ud and ud.get("premium") else ""
                            chat_list.controls.append(
                                ft.ListTile(
                                    leading=ft.CircleAvatar(foreground_image_src=ud.get("avatar") if ud else None, content=ft.Icon(ft.Icons.PERSON)),
                                    title=ft.Text(f"{partner}{b}", weight="bold"), subtitle=ft.Text(f"{cm[-1]['sender']}: {cm[-1]['text']}", max_lines=1),
                                    bgcolor="#1c242f", on_click=lambda _, p=partner: open_dm(p)
                                )
                            )
        page.update()

    search_tf.on_change = build_list
    build_list()

    back_menu = lambda: show_menu_screen(page, state, tr, show_auth)
    header = ft.Container(
        bgcolor="#1c242f", padding=10,
        content=ft.Row([
            ft.CircleAvatar(foreground_image_src=udata.get("avatar"), content=ft.Icon(ft.Icons.PERSON)),
            ft.Text(f"Doza • {state['user']}{prem_badge}", size=17, weight="bold", expand=True),
            ft.IconButton(ft.Icons.EDIT, icon_color="#2aabee", on_click=lambda _: build_create_room_view(page, state, tr, back_menu, open_room)),
            ft.IconButton(ft.Icons.SETTINGS, on_click=lambda _: build_settings_view(page, state, tr, back_menu, show_auth))
        ])
    )
    page.add(header, ft.Container(stories_row, padding=8), ft.Container(search_tf, padding=ft.Padding.symmetric(horizontal=10)), ft.Container(tabs_row, padding=8), chat_list)
def show_chat_screen(page, state, tr, show_auth):
    page.clean()
    t_info = state["target"]
    rooms = load_json(ROOMS_FILE, {})
    is_dm = t_info["type"] == "dm"
    partner = t_info.get("partner", "")

    if is_dm:
        ud = get_user_data(partner)
        b = " ⭐" if ud and ud.get("premium") else ""
        title_str = tr("saved") if partner == state["user"] else f"{partner}{b}"
        sub_str = get_status_text(partner, state["lang"])
    else:
        title_str = rooms[t_info["id"]]["name"]
        sub_str = f"{len(rooms[t_info['id']]['members'])} уч."

    status_txt = ft.Text(sub_str, size=12, color="#2aabee")
    msgs_col = ft.ListView(expand=True, spacing=8, auto_scroll=True, padding=10)
    msg_tf = ft.TextField(hint_text=tr("msg_ph"), expand=True, bgcolor="#242f3d", border_width=0, border_radius=20)

    def add_reaction(idx, emoji):
        all_m = load_json(MESSAGES_FILE, {})
        lst = all_m.get(t_info["id"], [])
        if 0 <= idx < len(lst):
            lst[idx]["react"] = emoji
            save_json(MESSAGES_FILE, all_m)
            load_msgs(force=True)

    def load_msgs(force=False):
        all_m = load_json(MESSAGES_FILE, {}).get(t_info["id"], [])
        if not force and len(all_m) == state["last_msg_count"]:
            return
        state["last_msg_count"] = len(all_m)
        msgs_col.controls.clear()
        for idx, m in enumerate(all_m):
            is_me = m["sender"] == state["user"]
            react_badge = ft.Text(m.get("react", ""), size=14) if m.get("react") else ft.Container()
            msgs_col.controls.append(
                ft.Row([
                    ft.GestureDetector(
                        on_double_tap=lambda _, i=idx: add_reaction(i, "❤️"),
                        content=ft.Container(
                            bgcolor="#2b5278" if is_me else "#182533",
                            padding=10, border_radius=12,
                            content=ft.Column([
                                ft.Text(m["sender"], size=11, color="#2aabee", weight="bold"),
                                ft.Text(m["text"], size=14),
                                react_badge
                            ], spacing=2)
                        )
                    )
                ], alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START)
            )
        page.update()

    def send_text(txt):
        if not txt.strip():
            return
        if txt.startswith("/calc "):
            try:
                expr = txt[6:].strip()
                res = eval(expr, {"__builtins__": None}, {})
                txt = f"🧮 {expr} = {res}"
            except Exception:
                txt = "❌ Ошибка в примере"
        elif txt.strip() == "/flip":
            txt = f"🪙 Монетка Doza: {random.choice(['Орёл', 'Решка'])}"
        elif txt.strip() == "/dice":
            txt = f"🎲 Кубик Doza: выпало {random.randint(1, 6)}"

        all_m = load_json(MESSAGES_FILE, {})
        all_m.setdefault(t_info["id"], []).append({"sender": state["user"], "text": txt.strip()})
        save_json(MESSAGES_FILE, all_m)
        load_msgs(force=True)

    def send_click(e):
        send_text(msg_tf.value)
        msg_tf.value = ""
        page.update()

    msg_tf.on_submit = send_click
    t_info["refresh_fn"] = load_msgs
    t_info["status_ctrl"] = status_txt

    gift_btn = ft.IconButton(
        ft.Icons.CARD_GIFTCARD, icon_color="#f1c40f",
        visible=(is_dm and partner != state["user"]),
        on_click=lambda _: open_gift_dialog(page, state, partner, send_text)
    )

    if not is_dm:
        r = rooms[t_info["id"]]
        if state["user"] not in r["members"]:
            def join_room(e):
                r["members"].append(state["user"])
                save_json(ROOMS_FILE, rooms)
                show_chat_screen(page, state, tr, show_auth)
            bottom_area = ft.Button(tr("join"), bgcolor="#2aabee", color="white", width=340, on_click=join_room)
        elif r["type"] == "channel" and r["owner"] != state["user"]:
            bottom_area = ft.Text(tr("only_admin"), color="gray")
        else:
            bottom_area = ft.Row([msg_tf, ft.IconButton(ft.Icons.SEND, icon_color="#2aabee", on_click=send_click)])
    else:
        bottom_area = ft.Row([gift_btn, msg_tf, ft.IconButton(ft.Icons.SEND, icon_color="#2aabee", on_click=send_click)])

    header = ft.Container(bgcolor="#1c242f", padding=8, content=ft.Row([
        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: show_menu_screen(page, state, tr, show_auth)),
        ft.Column([ft.Text(title_str, size=16, weight="bold"), status_txt], spacing=1, expand=True)
    ]))
    page.add(header, msgs_col, ft.Container(bottom_area, bgcolor="#1c242f", padding=8))
    load_msgs(force=True)

async def main(page: ft.Page):
    page.title = "Doza"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0e1621"
    page.window.width = 390
    page.window.height = 780

    state = {"user": "", "lang": "ru", "is_reg": False, "target": None, "tab": "all", "last_msg_count": -1}
    tr = lambda key: TEXTS[state["lang"]][key]

    def show_auth():
        state["target"] = None
        state["user"] = ""
        page.clean()
        nick_tf = ft.TextField(label=tr("nick"), width=300)
        pwd_tf = ft.TextField(label=tr("pwd"), password=True, can_reveal_password=True, width=300)
        err_txt = ft.Text("", color="red")

        def submit(e):
            users = load_json(USERS_FILE, {})
            n = nick_tf.value.strip().replace("_", "-")
            p = pwd_tf.value.strip()
            if not n or not p:
                err_txt.value = "Заполните все поля"
                page.update()
                return
            if state["is_reg"]:
                if n in users:
                    err_txt.value = "Ник уже занят"
                    page.update()
                    return
                users[n] = {"pwd": p, "stars": 200, "premium": False, "bio": "Привет! Я в Doza", "gifts": [], "avatar": None}
                save_json(USERS_FILE, users)
            else:
                ud = get_user_data(n)
                if not ud or ud.get("pwd") != p:
                    err_txt.value = "Неверный логин или пароль"
                    page.update()
                    return
            state["user"] = n
            update_last_seen(n)
            show_menu_screen(page, state, tr, show_auth)

        def toggle_reg(e):
            state["is_reg"] = not state["is_reg"]
            show_auth()

        page.add(ft.Column([
            ft.Icon(ft.Icons.BOLT_ROUNDED, size=65, color="#2aabee"),
            ft.Text("DOZA", size=32, weight="bold", color="#2aabee"),
            ft.Text(tr("reg") if state["is_reg"] else tr("login"), size=20),
            nick_tf, pwd_tf, err_txt,
            ft.Button(tr("create") if state["is_reg"] else tr("enter"), width=300, bgcolor="#2aabee", color="white", on_click=submit),
            ft.TextButton(tr("has_acc") if state["is_reg"] else tr("no_acc"), on_click=toggle_reg)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True))

    async def bg_sync():
        while True:
            await asyncio.sleep(2)
            if state["user"]:
                update_last_seen(state["user"])
                if state["target"] and "refresh_fn" in state["target"]:
                    if state["target"]["type"] == "dm":
                        state["target"]["status_ctrl"].value = get_status_text(state["target"]["partner"], state["lang"])
                    state["target"]["refresh_fn"](force=False)

    page.run_task(bg_sync)
    show_auth()

ft.run(main)
