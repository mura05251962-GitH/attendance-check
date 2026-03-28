import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

# カスタムCSSの注入
st.markdown("""
<style>

/* ===== スマホ専用：PCレイアウト縮小 ===== */
@media screen and (max-width: 600px) {

    .block-container {
        min-width: 800px !important;
        zoom: 0.55;
    }

    /* columns崩壊防止 */
    div[data-testid="column"] {
        flex: 1 1 auto !important;
        min-width: 0 !important;
        padding-left: 0.3rem !important;
        padding-right: 0.3rem !important;
    }

    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important;
        gap: 0.2rem !important;
        overflow-x: hidden;
    }
}

/* ===== タイトル ===== */
.app-title {
    font-size: clamp(20px, 3vw, 40px) !important;
    font-weight: bold;
    text-align: center;
    color: #000080;
}

/* ===== フォント（vwは使わない） ===== */
html, body {
    font-size: 16px !important;
    font-family: "游ゴシック", Arial, sans-serif;
}

/* ===== selectbox ===== */
div[data-baseweb="select"] {
    width: 120px !important;
    min-width: 0 !important;
}

/* ===== input ===== */
input {
    width: 100px !important;
}

/* ===== big-box ===== */
.big-box {
    padding: 8px 0;
    border-radius: 10px;
    background: #e8f0fe;
    border: 2px solid #4285f4;
}

</style>
""", unsafe_allow_html=True)
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

# ======　行番号選択　======
row_numbers = list(range(1, len(body) + 1))
def key_for(col, row):
    return f"col{col}_row{row}"
    
# ======　表題　======
with st.container():
    st.markdown('<h1 class="app-title">2026年OGOB会 出欠・集金アプリ</h1>',
            unsafe_allow_html=True)

    # ======　No、卒年次、名前　======

    col1, col2, col3 = st.columns([1, 1, 3])
    
    # selectbox は col1 にそのまま置く
    with col1:
        selected_row = st.selectbox("Noを選択", row_numbers)
        
    row_data = body[selected_row - 1]
    while len(row_data) < 16:
        row_data.append("")
    # ====== 正規化関数 ======
    def normalize(v):
        if v is None:
            return ""
        s = str(v)
        s = s.replace("　", "")   # 全角スペース
        s = s.replace(",", "")    # カンマ
        s = s.replace("\n", "")   # 改行
        s = s.replace("\r", "")
        s = s.replace("\t", "")
        return s.strip()
    row_data = [normalize(v) for v in row_data]
    # ====== 数値表示に,をいれる ======
    def to_comma(v):
        try:
            return f"{int(v):,}"
        except:
            return v
    # ====== テキストの数値変換 ======        
    def to_int(v):
        try:
            return int(v.replace(",", ""))
        except:
            return 0
    
    # #2（卒年度）
    with col2:
        st.markdown(
            f"""
            <div class="big-box">
                <div class="label">{header[1]}</div>
                <div class="Value">{row_data[1]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    # #3（名前）
    with col3:
        st.markdown(
            f"""
            <div class="big-box">
                <div class="label">{header[2]}</div>
                <div class="Value">{row_data[2]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
# ====== 編集フォーム =============================================
with st.container():
    st.markdown("---") 
    st.markdown("""
    <style>
    .stApp {background-color: #fff8dc;}
    </style>
    """,unsafe_allow_html=True)
    
    with st.form("edit_form"): 
    
        col1, col2 = st.columns(2)
        new_values = []
        new_values.append(row_data[0])
        new_values.append(row_data[1])
        new_values.append(row_data[2])
    
    
        # --- 列1：項目4,5 / 6,7 / 8,9 ---
        with col1:
            cA, cB = st.columns(2)
            with cA:
                st.text_input("4/11テニス", value=row_data[3], disabled=True)
                new_values.append(row_data[3]) 
            with cB:
                options = ["✓","ー",""]
                index=options.index(row_data[4]) if row_data[4] in options else 2
                new_values.append(
                    st.selectbox(header[4], options, index=index, key=key_for(4, selected_row))
                )
    
            cA, cB = st.columns(2)
            with cA:
                st.text_input("4/11総会", value=row_data[5], disabled=True)
                new_values.append(row_data[5])
            with cB:
                options = ["✓","ー",""]
                index=options.index(row_data[6]) if row_data[6] in options else 2
                new_values.append(
                    st.selectbox(header[6], options, index=index, key=key_for(6, selected_row))
                )
                                  
            cA, cB = st.columns(2)
            with cA:
                st.text_input("4/11懇親会", value=row_data[7], disabled=True)
                new_values.append(row_data[7])
            with cB:
                options = ["✓","ー",""]
                index=options.index(row_data[8]) if row_data[8] in options else 2
                new_values.append(
                    st.selectbox(header[8], options, index=index, key=key_for(8, selected_row))
                )
     
            cA, cB = st.columns(2)
            with cA:
                st.text_input("4/12テニス", value=row_data[9], disabled=True)
                new_values.append(row_data[9])
            with cB:
                options = ["✓","ー",""]
                index=options.index(row_data[10]) if row_data[8] in options else 2
                new_values.append(
                    st.selectbox(header[10], options, index=index, key=key_for(10, selected_row))
                )
     
        # --- 列3：項目12〜16 ---
        with col2:
            # 年会費
            value = to_comma(row_data[11])
            options = ["2,000", "ー", ""]
            index = options.index(value) if value in options else 2
            new_values.append(normalize(st.selectbox(header[11], options, index=index,
                                                     key=key_for(11, selected_row)))
             )
            # カンパ
            value = to_comma(row_data[12])
            options = ["1,000","2,000","3,000","ー",""]
            index = options.index(value) if value in options else 2
            new_values.append(normalize(st.selectbox(header[12], options, index=index,
                                                     key=key_for(12, selected_row)))
            )
            # 懇親会費
            value = to_comma(row_data[13])
            options = ["7,000","ー",""]
            index = options.index(value) if value in options else 2
            new_values.append(normalize(st.selectbox(header[13], options, index=index,
                                                     key=key_for(13, selected_row)))
            )
            # 合計金額（表示のみ）
            cA, cB = st.columns([1,1])
            with cA:
                st.text_input("集金", value=(row_data[14]), disabled=True)
                new_values.append(row_data[14])
     #           options = ["〇", "未", "ー",""]
     #           new_values.append(
     #               st.selectbox(header[14], options, index=options.index(row_data[14],
     #                            key_for(14, selected_row)))
     #                            if row_data[14] in options else 2))
            with cB:
                st.text_input("合計金額", value=to_comma(row_data[15]), disabled=True)
    
        submitted = st.form_submit_button("確認・集金完了")
        
        st.markdown("</div>", unsafe_allow_html=True)

# 保存処理
if submitted:
    new_values[14] = "〇"
    update_range = f"CollectList!B{selected_row+2}:P{selected_row+2}"
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=update_range,
        valueInputOption="USER_ENTERED",
        body={"values": [new_values]}
    ).execute()

    st.success("保存しました！")
    st.rerun()

