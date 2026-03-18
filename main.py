import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ====== Google Sheets 設定 ======
SPREADSHEET_ID = "1uL3LADSC9Qf4xmgxBRXzfUaBQ1U1-ZbBxRSslBQg848"
RANGE_NAME = "OBOG会集金リスト!B:P"  # 必要に応じて変更

# ====== 認証（サービスアカウント） ======
@st.cache_resource
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
    return result.get("values", [])

data = load_sheet()

# ====== UI ======
st.title("名簿編集アプリ（Google Sheets）")

# 行番号選択
row_numbers = list(range(2, len(data) + 1))  # 1行目はヘッダー
selected_row = st.selectbox("編集する行を選択", row_numbers)

row_data = data[selected_row - 1]

# 編集フォーム
with st.form("edit_form"):
    cols = st.columns(len(row_data))
    new_values = []

    for i, value in enumerate(row_data):
        new_value = cols[i].text_input(f"項目{i+1}", value)
        new_values.append(new_value)

    submitted = st.form_submit_button("保存")

# 保存処理
if submitted:
    update_range = f"名簿!A{selected_row}:F{selected_row}"
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=update_range,
        valueInputOption="USER_ENTERED",
        body={"values": [new_values]}
    ).execute()

    st.success("保存しました！")