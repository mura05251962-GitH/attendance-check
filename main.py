import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ====== Google Sheets 設定 ======
SPREADSHEET_ID = "1uL3LADSC9Qf4xmgxBRXzfUaBQ1U1-ZbBxRSslBQg848"
RANGE_NAME = "CollectList!B:Q"  # 必要に応じて変更

# ====== 認証（サービスアカウント） ======
#@st.cache_resource
def get_service():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build("sheets", "v4", credentials=creds)
    return service

service = get_service()
sheet = service.spreadsheets()

# ====== データ読み込み ======
def load_sheet():
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()
    values = result.get("values", [])
    return values

data = load_sheet()

header = data[1]          # ← 2行目（項目名）
body = data[2:]           # ← 3行目以降（データ）

# 行番号選択
row_numbers = list(range(1, len(body) + 1))

# ====== selectbox + #2 + #3 を横並びに配置 ======
st.markdown("""
<style>

/* ===== 共通フォントサイズ（全体を大きく） ===== */
html, body, [class*="css"] {
    font-size: 22px !important;
}

/* ===== big-box（上部の青枠） ===== */
.big-box {
    padding: 10px 0;
    text-align: center;
    border-radius: 10px;
    background: #e8f0fe;
    border: 2px solid #4285f4;
}

/* ===== big-box 内のラベルと値（共通化） ===== */
.big-box .label {
    font-size: 22px;
    font-weight: bold;
}
.big-box .value {
    font-size: 32px;
    font-weight: bold;
}

/* ===== フォーム内のラベル（出欠1、参加など） ===== */
label, .stMarkdown, .stTextInput label, .stSelectbox label {
    font-size: 22px !important;
}

/* ===== 入力欄の文字（text_input, selectbox の中身） ===== */
input, select, textarea {
    font-size: 22px !important;
}

/* ===== columns の横の隙間（gap）を詰める ===== */
div[data-testid="column"] {
    padding-left: 0.2rem !important;
    padding-right: 0.2rem !important;
}

/* カラム間の gap をゼロに近づける */
div[data-testid="stHorizontalBlock"] {
    gap: 0.2rem !important;
}

</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 4])

# selectbox は col1 にそのまま置く
with col1:
    selected_row = st.selectbox("対象Noを選択", row_numbers)

row_data = body[selected_row - 1]
while len(row_data) < 16:
    row_data.append("")

# #2（例：名前）
with col2:
    st.markdown(
        f"""
        <div class="big-box">
            <div class="label">{header[1]}</div>
            <div class="value">{row_data[1]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# #3（例：フリガナ or 会社名）
with col3:
    st.markdown(
        f"""
        <div class="big-box">
            <div class="label">{header[2]}</div>
            <div class="value">{row_data[2]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
# ====== 編集フォーム（カードで囲む） ======
with st.container():
    st.markdown("""
    <div style="padding:15px; border:1px solid #ddd; border-radius:10px; background:#fafafa;">
    """, unsafe_allow_html=True)
    
    with st.form("edit_form"):

        col1, col2 = st.columns(2)
        new_values = []

        # --- 列1：項目4,5 / 6,7 / 8,9 ---
        with col1:
            cA, cB = st.columns([2,1])
            with cA:
                st.text_input("4/11(土)テニス", value=row_data[3], disabled=True)
            with cB:
                options = ["✓","ー",""]
                new_values.append(st.selectbox(header[4], options, index=options.index(row_data[4]) if row_data[4] in options else 2))

            cA, cB = st.columns([2,1])
            with cA:
                st.text_input("4/11(土)総会", value=row_data[5], disabled=True)
            with cB:
                options = ["✓","ー",""]
                new_values.append(st.selectbox(header[6], options, index=options.index(row_data[6]) if row_data[4] in options else 2))

            cA, cB = st.columns([2,1])
            with cA:
                st.text_input("4/11(土)懇親会", value=row_data[7], disabled=True)
            with cB:
                options = ["✓","ー",""]
                new_values.append(st.selectbox(header[8], options, index=options.index(row_data[8]) if row_data[4] in options else 2))

            cA, cB = st.columns([2,1])
            with cA:
                st.text_input("4/12(日)テニス", value=row_data[9], disabled=True)
            with cB:
                options = ["✓","ー",""]
                new_values.append(st.selectbox(header[10], options, index=options.index(row_data[10]) if row_data[4] in options else 2))

        # --- 列3：項目12〜16 ---
        with col2:
            # 年会費
            options = ["2000","ー",""]
            new_values.append(st.selectbox(header[11], options, index=options.index(row_data[11]) if row_data[11] in options else 2))

            # カンパ
            options = ["1000","2000","3000","ー",""]
            new_values.append(st.selectbox(header[12], options, index=options.index(row_data[12]) if row_data[12] in options else 4))

            # 懇親会費
            options = ["7000","ー",""]
            new_values.append(st.selectbox(header[13], options, index=options.index(row_data[13]) if row_data[13] in options else 2))

            # 合計金額（表示のみ）
            cA, cB = st.columns([3,1])
            with cA:
                st.text_input("合計金額", value=row_data[14], disabled=True)
            with cB:
                options = ["〇", "未", "ー",""]
                new_values.append(st.selectbox(header[15], options, index=options.index(row_data[15]) if row_data[15] in options else 3))

        submitted = st.form_submit_button("保存")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
# 保存処理
if submitted:
    update_range = f"CollectList!B{selected_row+2}:Q{selected_row+2}"
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=update_range,
        valueInputOption="USER_ENTERED",
        body={"values": [new_values]}
    ).execute()

    st.success("保存しました！")
    st.experimental_rerun()
