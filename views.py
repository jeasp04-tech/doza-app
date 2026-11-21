import flet as ft
import time
from database import (
    ROOMS_FILE, STORIES_FILE, GIFTS_CATALOG,
    load_json, save_json, get_user_data, update_user_data
)

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
            prem_btn,
            bio_tf,
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
                leading=ft.Text(g["icon"], size=28),
                title=ft.Text(g["name"], weight="bold"),
                subtitle=ft.Text(f"{g['price']} ⭐", color="#f1c40f"),
                bgcolor="#1c242f",
                on_click=lambda _, item=g: buy_gift(item)
            )
        )

    dlg = ft.AlertDialog(
        title=ft.Text(f"Подарок для {partner} (Баланс: {my_stars}⭐)", size=15),
        content=grid,
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
        title=ft.Text("Новая история в Doza"),
        content=st_tf,
        actions=[
            ft.TextButton("Отмена", on_click=lambda _: setattr(dlg, "open", False) or page.update()),
            ft.Button("Опубликовать", bgcolor="#2aabee", color="white", on_click=post_story)
        ]
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()
