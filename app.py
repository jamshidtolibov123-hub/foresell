import io
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from Database import (create_tables, check_user, add_user,
                      add_product, get_products, delete_product,
                      update_product, get_product_by_id,
                      add_category, get_categories, delete_category,
                      add_sale, get_sales, get_today_sales, get_monthly_sales,
                      get_weekly_sales_chart, get_top_products,
                      get_sales_by_category, get_total_sales_count,
                      check_subscription, update_subscription, get_forecast,
                      get_all_sales_for_export)

# Jadvallar mavjudligini tekshirish
create_tables()

# Sahifa sozlamalari
st.set_page_config(
    page_title="Foresell",
    page_icon="📊",
    layout="wide"
)

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"


# LOGIN SAHIFASI
def login_page():
    st.title("📊 Foresell")
    st.subheader("Savdo tahlil tizimi")

    tab1, tab2 = st.tabs(["🔐 Kirish", "ℹ️ Ma'lumot"])

    # KIRISH
    # RO'YXATDAN O'TISH
    with tab2:
        st.subheader("Yangi akkount yaratish")

        # MAXFIY KOD
        secret_code = st.text_input("Maxfiy kod", type="password", key="secret")

        if secret_code == "FORESELL1PROJECT":
            new_username = st.text_input("Login", key="new_user")
            new_password = st.text_input("Parol", type="password", key="new_pass")
            new_password2 = st.text_input("Parolni tasdiqlang", type="password", key="new_pass2")
            business_name = st.text_input("Biznes nomi", key="business")

            if st.button("Ro'yxatdan o'tish", type="primary"):
                if not new_username or not new_password or not business_name:
                    st.error("Barcha maydonlarni to'ldiring!")
                elif new_password != new_password2:
                    st.error("Parollar mos emas!")
                elif len(new_password) < 4:
                    st.error("Parol kamida 4 ta belgi bo'lsin!")
                else:
                    if add_user(new_username, new_password, business_name):
                        st.success("Akkount yaratildi! Endi kirishingiz mumkin.")
                    else:
                        st.error("Bu login band!")
        elif secret_code:
            st.error("❌ Maxfiy kod noto'g'ri!")
        else:
            st.info("📞 Maxfiy kodni olish uchun admin bilan bog'laning.")

    # RO'YXATDAN O'TISH
    with tab2:
        st.info("📞 Ro'yxatdan o'tish uchun admin bilan bog'laning.")
        st.write("**Telegram:** @jamshvd")
        st.write("**Telefon:** +998 94 402 03 15")
        st.write("**Email: jamshidtolibov123@gmail.com** ")

