import streamlit as st
from googleapiclient.discovery import build

st.set_page_config(page_title="YouTuben Top Hauskat", page_icon="😂", layout="wide")

st.title("😂 Tämän hetken suosituimmat hauskat videot")
st.write("Tämä sovellus hakee YouTuben trendaavia komediavideoita reaaliajassa YouTube Data API:n avulla.")

# Haetaan API-avain Streamlitin salaisuuksista (st.secrets)
try:
    api_key = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.error("YouTube API-avainta ei ole asetettu Streamlitin salaisuuksiin (Secrets). Lisää se sovelluksen asetuksiin.")
else:
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        
        with st.spinner("Haetaan videoita YouTubesta..."):
            request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode="FI",
                maxResults=12,
                videoCategoryId="23"
            )
            response = request.execute()

        items = response.get("items", [])
        
        if not items:
            st.info("Videoita ei löytynyt.")
        else:
            cols = st.columns(3)
            for index, item in enumerate(items):
                title = item["snippet"]["title"]
                channel = item["snippet"]["channelTitle"]
                views = int(item["statistics"].get("viewCount", 0))
                video_id = item["id"]
                url = f"https://www.youtube.com/watch?v={video_id}"
                
                with cols[index % 3]:
                    st.subheader(title)
                    st.write(f"📺 **Kanava:** {channel}")
                    st.write(f"👁️ **Katselukerrat:** {views:,}".replace(",", " "))
                    st.markdown(f"[Katso videosta]({url})")
                    st.video(url)
                    st.divider()

    except Exception as e:
        st.error(f"Virhe haussa: {e}")
