import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "1년간 박스오피스 10위권에 든 영화 가운데 이 기간에 개봉한 216편의 데이터를 바탕으로 "
    "분포와 관계를 살펴보는 그래프 모음입니다."
)


@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 장르가 세로막대(|) 기호로 여러 개 적혀 있으면 첫 번째 장르만 사용
    df["genre"] = df["genre"].astype(str).apply(lambda x: x.split("|")[0].strip())

    # 개봉일(여덟 자리 숫자) -> datetime 변환
    df["openDt"] = pd.to_datetime(df["openDt"].astype(str), format="%Y%m%d", errors="coerce")

    return df


df = load_data()

with st.expander("📄 원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ------------------------------------------------------------
# 구역 1. 장르별 영화 편수 분포
# ------------------------------------------------------------
st.header("1. 장르별 영화 편수 분포")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
)
fig_genre.update_traces(
    textinfo="label+percent",
    hovertemplate="%{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_genre.update_layout(margin=dict(t=20, b=20, l=0, r=0))

st.plotly_chart(fig_genre, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: ")

st.divider()

# ------------------------------------------------------------
# 구역 2. 장르 안 영화별 총 관객 트리맵
# ------------------------------------------------------------
st.header("2. 장르 안 영화별 총 관객 트리맵")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
)
fig_treemap.update_traces(
    hovertemplate="영화명: %{label}<br>총 관객: %{value:,}명<extra></extra>",
)
fig_treemap.update_layout(margin=dict(t=20, b=20, l=0, r=0))

st.plotly_chart(fig_treemap, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: ")

st.divider()

# ------------------------------------------------------------
# 구역 3. 총 관객 히스토그램
# ------------------------------------------------------------
st.header("3. 총 관객 분포")

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=30,
)
fig_hist.update_traces(
    hovertemplate="구간: %{x}<br>영화 수: %{y}편<extra></extra>",
)
fig_hist.update_layout(
    margin=dict(t=20, b=20, l=0, r=0),
    xaxis_title="총 관객 수",
    yaxis_title="영화 수",
    bargap=0.05,
)

st.plotly_chart(fig_hist, use_container_width=True)

# 가장 영화가 몰린 구간, 최다 관객 영화 자동 계산
counts, bin_edges = np.histogram(df["total_audi"], bins=30)
max_bin_idx = counts.argmax()
bin_start = bin_edges[max_bin_idx]
bin_end = bin_edges[max_bin_idx + 1]

top_movie_row = df.loc[df["total_audi"].idxmax()]

st.info(
    f"💡 이 그래프로 알 수 있는 것: 대부분의 영화는 총 관객 "
    f"약 {bin_start:,.0f}명 ~ {bin_end:,.0f}명 구간에 몰려 있으며({counts[max_bin_idx]}편), "
    f"가장 많은 관객을 동원한 영화는 '{top_movie_row['movieNm']}'"
    f"(총 관객 {top_movie_row['total_audi']:,}명)입니다."
)

st.divider()

# ------------------------------------------------------------
# 구역 4. 개봉일 스크린수 vs 총 관객 산점도
# ------------------------------------------------------------
st.header("4. 개봉일 스크린수와 총 관객의 관계")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
)
fig_scatter.update_traces(
    hovertemplate="%{hovertext}<br>개봉일 스크린수: %{x:,}개<br>총 관객: %{y:,}명<extra></extra>",
)
fig_scatter.update_layout(
    margin=dict(t=20, b=20, l=0, r=0),
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title="장르",
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: ")

st.divider()

# ------------------------------------------------------------
# 구역 5. 영화 10편 이상 장르의 총 관객 박스플롯
# ------------------------------------------------------------
st.header("5. 장르별 총 관객 분포 (10편 이상 장르)")

genre_movie_counts = df["genre"].value_counts()
major_genres = genre_movie_counts[genre_movie_counts >= 10].index
df_major = df[df["genre"].isin(major_genres)]

fig_box = px.box(
    df_major,
    x="genre",
    y="total_audi",
    hover_name="movieNm",
    points="outliers",
)
fig_box.update_traces(
    hovertemplate="%{hovertext}<br>총 관객: %{y:,}명<extra></extra>",
)
fig_box.update_layout(
    margin=dict(t=20, b=20, l=0, r=0),
    xaxis_title="장르",
    yaxis_title="총 관객 수",
)

st.plotly_chart(fig_box, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: ")

st.divider()

# ------------------------------------------------------------
# (앞으로 그래프가 계속 추가될 구역)
# ------------------------------------------------------------
# st.header("6. ...")
