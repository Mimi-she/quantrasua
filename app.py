import streamlit as st
from datetime import datetime
import html
import uuid


# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Milk Tea POS",
    page_icon="🧋",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DỮ LIỆU QUÁN
# Có thể chỉnh sửa trực tiếp tại đây
# ============================================================

SHOP_NAME = "TRÀ SỮA MILK TEA"
SHOP_ADDRESS = "123 Nguyễn Trãi, Quận 1, TP. Hồ Chí Minh"
SHOP_PHONE = "0909 123 456"

# Danh sách trà sữa
DRINKS = {
    "Trà sữa truyền thống": 30000,
    "Trà sữa trân châu": 35000,
    "Trà sữa matcha": 38000,
    "Trà sữa socola": 38000,
    "Trà sữa khoai môn": 38000,
    "Trà sữa dâu": 38000,
    "Trà sữa caramel": 40000,
    "Trà sữa Oreo": 42000,
    "Trà sữa matcha đậu đỏ": 45000,
    "Trà sữa kem cheese": 45000,
}

# Phụ phí size
SIZE_PRICES = {
    "S": 0,
    "M": 5000,
    "L": 10000,
}

# Topping
TOPPINGS = {
    "Trân châu đen": 5000,
    "Trân châu trắng": 5000,
    "Thạch trái cây": 5000,
    "Thạch dừa": 5000,
    "Pudding trứng": 7000,
    "Pudding socola": 7000,
    "Kem cheese": 10000,
    "Đậu đỏ": 7000,
    "Oreo": 7000,
    "Hạt thủy tinh": 6000,
}

SUGAR_LEVELS = [
    "100% đường",
    "70% đường",
    "50% đường",
    "30% đường",
    "0% đường",
]

ICE_LEVELS = [
    "100% đá",
    "70% đá",
    "50% đá",
    "30% đá",
    "0% đá",
]


# ============================================================
# SESSION STATE
# ============================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "paid_invoice" not in st.session_state:
    st.session_state.paid_invoice = None

if "invoice_history" not in st.session_state:
    st.session_state.invoice_history = []


# ============================================================
# HÀM TIỆN ÍCH
# ============================================================

def format_currency(number):
    """Định dạng tiền VNĐ."""
    return f"{number:,.0f} ₫".replace(",", ".")


def create_invoice_id():
    """Tạo mã hóa đơn."""
    now = datetime.now()
    random_part = uuid.uuid4().hex[:4].upper()
    return f"HD{now.strftime('%Y%m%d%H%M%S')}{random_part}"


def calculate_item_price(drink, size, toppings):
    """Tính giá một loại nước."""
    price = DRINKS[drink]
    price += SIZE_PRICES[size]

    for topping in toppings:
        price += TOPPINGS[topping]

    return price


def add_item_to_cart(drink, size, toppings, sugar, ice, quantity):
    """Thêm sản phẩm vào giỏ hàng."""

    unit_price = calculate_item_price(
        drink,
        size,
        toppings
    )

    item = {
        "drink": drink,
        "size": size,
        "toppings": toppings.copy(),
        "sugar": sugar,
        "ice": ice,
        "quantity": quantity,
        "unit_price": unit_price,
        "total": unit_price * quantity,
    }

    st.session_state.cart.append(item)


def calculate_subtotal():
    """Tính tổng tiền giỏ hàng."""
    return sum(item["total"] for item in st.session_state.cart)


def clear_cart():
    st.session_state.cart = []


