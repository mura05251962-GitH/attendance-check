import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

st.markdown("""
<style>

/* =========================
   ① 全体：360px設計の基準
========================= */
.block-container {
    min-width: 360px !important;
    max-width: 360px !important;
    margin: 0 auto !important;
    padding-left: 8px !important;
    padding-right: 8px !important;
}

/* =========================
   ② columns：横並び強制
========================= */
div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 4px !important;
    overflow: hidden !important;
}

/* =========================
   ③ column：縮められるようにする
========================= */
div[data-testid="column"] {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    padding-top:0.2rem;
    padding-bottom:0.2rem;
    padding-left: 0.5rem !important;
    padding-right: 0.2rem !important;
}

/* =========================
   ④ selectbox：はみ出し防止
========================= */
div[data-baseweb="select"] {
    width: 100% !important;
    min-width: 0 !important;
}

/* テキスト省略（超重要） */
div[data-baseweb="select"] span {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* =========================
   ⑤ input系
========================= */
input, textarea {
    width: 100% !important;
    min-width: 0 !important;
}
/* ===== タイトルフォントサイズ（3VW=横幅の3%） ===== */
.app-title {
    font-size:16px !important;
    font-weight: bold !important;
    text-align: center !important;
    margin-bottom: 20px !important;
    color: #000080 !important;
}

/* =========================
   ⑥ フォント（固定px推奨）
========================= */
html, body {
    font-size: 14px !important;
}

/* =========================
   ⑦ 余白削減（詰める）
========================= */
label {
    margin-bottom: 2px !important;
}

.stMarkdown {
    margin-bottom: 2px !important;
}

/* ===== big-box（上部の青枠） ===== */
.big-box {
    padding: 2px 4px;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 4px;
    border-radius: 5px;
    background: #e8f0fe;
    border: 2px solid #4285f4;
}

/* ===== big-box 内のラベルと値（共通化） ===== */
.big-box .label {
    white-space: nowrap;
    font-size: 14px;
    font-weight: bold;
    min-width: 3rem;
}
.big-box .value {
    flex: 1 1 0;
    min-width: 0;
    font-size: 16px;
    font-weight: bold;
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

header = data[8]          # ← 2行目（項目名）
body = data[9:]           # ← 3行目以降（データ）

# ======　行番号選択　======
row_numbers = list(range(1, len(body) + 1))
def key_for(col, row):
    return f"col{col}_row{row}"
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
  
# ======　表題　======
st.markdown('<h1 class="app-title">2026年OGOB会 出欠・集金アプリ</h1>',
         unsafe_allow_html=True)

 # ======　No、卒年次、名前　======

col1, col2 = st.columns(2)
 
# selectbox は col1 にそのまま置く
with col1:
    selected_row = st.selectbox("Noを選択", row_numbers)
    
row_data = body[selected_row - 1]
while len(row_data) < 16:
    row_data.append("")
 
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

#（名前）
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
#    st.markdown("---") 
st.markdown("""
<style>
.stApp {background-color: #fffff0;}
</style>
""",unsafe_allow_html=True)

with st.form("edit_form"): 

    col1, col2, col3 = st.columns(3)
    new_values = []
    new_values.append(row_data[0])
    new_values.append(row_data[1])
    new_values.append(row_data[2])

    # --- 列1：項目4,6,8,10 ---
    with col1:
        st.text_input("4/11テニス", value=row_data[3], disabled=True)
        new_values.append(row_data[3]) 
        st.text_input("4/11総会", value=row_data[5], disabled=True)
        new_values.append(row_data[5])
        st.text_input("4/11懇親会", value=row_data[7], disabled=True)
        new_values.append(row_data[7])
        st.text_input("4/12テニス", value=row_data[9], disabled=True)
        new_values.append(row_data[9])
             
    # --- 列2：項目5,7,9,11 ---
    with col2:    
        options = ["✓","ー",""]
        index=options.index(row_data[4]) if row_data[4] in options else 2
        new_values.append(
            st.selectbox(header[4], options, index=index, key=key_for(4, selected_row))
        )
        options = ["✓","ー",""]
        index=options.index(row_data[6]) if row_data[6] in options else 2
        new_values.append(
            st.selectbox(header[6], options, index=index, key=key_for(6, selected_row))
        )
        options = ["✓","ー",""]
        index=options.index(row_data[8]) if row_data[8] in options else 2
        new_values.append(
            st.selectbox(header[8], options, index=index, key=key_for(8, selected_row))
        )
        options = ["✓","ー",""]
        index=options.index(row_data[10]) if row_data[8] in options else 2
        new_values.append(
            st.selectbox(header[10], options, index=index, key=key_for(10, selected_row))
        )
       
    # --- 列3：項目12〜16 ---
    with col3:
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
        # 集金（表示のみ）
        st.text_input("集金", value=(row_data[14]), disabled=True)
        new_values.append(row_data[14])
#          options = ["〇", "未", "ー",""]
#          new_values.append(
#              st.selectbox(header[14], options, index=options.index(row_data[14],
#                           key_for(14, selected_row)))
#                           if row_data[14] in options else 2))
         # 合計金額（表示のみ）
        st.text_input("合計金額", value=to_comma(row_data[15]), disabled=True)

   　submitted = st.form_submit_button("確認・集金完了")
    
#     st.markdown("</div>", unsafe_allow_html=True)

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

