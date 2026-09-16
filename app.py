import streamlit as st
from googleapiclient.discovery import build
import isodate

st.set_page_config(page_title="YouTuben Trendit Aiheittain", page_icon="🎯", layout="wide")

st.title("🎯 YouTuben suosituimmat videot aiheittain")
st.write("Valitse aihe-alue sivupalkista. (Shorts-videot on suodatettu automaattisesti pois!)")

CATEGORIES = {
    "23": "😂 Komedia",
    "24": "🍿 Viihde",
    "17": "⚽ Urheilu",
    "20": "🎮 Pelaaminen",
    "10": "🎵 Musiikki",
    "22": "👥 Ihmiset ja blogit",
    "25": "📰 Uutiset ja politiikka"
}

st.sidebar.header("Suodattimet")
selected_category_name = st.sidebar.selectbox(
    "Valitse aihe-alue:",
    list(CATEGORIES.values())
)

selected_category_id = [cat_id for cat_id, name in CATEGORIES.items() if name == selected_category_name][0]

try:
    api_key = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.error("YouTube API-avainta ei ole asetettu Streamlitin salaisuuksiin (Secrets).")
else:
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        
        with st.spinner(f"Haetaan videoita aiheesta: {selected_category_name}..."):
            # Haetaan isompi nippu (esim. 40), jotta suodatuksen jälkeen riittää pitkiä videoita
            request = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                chart="mostPopular",
                regionCode="FI",
                videoCategoryId=selected_category_id,
                maxResults=40
            )
            response = request.execute()

        items = response.get("items", [])
        
        # Suodatetaan Shorts-videot pois (kesto alle 60 sekuntia)
        filtered_items = []
        for item in items:
            duration_str = item["contentDetails"]["duration"]
            duration = isodate.parse_duration(duration_str)
            
            if duration.total_seconds() > 60:
                filtered_items.append(item)
                
            # Asetetaan halutuksi maksimimääräksi nyt esimerkiksi 24 kpl
            if len(filtered_items) >= 24:
                break

        if not filtered_items:
            st.info("Ei löytynyt sopivia pitkiä videoita valitusta kategoriasta tällä hetkellä.")
        else:
            st.header(f"{selected_category_name} (Näytetään {len(filtered_items)} suosituinta)")
            
            # Luodaan 4 saraketta, jotta useampi video mahtuu siististi rinnakkain
            cols = st.columns(4)
            for index, item in enumerate(filtered_items):
                title = item["snippet"]["title"]
                channel = item["snippet"]["channelTitle"]
                views = int(item["statistics"].get("viewCount", 0))
                video_id = item["id"]
                url = f"https://www.youtube.com/watch?v={video_id}"
                
                with cols[index % 4]:
                    st.subheader(title)
                    st.write(f"📺 **Kanava:** {channel}")
                    st.write(f"👁️ **Katselukerrat:** {views:,}".replace(",", " "))
                    st.markdown(f"[Katso videosta]({url})")
                    st.video(url)
                    st.divider()

    except Exception as e:
        st.error(f"Virhe haussa: {e}")
