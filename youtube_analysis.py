import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("INvideos.csv")

print(df.shape)
print(df.columns)
print(df.info())

# Check for duplicate rows
print("Duplicate rows:", df.duplicated().sum())
print("Unique video IDs:", df["video_id"].nunique())

# Remove exact duplicate rows
df = df.drop_duplicates()
print("Rows after removing duplicates:", len(df))

# Check missing values
print("Missing values:")
print(df.isnull().sum())

# Fill missing descriptions
df["description"] = df["description"].fillna("")

# Check again
print("Missing description values after filling:",
      df["description"].isnull().sum())

# Convert date columns
df["trending_date"] = pd.to_datetime(
    df["trending_date"],
    format="%y.%d.%m"
)

df["publish_time"] = pd.to_datetime(
    df["publish_time"],
    utc=True
)

# Create useful date features
df["publish_date"] = df["publish_time"].dt.date
df["publish_hour"] = df["publish_time"].dt.hour
df["publish_day"] = df["publish_time"].dt.day_name()

print(df[["publish_date", "publish_hour", "publish_day"]].head())

# Calculate days taken to become trending
df["days_to_trend"] = (
    df["trending_date"].dt.tz_localize("UTC")
    - df["publish_time"].dt.normalize()
).dt.days

print(df[["publish_time", "trending_date", "days_to_trend"]].head())


# Top 10 channels by number of trending videos
top_channels = (
    df["channel_title"]
    .value_counts()
    .head(10)
    .sort_values()
)

plt.figure(figsize=(12, 7))

bars = plt.barh(
    top_channels.index,
    top_channels.values
)

# Title and labels
plt.title(
    "Top 10 YouTube Channels in India's Trending Videos",
    fontsize=18,
    fontweight="bold",
    pad=20
)

plt.xlabel(
    "Number of Trending Videos",
    fontsize=12
)

# Remove unnecessary chart borders
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)
plt.gca().spines["left"].set_visible(False)

# Add light horizontal grid
plt.grid(
    axis="x",
    linestyle="--",
    alpha=0.3
)

# Put the grid behind the bars
plt.gca().set_axisbelow(True)

# Add values to bars
for bar in bars:
    width = bar.get_width()

    plt.text(
        width + 5,
        bar.get_y() + bar.get_height() / 2,
        f"{int(width):,}",
        va="center",
        fontsize=10,
        fontweight="bold"
    )

# Improve spacing
plt.tight_layout()

