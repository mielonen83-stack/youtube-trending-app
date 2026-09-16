import streamlit as st
from googleapiclient.discovery import build

st.set_page_config(page_title="YouTuben Trendit Aiheittain", page_icon="🎯", layout="wide")

st.title("🎯 YouTuben suosituimmat videot aiheittain")
st.write("Valitse alta tai sivupalkista haluamasi aihe-alue, niin näet Suomen katsotuimmat videot siltä saralta!")

# Kategorioiden sanakirja (Avain = API:n kategoria-ID, Arvo = Näytettävä nimi)
CATEGORIES = {
    "23": "😂 Komedia",
    "24": "🍿 Viihde",
    "17": "⚽ Urheilu",
    "20": "🎮 Pelaaminen",
    "10": "🎵 Musiikki",
    "22": "👥 Ihmiset ja blogit",
    "25": "📰 Uutiset ja politiikka"
}

# Luodaan sivupalkkiin valikko aiheista
st.sidebar.header("Suodattimet")
selected_category_name = st.sidebar.selectbox(
    "Valitse aihe-alue:",
    list(CATEGORIES.values())
)

# Etsitään valittua nimeä vastaava ID
selected_category_id = [cat_id for cat_id, name in CATEGORIES.items() if name == selected_category_name][0]

try:
    api_key = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.error("YouTube API-avainta ei ole asetettu Streamlitin salaisuuksiin (Secrets). Lisää se asetuksiin.")
else:
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        
        with st.spinner(f"Haetaan aihekonetta: {selected_category_name}..."):
            # Haetaan suosittuja videoita suoraan kyseisestä kategoriasta Suomessa
            request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode="FI",
                videoCategoryId=selected_category_id,
                maxResults=12
            )
            response = request.execute()

        items = response.get("items", [])
        
        if not items:
            st.info(s="Ei löytynyt videoita valitusta kategoriasta tällä hetkellä.")
        else:
            st.header(selected_category_name)
            
            # Näytetään videot siistissä 3 sarakkeen ruudukossa
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