def generate_receipt_text(invoice):
    """Tạo nội dung hóa đơn dạng TXT."""

    lines = []

    lines.append("=" * 55)
    lines.append(SHOP_NAME.center(55))
    lines.append(SHOP_ADDRESS.center(55))
    lines.append(f"Điện thoại: {SHOP_PHONE}".center(55))
    lines.append("=" * 55)

    lines.append(f"MÃ HÓA ĐƠN: {invoice['invoice_id']}")
    lines.append(f"Thời gian: {invoice['created_at']}")
    lines.append(f"Khách hàng: {invoice['customer_name']}")
    lines.append("-" * 55)

    for index, item in enumerate(invoice["items"], 1):
        lines.append(
            f"{index}. {item['drink']} - Size {item['size']}"
        )

        lines.append(
            f"   SL: {item['quantity']} x "
            f"{format_currency(item['unit_price'])}"
        )

        if item["toppings"]:
            lines.append(
                "   Topping: " + ", ".join(item["toppings"])
            )

        lines.append(
            f"   Đường: {item['sugar']} | Đá: {item['ice']}"
        )

        lines.append(
            f"   Thành tiền: {format_currency(item['total'])}"
        )

    lines.append("-" * 55)
    lines.append(
        f"TẠM TÍNH: {format_currency(invoice['subtotal'])}"
    )

    if invoice["discount"] > 0:
        lines.append(
            f"GIẢM GIÁ: -{format_currency(invoice['discount'])}"
        )

    lines.append(
        f"TỔNG THANH TOÁN: {format_currency(invoice['total'])}"
    )

    lines.append("=" * 55)
    lines.append("Cảm ơn quý khách đã ủng hộ!")
    lines.append("=" * 55)

    return "\n".join(lines)


def generate_receipt_html(invoice):
    """Tạo hóa đơn HTML để tải xuống/in."""

    rows = ""

    for index, item in enumerate(invoice["items"], 1):

        topping_text = (
            ", ".join(item["toppings"])
            if item["toppings"]
            else "Không"
        )

        rows += f"""
        <tr>
            <td>{index}</td>
            <td>
                <strong>{html.escape(item["drink"])}</strong><br>
                Size {html.escape(item["size"])}<br>
                <small>
                    Topping: {html.escape(topping_text)}<br>
                    Đường: {html.escape(item["sugar"])} |
                    Đá: {html.escape(item["ice"])}
                </small>
            </td>
            <td style="text-align:center">
                {item["quantity"]}
            </td>
            <td style="text-align:right">
                {format_currency(item["unit_price"])}
            </td>
            <td style="text-align:right">
                {format_currency(item["total"])}
            </td>
        </tr>
        """

    discount_row = ""

    if invoice["discount"] > 0:
        discount_row = f"""
        <tr>
            <td colspan="4" class="text-right">
                Giảm giá
            </td>
            <td class="text-right discount">
                -{format_currency(invoice["discount"])}
            </td>
        </tr>
        """

    receipt = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">

<title>Hóa đơn {invoice["invoice_id"]}</title>

<style>

body {{
    font-family: Arial, sans-serif;
    background: #f5f5f5;
    margin: 0;
    padding: 30px;
}}

.receipt {{
    max-width: 850px;
    margin: auto;
    background: white;
    padding: 35px;
    border-radius: 10px;
}}

.header {{
    text-align: center;
    margin-bottom: 25px;
}}

.header h1 {{
    margin-bottom: 5px;
}}

.info {{
    margin: 20px 0;
    padding: 15px;
    background: #f7f7f7;
    border-radius: 8px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    padding: 12px 8px;
    border-bottom: 1px solid #ddd;
    vertical-align: top;
}}

th {{
    background: #f0f0f0;
}}

.text-right {{
    text-align: right;
}}

.discount {{
    color: #d93025;
}}

.total {{
    font-size: 22px;
    font-weight: bold;
}}

.footer {{
    margin-top: 35px;
    text-align: center;
    color: #666;
}}

@media print {{

    body {{
        background: white;
        padding: 0;
    }}

    .receipt {{
        box-shadow: none;
        max-width: none;
    }}

}}

</style>

</head>

<body>

<div class="receipt">

<div class="header">

<h1>{html.escape(SHOP_NAME)}</h1>

<div>{html.escape(SHOP_ADDRESS)}</div>

<div>Điện thoại: {html.escape(SHOP_PHONE)}</div>

<h2>HÓA ĐƠN THANH TOÁN</h2>

</div>


<div class="info">

<strong>Mã hóa đơn:</strong>
{html.escape(invoice["invoice_id"])}
<br>

<strong>Thời gian:</strong>
{html.escape(invoice["created_at"])}
<br>

<strong>Khách hàng:</strong>
{html.escape(invoice["customer_name"])}

</div>


<table>

<thead>