# Save high-quality image
plt.savefig(
    "top_10_channels.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Trending videos over time

trending_over_time = (
    df.groupby("trending_date")["video_id"]
    .count()
)

plt.figure(figsize=(12, 6))

plt.plot(
    trending_over_time.index,
    trending_over_time.values,
    linewidth=2.5
)

plt.title(
    "Trending Video Activity Over Time",
    fontsize=18,
    fontweight="bold",
    pad=20
)

plt.xlabel("Trending Date", fontsize=12)
plt.ylabel("Number of Trending Videos", fontsize=12)

# Clean chart appearance
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

plt.gca().set_axisbelow(True)

plt.tight_layout()

plt.savefig(
    "trending_videos_over_time.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Views vs Likes

plt.figure(figsize=(12, 7))

plt.scatter(
    df["views"],
    df["likes"],
    alpha=0.35,
    s=25
)

plt.title(
    "Views vs Likes: Understanding Audience Engagement",
    fontsize=18,
    fontweight="bold",
    pad=20
)

plt.xlabel("Views", fontsize=12)
plt.ylabel("Likes", fontsize=12)

# Remove unnecessary borders
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

plt.grid(
    linestyle="--",
    alpha=0.25
)

plt.gca().set_axisbelow(True)

plt.tight_layout()

plt.savefig(
    "views_vs_likes.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Views vs Comments

plt.figure(figsize=(12, 7))

plt.scatter(
    df["views"],
    df["comment_count"],
    alpha=0.35,
    s=25,
    color="#8E44AD"
)

plt.title(
    "Views vs Comments: Measuring Audience Discussion",
    fontsize=18,
    fontweight="bold",
    pad=20
)

plt.xlabel("Views", fontsize=12)
plt.ylabel("Comments", fontsize=12)

# Remove unnecessary borders
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

plt.grid(
    linestyle="--",
    alpha=0.25
)

plt.gca().set_axisbelow(True)

plt.tight_layout()

plt.savefig(
    "views_vs_comments.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Convert publishing time to IST
df["publish_time_ist"] = df["publish_time"].dt.tz_convert("Asia/Kolkata")

df["publish_hour_ist"] = df["publish_time_ist"].dt.hour

# Trending videos by publishing hour
hourly_trending = (
    df.groupby("publish_hour_ist")["video_id"]
    .count()
)

plt.figure(figsize=(12, 7))

bars = plt.bar(
    hourly_trending.index,
    hourly_trending.values,
    color="#E67E22"
)

plt.title(
    "Trending Activity by Publishing Hour (IST)",
    fontsize=18,
    fontweight="bold",
    pad=20
)

plt.xlabel("Publishing Hour (IST)", fontsize=12)
plt.ylabel("Number of Trending Videos", fontsize=12)

# Clean appearance
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

plt.gca().set_axisbelow(True)

plt.xticks(range(24))

plt.tight_layout()

plt.savefig(
    "trending_activity_by_hour.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Trending videos by day of the week

day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

trending_by_day = (
    df.groupby("publish_day")["video_id"]
    .count()
    .reindex(day_order)
)

plt.figure(figsize=(12, 7))

bars = plt.bar(
    trending_by_day.index,
    trending_by_day.values,
    color="#16A085"
)

plt.title(
    "Trending Activity by Publishing Day",
    fontsize=18,
    fontweight="bold",
    pad=20
)

plt.xlabel("Day of the Week", fontsize=12)
plt.ylabel("Number of Trending Videos", fontsize=12)

# Clean appearance
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

plt.gca().set_axisbelow(True)

# Add values above bars
for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + 50,
        f"{int(height):,}",
        ha="center",
        fontsize=10,
        fontweight="bold"
    )

plt.tight_layout()

plt.savefig(
    "trending_activity_by_day.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Days taken for videos to become trending

plt.figure(figsize=(12, 7))

plt.hist(
    df["days_to_trend"],
    bins=30,
    color="#3498DB",
    edgecolor="white",
    alpha=0.9
)

plt.title(
    "How Quickly Videos Become Trending",
    fontsize=18,
    fontweight="bold",
    pad=20
)

plt.xlabel(
    "Days Taken to Become Trending",
    fontsize=12
)

plt.ylabel(
    "Number of Trending Videos",
    fontsize=12
)

# Clean appearance
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

plt.gca().set_axisbelow(True)

plt.tight_layout()

plt.savefig(
    "days_to_trend_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Average views by YouTube category

category_views = (
    df.groupby("category_id")["views"]
    .mean()
    .sort_values(ascending=False)
)

plt.figure(figsize=(12, 7))

bars = plt.bar(
    category_views.index.astype(str),
    category_views.values,
    color="#2E86C1"
)

plt.title(
    "Average Views by YouTube Category",
    fontsize=18,
    fontweight="bold",
    pad=20
)

plt.xlabel(
    "Category ID",
    fontsize=12
)

plt.ylabel(
    "Average Views",
    fontsize=12
)

# Clean appearance
plt.gca().spines["top"].set_visible(False)
plt.gca().spines["right"].set_visible(False)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

plt.gca().set_axisbelow(True)

# Format large numbers
plt.ticklabel_format(
    style="plain",
    axis="y"
)

plt.tight_layout()

plt.savefig(
    "average_views_by_category.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
