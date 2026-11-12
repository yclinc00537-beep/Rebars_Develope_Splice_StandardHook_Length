import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="結構標準圖鋼筋長度與彎鉤計算系統", layout="wide")

st.title("🏗️ 結構標準圖：鋼筋伸展、搭接與標準彎鉤計算系統")
st.markdown("整合 **表（ST1-5a）鋼筋伸展與搭接長度** 及 **表（ST1-1 / ST1-2）標準彎鉤尺寸**，內建規範公式自動計算（單位：cm）。")

# ==========================================
# 共用基礎資料與輔助函數
# ==========================================
rebar_db_map = {
    "#3": 0.953,
    "#4": 1.27,
    "#5": 1.59,
    "#6": 1.91,
    "#7": 2.22,
    "#8": 2.54,
    "#9": 2.87,
    "#10": 3.22,
    "#11": 3.58,
}

def ceil_half(val):
    return math.ceil(round(val, 4) * 2) / 2.0

def round_d(val):
    return math.floor(round(val, 4) * 10 + 0.5) / 10.0

# ==========================================
# 建立雙分頁介面 (Tabs)
# ==========================================
tab1, tab2 = st.tabs([
    "📏 模組一：鋼筋伸展與搭接長度 表(ST1-5a)",
    "🪝 模組二：鋼筋標準彎鉤尺寸 表(ST1-1 / ST1-2)"
])

# ------------------------------------------
# 分頁 1：表（ST1-5a）鋼筋之伸展與搭接長度
# ------------------------------------------
with tab1:
    st.header("📏 表（ST1-5a）鋼筋之伸展與搭接長度")
    
    rebar_options_t1 = {
        "9.53 mm (#3)": {"db": 0.953, "num": 3},
        "12.7 mm (#4)": {"db": 1.27, "num": 4},
        "15.9 mm (#5)": {"db": 1.59, "num": 5},
        "19.1 mm (#6)": {"db": 1.91, "num": 6},
        "22.2 mm (#7)": {"db": 2.22, "num": 7},
        "25.4 mm (#8)": {"db": 2.54, "num": 8},
        "28.7 mm (#9)": {"db": 2.87, "num": 9},
        "32.2 mm (#10)": {"db": 3.22, "num": 10},
        "35.8 mm (#11)": {"db": 3.58, "num": 11},
    }
    
    fc_options = (210, 245, 280, 350, 420, 490)
    
    category_options = {
        "受拉竹節鋼筋伸展長度 - 頂層筋 (Ld)": {"factor": 1.3},
        "受拉竹節鋼筋伸展長度 - 基本無塗層鋼筋 (Ld)": {"factor": 1.0},
        "受拉竹節鋼筋搭接長度 - 頂層筋甲級搭接 (Ls-甲)": {"factor": 1.3},
        "受拉竹節鋼筋搭接長度 - 頂層筋乙級搭接 (Ls-乙)": {"factor": 1.3 * 1.3},
        "受拉竹節鋼筋搭接長度 - 一般筋甲級搭接 (Ls-甲)": {"factor": 1.0},
        "受拉竹節鋼筋搭接長度 - 一般筋乙級搭接 (Ls-乙)": {"factor": 1.3},
        "受壓竹節鋼筋搭接長度 - 甲級搭接 (Ls-甲)": {"factor": 1.0},
        "受壓竹節鋼筋搭接長度 - 乙級搭接 (Ls-乙)": {"factor": 1.3},
    }
    
    fy_options = {
        "SD280 (fy = 2800)": 2800,
        "SD420 (fy = 4200)": 4200,
        "SD490 (fy = 4900)": 4900,
    }
    
    def calculate_splice_length(rebar_key, fc, category_key, fy_key):
        rebar = rebar_options_t1.get(rebar_key)
        db = rebar.get("db")
        num = rebar.get("num")
        fy = fy_options.get(fy_key)
        
        if fy == 4900 and num < 10:
            return "-"
        
        size_factor = 0.8 if num <= 6 else 1.0
        grade_factor = 1.08 if fy == 4900 else 1.0
        base_ld = (0.14 * fy * size_factor * grade_factor / math.sqrt(fc)) * db
        total_factor = category_options.get(category_key).get("factor")
        raw_length = base_ld * total_factor
        return max(30, math.ceil(raw_length))

    st.subheader("🔍 條件篩選（對應圖表左側與上方欄位）")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### ⬅️ 圖表左側項目")
        sel_rebar_t1 = st.selectbox("1. 鋼筋直徑 (號數)", tuple(rebar_options_t1.keys()), index=4, key="t1_rebar")
        sel_fc_t1 = st.selectbox("2. 混凝土抗壓強度 f'c (kgf/cm²)", fc_options, index=2, key="t1_fc")
    with c2:
        st.markdown("##### ⬆️ 圖表上方項目")
        sel_cat_t1 = st.selectbox("3. 伸展 / 搭接項目類別", tuple(category_options.keys()), index=5, key="t1_cat")
        sel_fy_t1 = st.selectbox("4. 鋼筋降伏強度等級", tuple(fy_options.keys()), index=1, key="t1_fy")

    st.divider()
    res_t1 = calculate_splice_length(sel_rebar_t1, sel_fc_t1, sel_cat_t1, sel_fy_t1)
    
    st.subheader("📊 查詢結果 (Output)")
    if res_t1 == "-":
        st.warning(f"⚠️ **查無此規格（圖表標示為 `-`）：** 依據表 ST1-5a，**{sel_fy_t1}** 不適用於 **{sel_rebar_t1}**。")
    else:
        rc1, rc2, rc3 = st.columns((1.5, 1.5, 2))
        with rc1:
            st.metric(label="所需最小長度", value=f"{res_t1} cm")
        with rc2:
            db_v = rebar_options_t1.get(sel_rebar_t1).get("db")
            st.metric(label="換算鋼筋直徑倍數", value=f"{math.ceil(res_t1 / db_v)} db")
        with rc3:
            st.info(f"**條件摘要：**\n\n{sel_rebar_t1} ｜ f'c = {sel_fc_t1} ｜ {sel_fy_t1}\n\n項目：{sel_cat_t1}")

    st.divider()
    st.subheader(f"📋 {sel_rebar_t1} 完整對照表（依混凝土強度 f'c 展開）")
    
    t1_table_data = list()
    for fc in fc_options:
        row = {"f'c (kgf/cm²)": fc}
        for cat in category_options.keys():
            _, short_cat = cat.split(" - ")
            for fy_k in fy_options.keys():
                short_fy, _ = fy_k.split(" ", 1)
                col_name = f"{short_cat} ({short_fy})"
                row.update({col_name: calculate_splice_length(sel_rebar_t1, fc, cat, fy_k)})
        t1_table_data.append(row)
        
    df_t1 = pd.DataFrame(t1_table_data)
    st.dataframe(df_t1, width="stretch", hide_index=True)

