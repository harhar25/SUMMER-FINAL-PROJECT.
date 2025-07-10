import flet as ft
from script.db_connection import DBConnection
from script.auth import login_user, register_user
from script.sentiment_predictor import predict_sentiment
from script.reviews_handler import load_reviews
import joblib
import spacy
from nltk.corpus import stopwords
import re

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words("english"))

current_user_id = None  # Session-like variable

def load_products():
    db = DBConnection()
    db.cursor.execute("SELECT id, name FROM products")
    products = db.cursor.fetchall()
    db.close()
    return [(str(p["id"]), p["name"]) for p in products]

def main(page: ft.Page):
    page.title = "ACLC Sentiment Analyzer"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 800
    page.window_height = 600
    page.scroll = "auto"

    product_options = load_products()

    product_dropdown = ft.Dropdown(
        label="Select a Product",
        width=400,
        options=[ft.dropdown.Option(k, text=v) for k, v in product_options]
    )

    # Dynamic update on focus
    def refresh_product_options(e):
        product_dropdown.options = [ft.dropdown.Option(k, text=v) for k, v in load_products()]
        page.update()

    product_dropdown.on_focus = refresh_product_options

    rating_slider = ft.Slider(
        min=1, max=5, divisions=4, label="{value} Stars", value=5, width=400
    )

    admin_product_name = ft.TextField(label="New Product Name", width=400)
    admin_message = ft.Text(value="", color=ft.Colors.GREEN)

    def add_product(e):
        name = admin_product_name.value.strip()
        if not name:
            admin_message.value = "⚠️ Enter a product name."
            admin_message.color = ft.Colors.RED
        else:
            try:
                db = DBConnection()
                db.cursor.execute("INSERT INTO products (name) VALUES (%s)", (name,))
                db.connection.commit()
                db.close()
                admin_message.value = f"✅ '{name}' added!"
                admin_message.color = ft.Colors.GREEN
                admin_product_name.value = ""
            except Exception as ex:
                admin_message.value = f"❌ Error: {ex}"
                admin_message.color = ft.Colors.RED
        page.update()

    admin_section = ft.Column([
        ft.Text("🛠️ Admin: Add Product", size=20, weight="bold"),
        admin_product_name,
        ft.ElevatedButton(text="Add Product", on_click=add_product),
        admin_message,
    ], spacing=15)


    def show_login():
        page.clean()
        page.add(
            ft.Stack(
                controls=[
                    # 🔹 Fullscreen background image
                    ft.Image(
                        src="assets/aclc_bg.jpg",
                        fit=ft.ImageFit.COVER,
                        expand=True
                    ),
                    # 🔹 Centered login form
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=login_view,
                                padding=30,
                                bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
                                border_radius=15,
                                width=400,
                                shadow=ft.BoxShadow(
                                    blur_radius=20,
                                    color=ft.Colors.BLACK12,
                                    offset=ft.Offset(0, 8)
                                )
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True
                    )
                ],
                expand=True
            )
        )
        page.update()


    def show_register():
        page.clean()
        page.add(register_view)

    def show_dashboard(user_id):
        page.clean()
        refresh_product_options(None)

        reviews_table = create_reviews_table(user_id)

        controls = []

        if user_id == 1:
            # ✅ Admin view: add product + review viewer
            controls = [
                ft.Row([
                    ft.Icon(name=ft.Icons.ADMIN_PANEL_SETTINGS, color=ft.Colors.BLUE_700, size=32),
                    ft.Text("Admin Dashboard", size=26, weight="bold", color=ft.Colors.BLUE_700),
                    logout_btn
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                admin_section,
                ft.Divider(height=20),
                ft.Text("📋 User Review History", size=20, weight="bold"),
                reviews_table
            ]

        else:
            # ✅ Regular user: full dashboard
            controls = [
                dashboard_view,
                ft.Divider(height=20),
                ft.Text("📋 Your Review History", size=20, weight="bold"),
                reviews_table
            ]

        page.add(ft.Column(controls=controls, spacing=20, scroll="auto"))

    # -------------------- LOGIN VIEW --------------------
    login_username = ft.TextField(label="Username", width=300)
    login_password = ft.TextField(label="Password", width=300, password=True, can_reveal_password=True)
    login_message = ft.Text(value="", color=ft.Colors.RED)

    def login(e):
        success, result = login_user(login_username.value, login_password.value)
        if success:
            global current_user_id
            current_user_id = result
            show_dashboard(current_user_id)
        else:
            login_message.value = result
            page.update()

    login_btn = ft.ElevatedButton(text="Login", on_click=login)
    go_register_btn = ft.TextButton(text="No account? Register here", on_click=lambda _: show_register())

    login_username = ft.TextField(
    label="Username",
    width=300,
    on_submit=lambda e: login_password.focus()  # 👈 Focus password field
    )

    login_password = ft.TextField(
        label="Password",
        width=300,
        password=True,
        can_reveal_password=True,
        on_submit=login  # 👈 Submit form when Enter is pressed
    )

    login_view = ft.Column([
        ft.Text("🔐 Login", size=26, weight="bold"),
        login_username,
        login_password,
        login_btn,
        login_message,
        go_register_btn
    ], spacing=20, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # -------------------- REGISTER VIEW --------------------
    reg_username = ft.TextField(label="Username", width=300)
    reg_password = ft.TextField(label="Password", width=300, password=True, can_reveal_password=True)
    reg_message = ft.Text(value="", color=ft.Colors.RED)

    def register(e):
        success, result = register_user(reg_username.value, reg_password.value)
        reg_message.value = result
        if success:
            reg_message.color = ft.Colors.GREEN
        else:
            reg_message.color = ft.Colors.RED
        page.update()

    reg_username = ft.TextField(
    label="Username",
    width=300,
    on_submit=lambda e: reg_password.focus()
)

    reg_password = ft.TextField(
        label="Password",
        width=300,
        password=True,
        can_reveal_password=True,
        on_submit=register
    )

    reg_btn = ft.ElevatedButton(text="Register", on_click=register)
    go_login_btn = ft.TextButton(text="Already have an account? Login", on_click=lambda _: show_login())

    register_view = ft.Column([
        ft.Text("📝 Register", size=26, weight="bold"),
        reg_username,
        reg_password,
        reg_btn,
        reg_message,
        go_login_btn
    ], spacing=20, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # -------------------- DASHBOARD VIEW --------------------
    input_text = ft.TextField(
        label="Write a food review...",
        multiline=True,
        min_lines=3,
        width=600,
        border_radius=10,
        filled=True,
        fill_color=ft.Colors.GREY_100
    )

    result_text = ft.Text(size=20, weight="bold", text_align="center")

    def submit_comment(e):
        review = input_text.value.strip()
        selected_product = product_dropdown.value
        rating = int(rating_slider.value)

        if review and selected_product:
            sentiment = predict_sentiment(
                review,
                user_id=current_user_id,
                product_id=int(selected_product),
                score=rating
            )
            result_text.value = f"Sentiment: {sentiment.upper()}"
            result_text.color = {
                "positive": ft.Colors.GREEN,
                "neutral": ft.Colors.AMBER,
                "negative": ft.Colors.RED
            }.get(sentiment.lower(), ft.Colors.BLUE)

            # ✅ Clear input
            input_text.value = ""
            rating_slider.value = 5
            product_dropdown.value = None

            # 🔁 Refresh the reviews table
            updated_table = create_reviews_table(current_user_id)
            page.controls[-1].controls[-1] = updated_table  # Replace old table
            page.update()
        else:
            result_text.value = "Please complete all fields!"
            result_text.color = ft.Colors.RED
            page.update()

    submit_btn = ft.ElevatedButton(
        text="SUBMIT COMMENT",
        on_click=submit_comment,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        height=45,
        width=200
    )


    logout_btn = ft.TextButton("Logout", on_click=lambda _: show_login())

    dashboard_view = ft.Column([
        ft.Row([
            ft.Icon(name=ft.Icons.SCHOOL, color=ft.Colors.BLUE_700, size=32),
            ft.Text("ACLC Sentiment Dashboard", size=26, weight="bold", color=ft.Colors.BLUE_700),
            logout_btn
        ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        product_dropdown,
        rating_slider,
        input_text,
        ft.Row([submit_btn], alignment=ft.MainAxisAlignment.CENTER),
        result_text
    ], spacing=25, alignment=ft.MainAxisAlignment.CENTER)

    # Initial screen
    show_login()



    def create_reviews_table(user_id):
        from script.db_connection import DBConnection

        try:
            db = DBConnection()

            if user_id == 1:
                # Admin: see all reviews with user + product info
                query = """
                    SELECT r.review_text, r.score, r.sentiment, r.date_created,
                        u.username, p.name as product_name
                    FROM reviews r
                    JOIN users u ON r.user_id = u.id
                    JOIN products p ON r.product_id = p.id
                    ORDER BY r.date_created DESC
                """
                db.cursor.execute(query)
                results = db.cursor.fetchall()
                db.close()

                if not results:
                    return ft.Text("No reviews submitted yet.", size=14, italic=True)

                rows = []
                for r in results:
                    rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(r["username"])),
                            ft.DataCell(ft.Text(r["product_name"])),
                            ft.DataCell(ft.Text(r["review_text"])),
                            ft.DataCell(ft.Text(str(r["score"]))),
                            ft.DataCell(ft.Text(r["sentiment"].capitalize())),
                            ft.DataCell(ft.Text(str(r["date_created"]).split('.')[0]))
                        ])
                    )

                return ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("User")),
                        ft.DataColumn(ft.Text("Product")),
                        ft.DataColumn(ft.Text("Review")),
                        ft.DataColumn(ft.Text("Rating")),
                        ft.DataColumn(ft.Text("Sentiment")),
                        ft.DataColumn(ft.Text("Date")),
                    ],
                    rows=rows
                )
            else:
                # Regular user: see only their own data
                query = """
                    SELECT r.review_text, r.score, r.date_created
                    FROM reviews r
                    WHERE r.user_id = %s
                    ORDER BY r.date_created DESC
                """
                db.cursor.execute(query, (user_id,))
                results = db.cursor.fetchall()
                db.close()

                if not results:
                    return ft.Text("No reviews yet. Submit one to get started!", size=14, italic=True)

                rows = []
                for r in results:
                    rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(r["review_text"][:30] + ("..." if len(r["review_text"]) > 30 else ""))),
                            ft.DataCell(ft.Text(str(r["score"]))),
                            ft.DataCell(ft.Text(str(r["date_created"]).split('.')[0]))
                        ])
                    )

                return ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Review")),
                        ft.DataColumn(ft.Text("Rating")),
                        ft.DataColumn(ft.Text("Date")),
                    ],
                    rows=rows
                )

        except Exception as e:
            return ft.Text(f"⚠️ Failed to load reviews: {e}")

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)


