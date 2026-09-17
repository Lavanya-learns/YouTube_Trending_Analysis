import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="YouTube Trending Analytics",
    page_icon="📺",
    layout="wide"
)

# -----------------------------
# Dashboard styling
# -----------------------------

st.markdown("""
<style>

    .main {
        background-color: #f8fafc;
    }

    h1 {
        font-weight: 700;
    }

    h2, h3 {
        font-weight: 600;
    }

    [data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
    }

</style>
""", unsafe_allow_html=True)


# Chart colors
blue = "#2563EB"
teal = "#14B8A6"
purple = "#8B5CF6"
orange = "#F59E0B"
red = "#EF4444"
cyan = "#06B6D4"
green = "#10B981"


# -----------------------------
# Load dataset
# -----------------------------

df = pd.read_csv("INvideos.csv")

# Remove exact duplicates
df = df.drop_duplicates()

# Fill missing descriptions
df["description"] = df["description"].fillna("")


# -----------------------------
# Convert dates
# -----------------------------

df["trending_date"] = pd.to_datetime(
    df["trending_date"],
    format="%y.%d.%m"
)

df["publish_time"] = pd.to_datetime(
    df["publish_time"],
    utc=True
)


# -----------------------------
# Convert publishing time to India time
# -----------------------------

df["publish_time_ist"] = df["publish_time"].dt.tz_convert(
    "Asia/Kolkata"
)


# -----------------------------
# Create date features
# -----------------------------

df["publish_hour_ist"] = df["publish_time_ist"].dt.hour

df["publish_day_ist"] = df["publish_time_ist"].dt.day_name()


# -----------------------------
# Days taken to become trending
# -----------------------------

df["days_to_trend"] = (
    df["trending_date"].dt.tz_localize("UTC")
    - df["publish_time"].dt.normalize()
).dt.days


# -----------------------------
# Dashboard title
# -----------------------------

st.title("📺 YouTube Trending Analytics")

st.markdown(
    "### Exploring trending video patterns, audience engagement and publishing trends in India"
)

st.divider()


# -----------------------------
# Sidebar filters
# -----------------------------

st.sidebar.header("🔎 Dashboard Filters")

min_date = df["trending_date"].min().date()

max_date = df["trending_date"].max().date()


selected_dates = st.sidebar.date_input(
    "Trending Date",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


channels = sorted(
    df["channel_title"].dropna().unique()
)


selected_channel = st.sidebar.selectbox(
    "Channel",
    ["All Channels"] + channels
)


min_views = st.sidebar.number_input(
    "Minimum Views",
    min_value=0,
    value=0,
    step=100000
)


# -----------------------------
# Apply filters
# -----------------------------

filtered_df = df.copy()


if len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        (filtered_df["trending_date"].dt.date >= start_date)
        & (filtered_df["trending_date"].dt.date <= end_date)
    ]


if selected_channel != "All Channels":

    filtered_df = filtered_df[
        filtered_df["channel_title"] == selected_channel
    ]


filtered_df = filtered_df[
    filtered_df["views"] >= min_views
]


# -----------------------------
# KPI cards
# -----------------------------

total_videos = len(filtered_df)

total_views = filtered_df["views"].sum()

total_likes = filtered_df["likes"].sum()

total_comments = filtered_df["comment_count"].sum()


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "📹 Trending Records",
    f"{total_videos:,}"
)


col2.metric(
    "👀 Total Views",
    f"{total_views / 1e9:.2f}B"
)


col3.metric(
    "👍 Total Likes",
    f"{total_likes / 1e6:.1f}M"
)


col4.metric(
    "💬 Total Comments",
    f"{total_comments / 1e6:.1f}M"
)


st.divider()


# -----------------------------
# Engagement KPIs
# -----------------------------

avg_likes = filtered_df["likes"].mean()

avg_comments = filtered_df["comment_count"].mean()

avg_views = filtered_df["views"].mean()


col1, col2, col3 = st.columns(3)


col1.metric(
    "📊 Average Views",
    f"{avg_views / 1e6:.2f}M"
)


col2.metric(
    "👍 Average Likes",
    f"{avg_likes / 1e3:.1f}K"
)


col3.metric(
    "💬 Average Comments",
    f"{avg_comments / 1e3:.1f}K"
)


st.divider()


# -----------------------------
# Trending activity over time
# -----------------------------

st.subheader("📈 Trending Activity Over Time")


trending_over_time = (
    filtered_df.groupby("trending_date")["video_id"]
    .count()
    .reset_index(name="video_count")
)


fig = px.line(
    trending_over_time,
    x="trending_date",
    y="video_count",
    markers=True,
    title="Number of Trending Videos Over Time",
    color_discrete_sequence=[teal]
)