# ------------------------------------------
# 分頁 2：表（ST1-1 & ST1-2）鋼筋標準彎鉤尺寸
# ------------------------------------------
with tab2:
    st.header("🪝 表（ST1-1 & ST1-2）鋼筋標準彎鉤尺寸")
    
    def calculate_hook_dimensions(hook_category, rebar_size, hook_angle):
        db = rebar_db_map.get(rebar_size)
        num = int(rebar_size.replace("#", ""))
        
        if hook_category == "表（ST1-1）主鋼筋標準彎鉤":
            d_mult = 6 if num <= 8 else 8
            D_val = round_d(d_mult * db)
            if hook_angle == "90° 彎鉤":
                A_val = ceil_half(12 * db)
                formula_note = f"D = {d_mult}db ｜ A = 12db"
            else:
                A_val = ceil_half(max(4 * db, 6.5))
                formula_note = f"D = {d_mult}db ｜ A = max(4db, 6.5cm)"
        else:
            D_val = round_d(4 * db)
            A_val = ceil_half(max(6 * db, 7.5))
            formula_note = "D = 4db ｜ A = max(6db, 7.5cm)（註：180°彎鉤 A 同 135°彎鉤）"
            
        return db, D_val, A_val, formula_note

    st.subheader("🔍 條件查詢（下拉選單）")
    hc1, hc2, hc3 = st.columns(3)
    
    with hc1:
        sel_cat_t2 = st.selectbox(
            "1. 選擇圖表類型（上方項目）",
            ("表（ST1-1）主鋼筋標準彎鉤", "表（ST1-2）箍筋標準彎鉤"),
            index=0,
            key="t2_cat"
        )
    with hc2:
        if sel_cat_t2 == "表（ST1-1）主鋼筋標準彎鉤":
            avail_rebars = ("#3", "#4", "#5", "#6", "#7", "#8", "#9", "#10", "#11")
        else:
            avail_rebars = ("#3", "#4", "#5")
        sel_rebar_t2 = st.selectbox("2. 選擇鋼筋編號（左側項目）", avail_rebars, index=0, key="t2_rebar")
    with hc3:
        if sel_cat_t2 == "表（ST1-1）主鋼筋標準彎鉤":
            avail_angles = ("90° 彎鉤", "180° 彎鉤")
        else:
            avail_angles = ("135° 彎鉤", "90° 彎鉤", "180° 彎鉤（同135°）")
        sel_angle_t2 = st.selectbox("3. 選擇彎鉤角度", avail_angles, index=0, key="t2_angle")

    st.divider()
    db_v2, D_res2, A_res2, note_res2 = calculate_hook_dimensions(sel_cat_t2, sel_rebar_t2, sel_angle_t2)
    
    st.subheader("📊 計算結果輸出 (Output)")
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.metric(label="鋼筋標稱直徑 (db)", value=f"{db_v2} cm")
    with mc2:
        st.metric(label="最小彎曲內徑 D", value=f"{D_res2:.1f} cm")
    with mc3:
        st.metric(label="末端延伸長度 A", value=f"{A_res2:.1f} cm")
    with mc4:
        st.info(f"**規範公式依據：**\n\n{note_res2}")

    st.divider()
    st.subheader("📋 完整標準彎鉤資料表（支援動態篩選）")
    
    all_hook_rows = list()
    for r in ("#3", "#4", "#5", "#6", "#7", "#8", "#9", "#10", "#11"):
        for ang in ("90° 彎鉤", "180° 彎鉤"):
            db_v, d_v, a_v, f_note = calculate_hook_dimensions("表（ST1-1）主鋼筋標準彎鉤", r, ang)
            all_hook_rows.append({
                "圖表分類": "表（ST1-1）主鋼筋標準彎鉤",
                "鋼筋編號": r,
                "標稱直徑 db (cm)": db_v,
                "彎鉤角度": ang,
                "彎曲內徑 D (cm)": f"{d_v:.1f}",
                "延伸長度 A (cm)": f"{a_v:.1f}",
                "計算公式": f_note
            })
            
    for r in ("#3", "#4", "#5"):
        for ang in ("135° 彎鉤", "90° 彎鉤", "180° 彎鉤（同135°）"):
            db_v, d_v, a_v, f_note = calculate_hook_dimensions("表（ST1-2）箍筋標準彎鉤", r, ang)
            all_hook_rows.append({
                "圖表分類": "表（ST1-2）箍筋標準彎鉤",
                "鋼筋編號": r,
                "標稱直徑 db (cm)": db_v,
                "彎鉤角度": ang,
                "彎曲內徑 D (cm)": f"{d_v:.1f}",
                "延伸長度 A (cm)": f"{a_v:.1f}",
                "計算公式": f_note
            })
            
    df_t2 = pd.DataFrame(all_hook_rows)
    
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        f_cat = st.multiselect("篩選圖表分類", options=df_t2["圖表分類"].unique().tolist(), default=df_t2["圖表分類"].unique().tolist(), key="f_t2_cat")
    with fc2:
        f_reb = st.multiselect("篩選鋼筋編號", options=df_t2["鋼筋編號"].unique().tolist(), default=df_t2["鋼筋編號"].unique().tolist(), key="f_t2_reb")
    with fc3:
        f_ang = st.multiselect("篩選彎鉤角度", options=df_t2["彎鉤角度"].unique().tolist(), default=df_t2["彎鉤角度"].unique().tolist(), key="f_t2_ang")
        
    filtered_df_t2 = df_t2[
        (df_t2["圖表分類"].isin(f_cat)) &
        (df_t2["鋼筋編號"].isin(f_reb)) &
        (df_t2["彎鉤角度"].isin(f_ang))
    ]
    st.dataframe(filtered_df_t2, width="stretch", hide_index=True)