# DASHBOARD SAHIFASI
def dashboard():
    # Obuna tekshirish
    subscription_end = check_subscription(st.session_state.user_id)

    st.title("📊 Foresell Dashboard")

    col1, col2 = st.columns([4, 1])
    with col1:
        st.success(f"Xush kelibsiz, {st.session_state.business_name}! 👋")
    with col2:
        if st.button("🚪 Chiqish"):
            st.session_state.logged_in = False
            st.rerun()

    # Obuna holati
    if subscription_end:
        end_date = datetime.strptime(subscription_end, "%Y-%m-%d")
        days_left = (end_date - datetime.now()).days
        if days_left > 0:
            st.info(f"📅 Obuna muddati: {subscription_end} gacha ({days_left} kun qoldi)")
        else:
            st.error("⚠️ Obuna muddati tugagan! Iltimos, obunani yangilang.")

    st.divider()

    # TABLAR
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💰 Sotuv", "📦 Tovarlar", "📁 Kategoriyalar",
        "📊 Statistika", "📈 Hisobotlar", "⚙️ Sozlamalar"
    ])

    # TAB 1: SOTUV
    with tab1:
        st.subheader("Yangi sotuv kiritish")

        products = get_products(st.session_state.user_id)

        if not products:
            st.warning("Avval tovar qo'shing! '📦 Tovarlar' tabiga o'ting.")
        else:
            product_dict = {f"{p[1]} - {p[2]:,.0f} so'm": p for p in products}

            col1, col2 = st.columns(2)
            with col1:
                selected_product = st.selectbox("Tovarni tanlang", list(product_dict.keys()))
            with col2:
                quantity = st.number_input("Miqdori", min_value=1, value=1)

            product = product_dict[selected_product]
            total_price = product[2] * quantity

            st.info(f"💵 Jami summa: **{total_price:,.0f} so'm**")

            if st.button("✅ Sotuvni saqlash", type="primary"):
                add_sale(st.session_state.user_id, product[0], quantity, total_price)
                st.success(f"Sotuv saqlandi! {product[1]} x {quantity} = {total_price:,.0f} so'm")
                st.rerun()

        st.divider()
        st.subheader("Sotuvlar tarixi")

        sales = get_sales(st.session_state.user_id)

        if sales:
            for sale in sales[:10]:
                col1, col2, col3, col4 = st.columns([3, 1, 2, 2])
                with col1:
                    st.write(f"**{sale[1]}**")
                with col2:
                    st.write(f"{sale[2]} dona")
                with col3:
                    st.write(f"💵 {sale[3]:,.0f} so'm")
                with col4:
                    st.write(f"📅 {sale[4][:10]}")
        else:
            st.info("Hozircha sotuvlar yo'q.")

        # TAB 2: TOVARLAR
        with tab2:
            # Tahrirlash rejimi
            if "edit_product_id" not in st.session_state:
                st.session_state.edit_product_id = None

            # TAHRIRLASH FORMASI
            if st.session_state.edit_product_id:
                product = get_product_by_id(st.session_state.edit_product_id)
                if product:
                    st.subheader("✏️ Tovarni tahrirlash")

                    categories = get_categories(st.session_state.user_id)
                    category_names = [cat[1] for cat in categories]

                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input("Tovar nomi", value=product[1], key="edit_name")
                        new_price = st.number_input("Narxi (so'm)", value=int(product[2]), min_value=0, step=1000,
                                                    key="edit_price")
                    with col2:
                        current_index = category_names.index(product[3]) if product[3] in category_names else 0
                        new_category = st.selectbox("Kategoriya", category_names, index=current_index, key="edit_cat")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Saqlash", type="primary"):
                            if new_name and new_price > 0:
                                update_product(st.session_state.edit_product_id, new_name, new_price, new_category)
                                st.success("Tovar yangilandi!")
                                st.session_state.edit_product_id = None
                                st.rerun()
                            else:
                                st.error("Tovar nomi va narxini kiriting!")
                    with col2:
                        if st.button("❌ Bekor qilish"):
                            st.session_state.edit_product_id = None
                            st.rerun()

                    st.divider()

            # YANGI TOVAR QO'SHISH
            st.subheader("Yangi tovar qo'shish")

            categories = get_categories(st.session_state.user_id)
            category_names = [cat[1] for cat in categories]

            if not category_names:
                st.warning("Avval kategoriya qo'shing! '📁 Kategoriyalar' tabiga o'ting.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    tovar_nomi = st.text_input("Tovar nomi", key="new_product_name")
                    tovar_narxi = st.number_input("Narxi (so'm)", min_value=0, step=1000, key="new_product_price")
                with col2:
                    kategoriya = st.selectbox("Kategoriya", category_names, key="new_product_cat")

                if st.button("➕ Tovar qo'shish", type="primary"):
                    if tovar_nomi and tovar_narxi > 0:
                        add_product(st.session_state.user_id, tovar_nomi, tovar_narxi, kategoriya)
                        st.success(f"'{tovar_nomi}' qo'shildi!")
                        st.rerun()
                    else:
                        st.error("Tovar nomi va narxini kiriting!")

            st.divider()
            st.subheader("Tovarlar ro'yxati")

            # QIDIRUV
            search_query = st.text_input("🔍 Tovar qidirish", placeholder="Tovar nomini yozing...")

            # Tovarlarni olish
            products = get_products(st.session_state.user_id)

            # Qidiruv filtri
            if search_query:
                products = [p for p in products if search_query.lower() in p[1].lower()]

            if products:
                for product in products:
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                    with col1:
                        st.write(f"**{product[1]}**")
                    with col2:
                        st.write(f"{product[2]:,.0f} so'm")
                    with col3:
                        st.write(f"📁 {product[3]}")
                    with col4:
                        if st.button("✏️", key=f"edit_{product[0]}"):
                            st.session_state.edit_product_id = product[0]
                            st.rerun()
                    with col5:
                        if st.button("🗑️", key=f"del_{product[0]}"):
                            delete_product(product[0])
                            st.rerun()
            else:
                st.info("Hozircha tovarlar yo'q.")

    # TAB 3: KATEGORIYALAR
    with tab3:
        st.subheader("Yangi kategoriya qo'shish")

        col1, col2 = st.columns([3, 1])
        with col1:
            yangi_kategoriya = st.text_input("Kategoriya nomi")
        with col2:
            st.write("")
            st.write("")
            if st.button("➕ Qo'shish", type="primary"):
                if yangi_kategoriya:
                    add_category(st.session_state.user_id, yangi_kategoriya)
                    st.success(f"'{yangi_kategoriya}' qo'shildi!")
                    st.rerun()
                else:
                    st.error("Kategoriya nomini kiriting!")

        st.divider()
        st.subheader("Kategoriyalar ro'yxati")

        categories = get_categories(st.session_state.user_id)

        if categories:
            for cat in categories:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"📁 **{cat[1]}**")
                with col2:
                    if st.button("🗑️", key=f"del_cat_{cat[0]}"):
                        delete_category(cat[0])
                        st.rerun()
        else:
            st.info("Hozircha kategoriyalar yo'q.")

    # TAB 4: STATISTIKA
    with tab4:
        products = get_products(st.session_state.user_id)
        categories = get_categories(st.session_state.user_id)
        today_sales = get_today_sales(st.session_state.user_id)
        monthly_sales = get_monthly_sales(st.session_state.user_id)
        total_count = get_total_sales_count(st.session_state.user_id)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📦 Tovarlar", f"{len(products)} ta")
        with col2:
            st.metric("📁 Kategoriyalar", f"{len(categories)} ta")
        with col3:
            st.metric("🧾 Sotuvlar soni", f"{total_count} ta")
        with col4:
            st.metric("💰 Bugungi sotuv", f"{today_sales:,.0f}")
        with col5:
            st.metric("📊 Oylik sotuv", f"{monthly_sales:,.0f}")

    # TAB 5: HISOBOTLAR
    with tab5:
        st.subheader("📈 Oxirgi 7 kunlik sotuvlar")

        weekly_data = get_weekly_sales_chart(st.session_state.user_id)

        if weekly_data:
            df = pd.DataFrame(weekly_data, columns=["Sana", "Summa"])
            st.bar_chart(df.set_index("Sana"))
        else:
            st.info("Hozircha grafik uchun ma'lumot yo'q. Sotuv kiriting!")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏆 Top sotilgan tovarlar")
            top_products = get_top_products(st.session_state.user_id)

            if top_products:
                for i, item in enumerate(top_products, 1):
                    st.write(f"**{i}. {item[0]}** — {item[1]} dona — {item[2]:,.0f} so'm")
            else:
                st.info("Hozircha ma'lumot yo'q.")

        with col2:
            st.subheader("📁 Kategoriya bo'yicha sotuvlar")
            category_sales = get_sales_by_category(st.session_state.user_id)

            if category_sales:
                for item in category_sales:
                    st.write(f"**{item[0]}** — {item[1]:,.0f} so'm")
            else:
                st.info("Hozircha ma'lumot yo'q.")

        st.divider()

        # PROGNOZ
        st.subheader("🔮 Keyingi oy prognozi")
        forecast = get_forecast(st.session_state.user_id)

        if forecast > 0:
            st.success(f"Keyingi oyda taxminan **{forecast:,.0f} so'm** sotuv kutilmoqda")
            st.caption("Bu prognoz oxirgi 30 kunlik o'rtacha sotuvga asoslangan")
        else:
            st.info("Prognoz uchun kamida 1 kunlik sotuv ma'lumoti kerak")

    # TAB 6: SOZLAMALAR
    with tab6:
        st.subheader("⚙️ Sozlamalar")

        st.write(f"**Biznes nomi:** {st.session_state.business_name}")
        st.write(f"**Login:** {st.session_state.username}")

        st.divider()

        st.subheader("📅 Obuna muddatini belgilash")

        new_end_date = st.date_input(
            "Obuna tugash sanasi",
            value=datetime.now() + timedelta(days=30)
        )

        if st.button("💾 Obunani saqlash"):
            update_subscription(st.session_state.user_id, str(new_end_date))
            st.success(f"Obuna {new_end_date} gacha belgilandi!")
            st.rerun()


# ASOSIY MANTIQ
if st.session_state.logged_in:
    dashboard()
else:
    login_page()