fig.update_layout(
    xaxis_title="Trending Date",
    yaxis_title="Number of Videos",
    template="plotly_white"
)


st.plotly_chart(
    fig,
    use_container_width=True,
    key="trending_over_time_chart"
)


# -----------------------------
# Channel and engagement analysis
# -----------------------------

col1, col2 = st.columns(2)


# -----------------------------
# Top 10 channels
# -----------------------------

with col1:

    st.subheader("🏆 Top 10 Channels")

    top_channels = (
        filtered_df["channel_title"]
        .value_counts()
        .head(10)
        .sort_values()
        .reset_index()
    )

    top_channels.columns = [
        "channel_title",
        "video_count"
    ]

    fig_channels = px.bar(
        top_channels,
        x="video_count",
        y="channel_title",
        orientation="h",
        title="Channels with the Most Trending Videos",
        color_discrete_sequence=[purple]
    )

    fig_channels.update_layout(
        xaxis_title="Trending Videos",
        yaxis_title="",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_channels,
        use_container_width=True,
        key="top_channels_chart"
    )


# -----------------------------
# Views vs Likes
# -----------------------------

with col2:

    st.subheader("👀 Views vs Likes")

    fig_engagement = px.scatter(
        filtered_df,
        x="views",
        y="likes",
        title="Relationship Between Views and Likes",
        opacity=0.4,
        color_discrete_sequence=[blue]
    )

    fig_engagement.update_layout(
        xaxis_title="Views",
        yaxis_title="Likes",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_engagement,
        use_container_width=True,
        key="views_likes_chart"
    )


# -----------------------------
# Views vs Comments
# -----------------------------

with col1:

    st.subheader("💬 Views vs Comments")

    fig_comments = px.scatter(
        filtered_df,
        x="views",
        y="comment_count",
        title="Relationship Between Views and Comments",
        opacity=0.4,
        color_discrete_sequence=[orange]
    )

    fig_comments.update_layout(
        xaxis_title="Views",
        yaxis_title="Comments",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_comments,
        use_container_width=True,
        key="views_comments_chart"
    )


# -----------------------------
# Publishing Hour
# -----------------------------

with col2:

    st.subheader("🕐 Publishing Hour (IST)")

    hourly_activity = (
        filtered_df["publish_hour_ist"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    hourly_activity.columns = [
        "publish_hour",
        "video_count"
    ]

    fig_hour = px.bar(
        hourly_activity,
        x="publish_hour",
        y="video_count",
        title="Trending Videos by Publishing Hour",
        color_discrete_sequence=[green]
    )

    fig_hour.update_layout(
        xaxis_title="Publishing Hour (IST)",
        yaxis_title="Number of Videos",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_hour,
        use_container_width=True,
        key="publishing_hour_chart"
    )


# -----------------------------
# Publishing Day
# -----------------------------

with col1:

    st.subheader("📅 Publishing Day (IST)")

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    daily_activity = (
        filtered_df["publish_day_ist"]
        .value_counts()
        .reindex(day_order)
        .fillna(0)
        .reset_index()
    )

    daily_activity.columns = [
        "publish_day",
        "video_count"
    ]

    fig_day = px.bar(
        daily_activity,
        x="publish_day",
        y="video_count",
        title="Trending Videos by Publishing Day",
        color_discrete_sequence=[cyan]
    )

    fig_day.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Number of Videos",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_day,
        use_container_width=True,
        key="publishing_day_chart"
    )


# -----------------------------
# Average Views by Category
# -----------------------------

with col2:

    st.subheader("📊 Average Views by Category")

    category_views = (
        filtered_df.groupby("category_id")["views"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    category_views["category_id"] = (
        category_views["category_id"]
        .astype(str)
    )

    fig_category = px.bar(
        category_views,
        x="category_id",
        y="views",
        title="Average Views by YouTube Category",
        color_discrete_sequence=[teal]
    )

    fig_category.update_layout(
        xaxis_title="Category ID",
        yaxis_title="Average Views",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True,
        key="category_views_chart"
    )


# -----------------------------
# Days to Become Trending
# -----------------------------

st.subheader("⏱️ Days to Become Trending")


trend_days = (
    filtered_df["days_to_trend"]
    .value_counts()
    .sort_index()
    .reset_index()
)


trend_days.columns = [
    "days_to_trend",
    "video_count"
]


fig_days = px.bar(
    trend_days,
    x="days_to_trend",
    y="video_count",
    title="How Quickly Videos Become Trending",
    color_discrete_sequence=[orange]
)


fig_days.update_layout(
    xaxis_title="Days to Become Trending",
    yaxis_title="Number of Videos",
    template="plotly_white"
)


st.plotly_chart(
    fig_days,
    use_container_width=True,
    key="days_to_trend_chart"
)