<tr>
<th>#</th>
<th>Sản phẩm</th>
<th>Số lượng</th>
<th>Đơn giá</th>
<th>Thành tiền</th>
</tr>

</thead>

<tbody>

{rows}

<tr>

<td colspan="4" class="text-right">
Tạm tính
</td>

<td class="text-right">
{format_currency(invoice["subtotal"])}
</td>

</tr>

{discount_row}

<tr>

<td colspan="4" class="text-right total">
TỔNG THANH TOÁN
</td>

<td class="text-right total">
{format_currency(invoice["total"])}
</td>

</tr>

</tbody>

</table>


<div class="footer">

<p>Cảm ơn quý khách đã ủng hộ!</p>

<p>Hẹn gặp lại quý khách ❤️</p>

</div>

</div>

</body>

</html>
"""

    return receipt


# ============================================================
# CSS GIAO DIỆN
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #777;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .price-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #f5f5f5;
        text-align: center;
        font-size: 22px;
        font-weight: bold;
    }

    .total-box {
        padding: 20px;
        border-radius: 12px;
        background-color: #fff3e6;
        border: 1px solid #ffd5a8;
    }

    .invoice-title {
        text-align: center;
        font-size: 30px;
        font-weight: bold;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🧋 Milk Tea POS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Hệ thống tính tiền & quản lý hóa đơn quán trà sữa</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🏪 Thông tin quán")

    st.write(f"**{SHOP_NAME}**")
    st.write(SHOP_ADDRESS)
    st.write(f"☎️ {SHOP_PHONE}")

    st.divider()

    st.subheader("📊 Giỏ hàng")

    st.metric(
        "Số loại nước",
        len(st.session_state.cart)
    )

    st.metric(
        "Tổng tiền",
        format_currency(calculate_subtotal())
    )

    if st.button(
        "🗑️ Xóa toàn bộ giỏ hàng",
        use_container_width=True
    ):

        clear_cart()

        st.session_state.paid_invoice = None

        st.rerun()


# ============================================================
# TAB
# ============================================================

tab_order, tab_invoice, tab_history = st.tabs(
    [
        "🧋 Tạo đơn hàng",
        "🧾 Hóa đơn",
        "📚 Lịch sử hóa đơn"
    ]
)


# ============================================================
# TAB 1 - TẠO ĐƠN
# ============================================================

with tab_order:

    st.subheader("👤 Thông tin khách hàng")

    customer_name = st.text_input(
        "Tên khách hàng",
        placeholder="Ví dụ: Nguyễn Văn An",
        key="customer_name"
    )

    st.divider()

    st.subheader("🥤 Thêm món")

    col1, col2 = st.columns(2)

    with col1:

        drink = st.selectbox(
            "Loại trà sữa",
            list(DRINKS.keys())
        )

        size = st.radio(
            "Size ly",
            list(SIZE_PRICES.keys()),
            horizontal=True
        )

        sugar = st.select_slider(
            "Mức độ đường",
            options=SUGAR_LEVELS,
            value="70% đường"
        )

    with col2:

        toppings = st.multiselect(
            "Topping",
            options=list(TOPPINGS.keys()),
            format_func=lambda x: f"{x} (+{format_currency(TOPPINGS[x])})"
        )

        ice = st.select_slider(
            "Mức độ đá",
            options=ICE_LEVELS,
            value="70% đá"
        )

        quantity = st.number_input(
            "Số lượng",
            min_value=1,
            max_value=100,
            value=1,
            step=1
        )

    # Tính giá trước khi thêm
    current_unit_price = calculate_item_price(
        drink,
        size,
        toppings
    )

    st.markdown(
        f"""
        <div class="price-box">
        Đơn giá: {format_currency(current_unit_price)}
        &nbsp;&nbsp;|&nbsp;&nbsp;
        Thành tiền: {format_currency(current_unit_price * quantity)}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    if st.button(
        "➕ THÊM MÓN VÀO HÓA ĐƠN",
        type="primary",
        use_container_width=True
    ):

        add_item_to_cart(
            drink=drink,
            size=size,
            toppings=toppings,
            sugar=sugar,
            ice=ice,
            quantity=quantity
        )

        st.success(
            f"Đã thêm {quantity} x {drink} vào hóa đơn."
        )

        st.rerun()

    # ========================================================
    # GIỎ HÀNG
    # ========================================================

    st.divider()

    st.subheader("🛒 Danh sách món trong hóa đơn")

    if not st.session_state.cart:

        st.info(
            "Chưa có món nào. Hãy chọn món ở phía trên và bấm 'Thêm món vào hóa đơn'."
        )

    else:

        for index, item in enumerate(
            st.session_state.cart
        ):

            with st.container(border=True):

                col_a, col_b, col_c = st.columns(
                    [5, 2, 1]
                )

                with col_a:

                    st.markdown(
                        f"### {index + 1}. {item['drink']}"
                    )

                    st.write(
                        f"Size: **{item['size']}**"
                    )

                    st.write(
                        f"Đường: **{item['sugar']}** | "
                        f"Đá: **{item['ice']}**"
                    )

                    if item["toppings"]:

                        st.write(
                            "Topping: **" +
                            ", ".join(item["toppings"]) +
                            "**"
                        )

                    else:

                        st.write(
                            "Topping: **Không**"
                        )

                with col_b:

                    st.write(
                        f"SL: **{item['quantity']}**"
                    )

                    st.write(
                        f"Đơn giá: **{format_currency(item['unit_price'])}**"
                    )

                    st.write(
                        f"Thành tiền: **{format_currency(item['total'])}**"
                    )

                with col_c:

                    if st.button(
                        "🗑️ Xóa",
                        key=f"delete_{index}"
                    ):

                        st.session_state.cart.pop(index)

                        st.rerun()

        # ====================================================
        # TỔNG TIỀN
        # ====================================================

        st.divider()

        subtotal = calculate_subtotal()

        discount = st.number_input(
            "🏷️ Giảm giá",
            min_value=0,
            max_value=subtotal,
            value=0,
            step=1000,
            format="%d"
        )

        total = subtotal - discount

        st.markdown(
            f"""
            <div class="total-box">

            <h3>💰 Tổng thanh toán</h3>

            <p>
            Tạm tính:
            <strong>{format_currency(subtotal)}</strong>
            </p>

            <p>
            Giảm giá:
            <strong>-{format_currency(discount)}</strong>
            </p>

            <h2>
            Tổng cộng:
            {format_currency(total)}
            </h2>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        # ====================================================
        # THANH TOÁN
        # ====================================================

        if st.button(
            "💳 THANH TOÁN & TẠO HÓA ĐƠN",
            type="primary",
            use_container_width=True
        ):

            if not customer_name.strip():

                st.error(
                    "Vui lòng nhập tên khách hàng trước khi thanh toán."
                )

            elif not st.session_state.cart:

                st.error(
                    "Hóa đơn chưa có món."
                )

            else:

                invoice = {

                    "invoice_id": create_invoice_id(),

                    "created_at":
                        datetime.now().strftime(
                            "%d/%m/%Y %H:%M:%S"
                        ),

                    "customer_name":
                        customer_name.strip(),

                    "items":
                        [
                            item.copy()
                            for item
                            in st.session_state.cart
                        ],

                    "subtotal":
                        subtotal,

                    "discount":
                        discount,

                    "total":
                        total
                }

                st.session_state.paid_invoice = invoice

                st.session_state.invoice_history.insert(
                    0,
                    invoice
                )

                st.session_state.cart = []

                st.success(
                    "Thanh toán thành công! Hóa đơn đã được tạo."
                )

                st.balloons()


# ============================================================
# TAB 2 - HÓA ĐƠN
# ============================================================

with tab_invoice:

    invoice = st.session_state.paid_invoice

    if invoice is None:

        st.info(
            "Chưa có hóa đơn. Hãy tạo đơn hàng và bấm Thanh toán."
        )

    else:

        st.markdown(
            '<div class="invoice-title">🧾 HÓA ĐƠN THANH TOÁN</div>',
            unsafe_allow_html=True
        )

        st.write("")

        # Thông tin hóa đơn

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Mã hóa đơn",
                invoice["invoice_id"]
            )

        with col2:

            st.metric(
                "Khách hàng",
                invoice["customer_name"]
            )

        with col3:

            st.metric(
                "Tổng thanh toán",
                format_currency(invoice["total"])
            )

        st.divider()

        # Bảng sản phẩm

        table_data = []

        for index, item in enumerate(
            invoice["items"],
            1
        ):

            topping_text = (
                ", ".join(item["toppings"])
                if item["toppings"]
                else "Không"
            )

            table_data.append(
                {
                    "#": index,
                    "Món": item["drink"],
                    "Size": item["size"],
                    "Topping": topping_text,
                    "Đường": item["sugar"],
                    "Đá": item["ice"],
                    "SL": item["quantity"],
                    "Đơn giá": format_currency(
                        item["unit_price"]
                    ),
                    "Thành tiền": format_currency(
                        item["total"]
                    ),
                }
            )

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # Tổng tiền

        col1, col2 = st.columns(2)

        with col2:

            st.markdown(
                f"""
                **Tạm tính:**  
                {format_currency(invoice["subtotal"])}

                **Giảm giá:**  
                -{format_currency(invoice["discount"])}

                # Tổng: {format_currency(invoice["total"])}
                """
            )

        st.divider()

        st.subheader("📥 Xuất hóa đơn")

        receipt_text = generate_receipt_text(
            invoice
        )

        receipt_html = generate_receipt_html(
            invoice
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.download_button(
                label="📄 Tải hóa đơn TXT",
                data=receipt_text,
                file_name=f"{invoice['invoice_id']}.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:

            st.download_button(
                label="🌐 Tải hóa đơn HTML",
                data=receipt_html,
                file_name=f"{invoice['invoice_id']}.html",
                mime="text/html",
                use_container_width=True
            )

        with col3:

            st.info(
                "Mở file HTML bằng trình duyệt rồi nhấn Ctrl + P để in hoặc lưu thành PDF."
            )


# ============================================================
# TAB 3 - LỊCH SỬ HÓA ĐƠN
# ============================================================

with tab_history:

    st.subheader("📚 Lịch sử hóa đơn")

    history = st.session_state.invoice_history

    if not history:

        st.info(
            "Chưa có hóa đơn nào trong phiên làm việc này."
        )

    else:

        total_revenue = sum(
            invoice["total"]
            for invoice in history
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Số hóa đơn",
                len(history)
            )

        with col2:

            st.metric(
                "Doanh thu",
                format_currency(total_revenue)
            )

        with col3:

            average = (
                total_revenue / len(history)
                if history
                else 0
            )

            st.metric(
                "Trung bình / hóa đơn",
                format_currency(average)
            )

        st.divider()

        for invoice in history:

            with st.expander(
                f"🧾 {invoice['invoice_id']} "
                f"— {invoice['customer_name']} "
                f"— {format_currency(invoice['total'])}"
            ):

                st.write(
                    f"**Thời gian:** {invoice['created_at']}"
                )

                st.write(
                    f"**Khách hàng:** {invoice['customer_name']}"
                )

                st.write(
                    f"**Tạm tính:** "
                    f"{format_currency(invoice['subtotal'])}"
                )

                st.write(
                    f"**Giảm giá:** "
                    f"{format_currency(invoice['discount'])}"
                )

                st.write(
                    f"**Tổng tiền:** "
                    f"{format_currency(invoice['total'])}"
                )

                history_table = []

                for index, item in enumerate(
                    invoice["items"],
                    1
                ):

                    history_table.append(
                        {
                            "#": index,
                            "Món": item["drink"],
                            "Size": item["size"],
                            "SL": item["quantity"],
                            "Đơn giá":
                                format_currency(
                                    item["unit_price"]
                                ),
                            "Thành tiền":
                                format_currency(
                                    item["total"]
                                )
                        }
                    )

                st.dataframe(
                    history_table,
                    use_container_width=True,
                    hide_index=True
                )

                st.download_button(
                    label="📥 Tải lại hóa đơn",
                    data=generate_receipt_html(
                        invoice
                    ),
                    file_name=f"{invoice['invoice_id']}.html",
                    mime="text/html",
                    key=f"download_{invoice['invoice_id']}"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🧋 Milk Tea POS — Hệ thống bán hàng trà sữa bằng Streamlit"
)
