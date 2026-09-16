import streamlit as st
from googleapiclient.discovery import build

st.set_page_config(page_title="YouTuben Trendit Aiheittain", page_icon="🎯", layout="wide")

st.title("🎯 YouTuben suosituimmat videot aiheittain")
st.write("Tämä sovellus hakee Suomen trendaavat videot ja järjestää ne automaattisesti aihe-alueittain.")

# Sanakirja YouTube-kategorioiden tunnuksille ja niiden suomenkielisille nimille
CATEGORY_MAPPING = {
    "20": "🎮 Pelaaminen",
    "23": "😂 Komedia",
    "24": "🍿 Viihde",
    "22": "👥 Ihmiset ja blogit",
    "10": "🎵 Musiikki",
    "17": "⚽ Urheilu",
    "25": "📰 Uutiset ja politiikka"
}

try:
    api_key = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.error("YouTube API-avainta ei ole asetettu Streamlitin salaisuuksiin (Secrets).")
else:
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        
        with st.spinner("Haetaan trendaavia videoita..."):
            # Haetaan laajempi otanta (max 50) suosituimpia videoita Suomesta
            request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode="FI",
                maxResults=50
            )
            response = request.execute()

        items = response.get("items", [])
        
        if not items:
            st.info("Videoita ei löytynyt.")
        else:
            # Ryhmitellään videot kategorian mukaan
            categorized_videos = {}
            for item in items:
                cat_id = item["snippet"].get("categoryId", "muu")
                cat_name = CATEGORY_MAPPING.get(cat_id, "📁 Muut aiheet")
                
                if cat_name not in categorized_videos:
                    categorized_videos[cat_name] = []
                categorized_videos[cat_name].append(item)
            
            # Käydään ryhmät läpi ja näytetään ne omilla osioillaan
            for cat_name, videos in categorized_videos.items():
                st.header(cat_name)
                
                cols = st.columns(3)
                for index, item in enumerate(videos):
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
