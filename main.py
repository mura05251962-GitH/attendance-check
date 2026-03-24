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

# ======　行番号選択　======
row_numbers = list(range(1, len(body) + 1))
def key_for(col, row):
    return f"col{col}_row{row}"
    
# ====== selectbox + #2 + #3 を横並びに配置 ======
st.markdown("""
<style>

/* ===== タイトルフォントサイズ（3VW=横幅の3%） ===== */
.app-title {
    font-size: clamp(32px, 3vw, 40px) !important;
    font-weight: bold !important;
    text-align: center !important;
    margin-bottom: 20px !important;
    color: #000080 !important;
}

/* ===== 共通フォントサイズ（全体を大きく） ===== */
html, body, [class*="css"] {
    font-size: 26px !important;
    font-family: "メイリオ", Meiryo, sans-serif !important;
}
/* すべての文字色を黒にする */
html, body, div, span, label, p, input, select, textarea, button,
.stMarkdown, .stTextInput, .stSelectbox, .stRadio, .stCheckbox {
    color: #000 !important;
}
/* ===== selectbox の選択肢（参加・不参加）を黒にする ===== */
div[data-baseweb="select"] * {
    color: #000 !important;
}
div[data-baseweb="select"] > div {
    color: #000 !important;
}
input:disabled {
    color: #000 !important;
    -webkit-text-fill-color: #000 !important;  /* Safari / Chrome 系対策 */
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
.big-box .Value {
    font-size: 30px;
    font-weight: bold;
}

/* ===== フォーム内のラベル（出欠1、参加など） ===== */
label, .stMarkdown, .stTextInput label, .stSelectbox label {
    font-size: 30px !important;
}

/* ===== 入力欄の文字（text_input, selectbox の中身） ===== */
input, select, textarea {
    font-size: 26px !important;
    font-weight: bold;
    }

/* markdown上下の余白をゼロにする */
hr {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}
/* ===== columns の横の隙間（gap）を詰める ===== */
div[data-testid="column"] {
    padding-left: 1rem !important;
    padding-right: 0.2rem !important;
}

/* カラム間の gap をゼロに近づける */
div[data-testid="stHorizontalBlock"] {
    gap: 0.2rem !important;
}

/* フォームを絶対配置の基準にする */
form {
    position: relative !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="app-title">2026年OGOB会 出欠・集金アプリ</h1>',
            unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 4])

# selectbox は col1 にそのまま置く
with col1:
    selected_row = st.selectbox("対象Noを選択", row_numbers)
    
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
    
# ====== 編集フォーム（カードで囲む） ======
#with st.container():
st.markdown("---") 
st.markdown("""
#<div style="background-color: #ffffe0">
#</div>
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
            st.text_input("4/11(土)テニス", value=row_data[3], disabled=True)
            new_values.append(row_data[3]) 
        with cB:
            options = ["✓","ー",""]
            index=options.index(row_data[4]) if row_data[4] in options else 2
            new_values.append(
                st.selectbox(header[4], options, index=index, key=key_for(4, selected_row))
            )

        cA, cB = st.columns(2)
        with cA:
            st.text_input("4/11(土)総会", value=row_data[5], disabled=True)
            new_values.append(row_data[5])
        with cB:
            options = ["✓","ー",""]
            index=options.index(row_data[6]) if row_data[6] in options else 2
            new_values.append(
                st.selectbox(header[6], options, index=index, key=key_for(6, selected_row))
            )
                              
        cA, cB = st.columns(2)
        with cA:
            st.text_input("4/11(土)懇親会", value=row_data[7], disabled=True)
            new_values.append(row_data[7])
        with cB:
            options = ["✓","ー",""]
            index=options.index(row_data[8]) if row_data[8] in options else 2
            new_values.append(
                st.selectbox(header[8], options, index=index, key=key_for(8, selected_row))
            )
 
        cA, cB = st.columns(2)
        with cA:
            st.text_input("4/12(日)テニス", value=row_data[9], disabled=True)
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
             # 合計金額を計算
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

