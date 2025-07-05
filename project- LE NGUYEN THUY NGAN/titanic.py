import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import matplotlib.font_manager as fm
import platform
import os

if platform.system() == 'Windows':
    font_path = 'C:/Windows/Fonts/malgun.ttf'
elif platform.system() == 'Darwin':
    font_path = '/System/Library/Fonts/AppleGothic.ttf'
else:
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
else:
    font_prop = None

plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="🚢 타이타닉 생존 대시보드", layout="wide")

st.markdown("""
    <style>
    body, .stApp {
        background-color: #f8e1e1;
    }
    .slide {
        animation: slidein 0.6s ease-out;
    }
    @keyframes slidein {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: #d87f7f;
        height: 100%;
        padding: 2rem 1.5rem;
        border-radius: 0 0 0 60%;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {
        color: white !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 20px !important;
        font-weight: 600 !important;
        padding: 18px 32px !important;
        line-height: 1.5 !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #fce4ec !important;
        color: #b71c1c !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    train = pd.read_csv("train.csv")
    test = pd.read_csv("test.csv")
    gender = pd.read_csv("gender_submission.csv")
    return train, test, gender

train_df, test_df, gender_df = load_data()

def preprocess(df):
    df = df.copy()
    df['Sex'] = df['Sex'].map({'male': 0, 'female': 1})
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce').fillna(df['Age'].median())
    df['Fare'] = pd.to_numeric(df['Fare'], errors='coerce').fillna(df['Fare'].median())
    df['Embarked'] = df['Embarked'].fillna('S').map({'S': 0, 'C': 1, 'Q': 2})
    df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
    return df

train_df = preprocess(train_df)
test_df = preprocess(test_df)

features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked', 'FamilySize']
X = train_df[features]
y = train_df['Survived']
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)
predictions = model.predict(test_df[features])

total_passengers = len(train_df)
actual_survived = train_df['Survived'].sum()
actual_not_survived = total_passengers - actual_survived
survival_rate = train_df['Survived'].mean() * 100

# Sidebar
with st.sidebar:
    st.markdown("""
        <h2>🌸 홈</h2>
    """, unsafe_allow_html=True)

    section = st.radio("항목 선택:", [
        "📊 예측 개요",
        "🧠 빠른 예측",
        "📋 예측 결과",
        "📬 승객 검색",
        "📈 시각화 차트"
    ])

st.title("🚢 타이타닉 생존 대시보드")

# 📊 예측 개요
if section == "📊 예측 개요":
    st.markdown("<div class='slide'>", unsafe_allow_html=True)
    st.markdown("""
        <style>
        .summary-wrapper {
            display: flex;
            justify-content: center;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
            max-width: 800px;
            width: 100%;
        }
        .summary-item {
            background: linear-gradient(to bottom right, #ffe6e6, #fff0f5);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            font-size: 18px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        }
        .summary-item b {
            color: #b71c1c;
        }
        </style>

        <div class="summary-wrapper">
            <div class="summary-box">
                <h2>📌 예측 개요</h2>
            <div class="summary-grid">
                <div class="summary-item"><b>👥 전체 승객 수:</b><br>""" + str(total_passengers) + """</div>
                <div class="summary-item"><b>✅ 생존자 수:</b><br>""" + str(actual_survived) + """</div>
                <div class="summary-item"><b>❌ 사망자 수:</b><br>""" + str(actual_not_survived) + """</div>
                <div class="summary-item"><b>📈 생존률:</b><br>{:.2f}%</div>
            </div>
        </div>
    """.format(survival_rate), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 🧠 빠른 예측
elif section == "🧠 빠른 예측":
    st.markdown("<div class='slide'>", unsafe_allow_html=True)
    st.subheader("🧠 빠른 예측")
    pclass = st.selectbox("티켓 등급", [1, 2, 3])
    sex = st.radio("성별", ['남성', '여성'])
    age = st.slider("나이", 0, 80, 30)
    fare = st.slider("요금", 0.0, 600.0, 50.0)
    sex_val = 0 if sex == '남성' else 1
    input_df = pd.DataFrame([{
        'Pclass': pclass, 'Sex': sex_val, 'Age': age,
        'SibSp': 0, 'Parch': 0, 'Fare': fare, 'Embarked': 0, 'FamilySize': 1
    }])
    if st.button("🔮 예측하기"):
        pred = model.predict(input_df)[0]
        proba = model.predict_proba(input_df)[0][1]
        st.success(f"{'✅ 생존' if pred else '❌ 사망'} ({proba*100:.1f}%)")
    st.markdown("</div>", unsafe_allow_html=True)

# 📋 예측 결과
if section == "📋 예측 결과":
    st.markdown("<div class='slide'>", unsafe_allow_html=True)
    st.subheader("📋 예측 결과")

    result_df = pd.DataFrame({"PassengerId": test_df["PassengerId"], "Survived": predictions})
    result_df["Survived"] = result_df["Survived"].map({0: "❌ 사망", 1: "✅ 생존"})
    result_df = result_df.merge(test_df[["PassengerId", "Name"]], on="PassengerId", how="left")

    survived_count = (result_df["Survived"] == "✅ 생존").sum()
    not_survived_count = (result_df["Survived"] == "❌ 사망").sum()
    pie_labels = [' 생존', ' 사망']
    pie_sizes = [survived_count, not_survived_count]
    pie_colors = ["#c4f2d1", '#f7bdbb']

    fig, ax = plt.subplots()
    fig.patch.set_alpha(0.0)
    wedges, texts, autotexts = ax.pie(
        pie_sizes,
        labels=pie_labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=pie_colors,
        textprops={'fontsize': 12, 'fontproperties': font_prop} if font_prop else {'fontsize': 12}
    )
    ax.axis('equal')
    ax.set_title("예측 생존 분포", fontproperties=font_prop)
    st.pyplot(fig)

    st.markdown("### 🟢 생존자 명단")
    df_survived = result_df[result_df["Survived"] == "✅ 생존"].reset_index(drop=True)
    df_survived.index += 1
    styled_survived = df_survived[["Name", "Survived"]].rename_axis("번호").style.set_properties(
        **{'background-color': "#e2f7e8", 'border-color': "#c4f2d1", 'color': '#111'}
    )
    st.dataframe(styled_survived, use_container_width=True)

    st.markdown("### 🔴 사망자 명단")
    df_not_survived = result_df[result_df["Survived"] == "❌ 사망"].reset_index(drop=True)
    df_not_survived.index += 1
    styled_not_survived = df_not_survived[["Name", "Survived"]].rename_axis("번호").style.set_properties(
        **{'background-color': '#fdecea', 'border-color': '#f7bdbb', 'color': '#111'}
    )
    st.dataframe(styled_not_survived, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# 📬 승객 검색
elif section == "📬 승객 검색":
    st.markdown("<div class='slide'>", unsafe_allow_html=True)
    st.subheader("📬 승객 검색")
    search_name = st.text_input("🔎 승객 이름 입력")
    gender_filter = st.selectbox("성별", options=["전체", "남성", "여성"])
    age_range = st.slider("나이 범위", min_value=0, max_value=80, value=(0, 80))

    filtered_df = train_df.copy()
    if search_name:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(search_name, case=False, na=False)]
    if gender_filter != "전체":
        gender_val = 0 if gender_filter == "남성" else 1
        filtered_df = filtered_df[filtered_df["Sex"] == gender_val]
    filtered_df = filtered_df[(filtered_df["Age"] >= age_range[0]) & (filtered_df["Age"] <= age_range[1])]
    
    filtered_df['Age'] = filtered_df['Age'].round(0).astype('Int64')  
    filtered_df['Fare'] = filtered_df['Fare'].apply(lambda x: f"{x:.3f}")
    
    styled_filtered = filtered_df[['Name', 'Sex', 'Age', 'Fare', 'Pclass', 'Survived']].style.set_properties(
        **{
            'background-color':"#e2f7e8",
            'border-color': "#c4f2d1",
            'color': '#111'
        }
    )
    st.dataframe(styled_filtered, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

if section == "📈 시각화 차트":
    st.markdown("<div class='slide'>", unsafe_allow_html=True)
    st.subheader("📈 시각화 차트")

    tab_labels = [
        "♂️♀️ 성별", "🎂 연령대",
        "👨‍👩‍👧‍👦 동반 가족 수", "💰 요금",
        "🔥 상관관계 히트맵"
    ]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        fig, ax = plt.subplots(figsize=(2.8, 1.2))
        train_df.groupby('Sex')['Survived'].mean().plot(kind='bar', color=['#87CEFA', '#FFB6C1'], ax=ax)
        ax.set_xlabel("") 
        ax.set_xticklabels(['남성', '여성'], rotation=0, fontsize=7)
        ax.tick_params(axis='both', labelbottom=True, labelleft=True)
        plt.subplots_adjust(bottom=0.15)

        fig.text(0.01, 0.99, "생존률", ha='left', va='top', fontsize=7, fontproperties=font_prop)
        fig.text(0.99, 0.01, "성별", ha='right', va='bottom', fontsize=7, fontproperties=font_prop)
        fig.text(0.5, -0.15, "성별에 따른 생존률", ha='center', fontsize=9, fontproperties=font_prop)
        st.pyplot(fig)
        st.markdown("""
- 여성의 생존률이 남성보다 **현저히 높게** 나타납니다.  
- 이는 타이타닉 사고 당시 **"여성과 아이들 우선"** 원칙이 적용된 결과일 수 있습니다.  
- 성별은 생존 여부 예측에 있어 매우 중요한 변수입니다.
""")
    with tabs[1]:
        fig, ax = plt.subplots(figsize=(2.8, 1.2))
        age_bins = pd.cut(train_df['Age'], bins=[0, 12, 18, 35, 60, 100])
        train_df.groupby(age_bins)['Survived'].mean().plot(kind='bar', color='#AED581', ax=ax)
        labels = ['12', '18', '35', '60', '100']
        ax.set_xticklabels(labels, rotation=0, fontsize=7)

        ax.set_xlabel("")
        ax.tick_params(axis='both', labelsize =7, labelbottom=True, labelleft=True)
        plt.subplots_adjust(bottom=0.15)
        fig.text(0.01, 0.99, "생존률", ha='left', va='top', fontsize=7, fontproperties=font_prop)
        fig.text(0.99, 0.01, "연령대", ha='right', va='bottom', fontsize=7, fontproperties=font_prop)
        fig.text(0.5, -0.15, "연령대별 생존률", ha='center', fontsize=9, fontproperties=font_prop)
        st.pyplot(fig)
        st.markdown("""
- **12세 이하 어린이**의 생존률이 가장 높게 나타납니다.  
- 반면, **중장년층(35세 이상)**의 생존률은 상대적으로 낮습니다.  
- 나이는 생존 여부에 영향을 주는 **의미 있는 변수**입니다.
""")

    with tabs[2]:
        fig, ax = plt.subplots(figsize=(2.5, 1.2))
        df_filtered = train_df[train_df['SibSp'] <= 4]
        df_filtered.groupby('SibSp')['Survived'].mean().plot(kind='bar', color="#71CFC2", ax=ax)
        ax.set_xlabel("")
        ax.tick_params(axis='both', labelsize=7,labelbottom=True, labelleft=True)
        plt.subplots_adjust(bottom=0.15)
        fig.text(0.01, 0.99, "생존률", ha='left', va='top', fontsize=7, fontproperties=font_prop)
        fig.text(0.99, 0.01, "동반\n가족\n수 ", ha='right', va='bottom', fontsize=7, fontproperties=font_prop)
        fig.text(0.5, -0.15, "동반 가족 수에 따른 생존률", ha='center', fontsize=9, fontproperties=font_prop)
        st.pyplot(fig)
        st.markdown("""
- **1~2명의 가족과 동반한 승객**의 생존률이 가장 높게 나타납니다.  
- **혼자 탑승했거나 가족이 너무 많은 경우** 생존률이 낮아지는 경향이 있습니다.  
- 가족 구성원 수는 생존 여부에 **영향을 미치는 요인** 중 하나입니다.
""")

    with tabs[3]:
        fig, ax = plt.subplots(figsize=(2.8, 1.2))
        fare_bins = pd.qcut(train_df['Fare'], q=5)
        fare_grouped = train_df.groupby(fare_bins)['Survived'].mean()
        fare_grouped.plot(kind='bar', color="#A689A9", ax=ax)
        labels = ['~7.8', '7.8~10', '10~21', '21~39', '39~512']
        ax.set_xticklabels(labels, rotation=0, fontsize=7)

        ax.set_xlabel("")
        ax.tick_params(axis='both', labelsize=7, labelbottom=True, labelleft=True)
        plt.subplots_adjust(bottom=0.15)
        fig.text(0.01, 0.99, "생존률", ha='left', va='top', fontsize=7, fontproperties=font_prop)
        fig.text(0.99, 0.01, "요금\n구간", ha='right', va='bottom', fontsize=7, fontproperties=font_prop)
        fig.text(0.5, -0.18, "요금 구간별 생존률", ha='center', fontsize=9, fontproperties=font_prop)

        st.pyplot(fig)
        st.markdown("""
- **요금이 높을수록 생존률이 증가**하는 경향을 보입니다.  
- 이는 고급 객실을 이용한 승객이 구조 우선 순위에 있었음을 시사합니다.  
- 요금은 생존 가능성을 가늠할 수 있는 **중요한 사회적 지표**입니다.
""")

    with tabs[4]:
        st.markdown("<div class='slide'>", unsafe_allow_html=True)
        st.subheader("📈 상관관계 히트맵")

        fig, ax = plt.subplots(figsize=(7.5, 3.2))
        corr_display = train_df[['Survived', 'Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'FamilySize']].corr()
        custom_cmap = sns.light_palette("#d87f7f", reverse=True, as_cmap=True)

        heatmap = sns.heatmap(
    corr_display,
    cmap=custom_cmap,
    ax=ax,
    annot=True,
    fmt=".2f",
    annot_kws={'fontsize': 7},
    vmin=-1, vmax=1,
    cbar=True,
    cbar_kws={"shrink": 0.5}
)

        cbar = heatmap.collections[0].colorbar
        cbar.set_ticks([-1.0, -0.5, 0.0, 0.5, 1.0])
        cbar.set_ticklabels(['-1.0', '-0.5', '0.0', '0.5', '1.0'])

        ax.set_xticklabels(ax.get_xticklabels(), rotation=30, fontsize=8)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)
        ax.set_xlabel("")
        ax.set_ylabel("")

        fig.text(0.05, 0.99, "변수", ha='left', va='top', fontsize=8, fontproperties=font_prop)
        fig.text(0.85, 0.1, "변수", ha='right', va='bottom', fontsize=8, fontproperties=font_prop)
        fig.text(0.5, 0, "상관관계 히트맵 ", ha='center', fontsize=13, fontproperties=font_prop)

        fig.tight_layout(pad=0.5)
        st.pyplot(fig, use_container_width=True)

        st.markdown("""
- 색상이 진할수록 생존에 **부정적인 영향을 주는 변수**입니다.  
- 예를 들어, `성별(Sex)`은 생존과 비교적 강한 상관관계를 보이며, `요금(Fare)`은 약한 양의 관계를 보입니다.  
- 단일 변수로는 예측이 어렵기 때문에, 다양한 변수 조합이 중요합니다.
""")
    st.markdown("</div>", unsafe_allow_html=True)
