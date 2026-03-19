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
selected_row = st.selectbox("対象Noを選択", row_numbers)

row_data = body[selected_row - 1]   # データ本体
# データ行を16列に揃える（足りない分は空文字で埋める）
while len(row_data) < 16:
    row_data.append("")
# ====== 編集フォーム（カードで囲む） ======
with st.container():
    st.markdown("""
    <div style="padding:15px; border:1px solid #ddd; border-radius:10px; background:#fafafa;">
    """, unsafe_allow_html=True)

    with st.form("edit_form"):

        col1, col2, col3, col4 = st.columns(4)
        new_values = []
    
# ====== 編集フォーム ======
with st.form("edit_form"):

    col1, col2, col3, col4 = st.columns(4)
    new_values = []

    # --- 列1：項目1,2,3 ---
    with col1:
        for i in [0, 1, 2]:
            new_values.append(st.text_input(header[i], row_data[i]))

    # --- 列2：項目4,5 / 6,7 / 8,9 ---
    with col2:
        cA, cB = st.columns(2)
        with cA:
            new_values.append(st.text_input(header[3], row_data[3]))
        with cB:
            options = ["〇", "×", ""]
            new_values.append(st.text_input(header[4], row_data[4]))
        cA, cB = st.columns(2)
        with cA:
            new_values.append(st.text_input(header[5], row_data[5]))
        with cB:
            options = ["〇", "×", ""]
            new_values.append(st.text_input(header[6], row_data[6]))
        cA, cB = st.columns(2)
        with cA:
            new_values.append(st.text_input(header[7], row_data[7]))
        with cB:
            options = ["〇", "×", ""]
            new_values.append(st.text_input(header[8], row_data[8]))

    # --- 列3：項目10,11 ---
    with col3:
        cA, cB = st.columns(2)
        with cA:
            new_values.append(st.text_input(header[9], row_data[9]))
        with cB:
            options = ["〇", "×", ""]
            new_values.append(st.text_input(header[10], row_data[10]))

    # --- 列4：項目12〜16 ---
    with col4:
        options = ["2000","ー",""]
        new_values.append(st.text_input(header[13], row_data[13]))
        options = ["1000","ー","2000","3000"]
        new_values.append(st.text_input(header[13], row_data[13]))
　　　　 options = ["7000","ー",""]
        new_values.append(st.text_input(header[13], row_data[13]))
        cA, cB = st.columns(2)
        with cA:
            new_values.append(st.text_input(header[14], row_data[14]))
        with cB:
            options = ["〇", "未", "ー",""]
            new_values.append(st.text_input(header[15], row_data[15]))

        submitted = st.form_submit_button("保存")

    st.markdown("</div>", unsafe_allow_html=True)
    
# 保存処理
if submitted:
    update_range = f"CollectList!B{selected_row}:Q{selected_row}"
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=update_range,
        valueInputOption="USER_ENTERED",
        body={"values": [new_values]}
    ).execute()

    st.success("保存しました！")
