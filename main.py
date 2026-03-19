import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ====== Google Sheets 設定 ======
SPREADSHEET_ID = "1uL3LADSC9Qf4xmgxBRXzfUaBQ1U1-ZbBxRSslBQg848"
RANGE_NAME = "CollectList!B:O"  # 必要に応じて変更

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
    return result.get("values", [])

data = load_sheet()

# ====== UI ======
st.title("2026年芙蓉クラブOGOB会 出欠・集金アプリ")

# 行番号選択
row_numbers = list(range(3, len(data) + 1))  # 2行目はヘッダー
selected_row = st.selectbox("編集する行を選択", row_numbers)

row_data = data[selected_row - 2]

# 編集フォーム
with st.form("edit_form"):

    # 3列レイアウトを作成
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    columns = [col1, col2, col3, col4, col5, col6]

    new_values = []

    # 各項目をどの列に置くかを指定（0=左, 1=中央, 2=右）
    # 必要に応じて自由に変更できる
    layout_map = [
        0, 1, 2,           # 項目B,C,D
        0, 1, 2, 3, 4, 5,  # 項目E,F,G,H,I,J
        0, 1,              # 項目K,L
        0, 1, 2, 3, 4      # 項目M,N,O,P,Q
    ]

    # row_data の項目数に合わせて layout_map を自動調整（安全策）
    if len(layout_map) < len(row_data):
        # 足りない分は左列に入れる
        layout_map += [0] * (len(row_data) - len(layout_map))

    # 入力欄を配置
    for i, value in enumerate(row_data):
        col_index = layout_map[i]
        new_value = columns[col_index].text_input(f"項目{i+1}", value)
        new_values.append(new_value)

    submitted = st.form_submit_button("保存")

# 保存処理
if submitted:
    update_range = f"CollectList!B{selected_row}:O{selected_row}"
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=update_range,
        valueInputOption="USER_ENTERED",
        body={"values": [new_values]}
    ).execute()

    st.success("保存しました！")
