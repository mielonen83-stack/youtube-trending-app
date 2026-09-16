import streamlit as st
from googleapiclient.discovery import build

st.set_page_config(page_title="YouTube Uutiset & Live-kamerat", page_icon="🔴", layout="wide")

st.title("🔴 YouTube Uutiset & Maailman Live-kamerat (24/7)")
st.write("Selaa uutiskanavia tai hyppää suoraan suoriin lähetyksiin, sääkameroihin ja tapahtumiin ympäri maailmaa!")

# Valikko: Kanavat vai Live-lähetykset?
mode = st.sidebar.radio("Valitse tila:", ["📺 Uutiskanavat", "🔴 Maailman Live-lähetykset & Kamerat"])

# Laaja uutiskanavalista
CHANNELS = {
    "🇫🇮 MTV Uutiset": "MTV Uutiset",
    "🇫🇮 Yle Uutiset": "Yle Uutiset",
    "🇫🇮 Iltalehti": "Iltalehti",
    "🇫🇮 Ilta-Sanomat": "Ilta-Sanomat",
    "🌍 BBC News": "BBC News",
    "🌍 CNN": "CNN",
    "🌍 Reuters": "Reuters",
    "🌍 Sky News": "Sky News",
    "🌍 Al Jazeera English": "Al Jazeera English",
    "🇺🇸 Bloomberg": "Bloomberg News",
    "🇺🇸 CNBC": "CNBC",
    "💡 Johnny Harris": "Johnny Harris",
    "💡 Vox": "Vox"
}

# Valmiita pikavalintoja mahtaville 24/7-livehauille
LIVE_PRESETS = {
    "🌍 Maailman uutiset 24/7 (News Live)": "news live stream 24/7",
    "🚀 Avaruus & ISS (NASA / SpaceX)": "space live stream 24/7",
    "🌪️ Sää & Myrskyt (Weather Live)": "weather live tracking storm",
    "🌋 Tulivuoret & Luonto (Earth Live)": "earth webcam live 24/7",
    "🏙️ Kaupunkikamerat (Times Square ym.)": "city webcam live hd",
    "✈️ Lentokentät & Liikenne": "airport webcam live stream"
}

try:
    api_key = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.error("YouTube API-avainta ei ole asetettu Streamlitin salaisuuksiin (Secrets).")
else:
    youtube = build("youtube", "v3", developerKey=api_key)

    if mode == "📺 Uutiskanavat":
        selected_channel_name = st.sidebar.selectbox("Valitse uutislähde:", list(CHANNELS.keys()))
        search_query = CHANNELS[selected_channel_name]

        try:
            with st.spinner(f"Haetaan kanavaa '{search_query}'..."):
                search_response = youtube.search().list(
                    part="snippet",
                    q=search_query,
                    type="channel",
                    maxResults=1
                ).execute()

            search_items = search_response.get("items", [])
            if not search_items:
                st.warning("Kanavaa ei löytynyt.")
            else:
                channel_id = search_items[0]["id"]["channelId"]
                
                channel_response = youtube.channels().list(
                    part="snippet,statistics,contentDetails",
                    id=channel_id
                ).execute()
                
                ch_data = channel_response["items"][0]
                title = ch_data["snippet"]["title"]
                description = ch_data["snippet"]["description"]
                subs = int(ch_data["statistics"].get("subscriberCount", 0))
                avatar = ch_data["snippet"]["thumbnails"]["high"]["url"]
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(avatar, width=150)
                with col2:
                    st.header(title)
                    st.write(description[:300] + "..." if description else "Ei kuvausta.")
                    st.metric("Tilaajia", f"{subs:,}".replace(",", " "))
                
                st.divider()
                st.subheader("Tuoreimmat videot")

                uploads_playlist_id = ch_data["contentDetails"]["relatedPlaylists"]["uploads"]
                playlist_response = youtube.playlistItems().list(
                    part="snippet",
                    playlistId=uploads_playlist_id,
                    maxResults=12
                ).execute()
                
                video_items = playlist_response.get("items", [])
                if not video_items:
                    st.info("Videoita ei löytynyt.")
                else:
                    v_cols = st.columns(3)
                    for idx, v_item in enumerate(video_items):
                        v_title = v_item["snippet"]["title"]
                        v_id = v_item["snippet"]["resourceId"]["videoId"]
                        v_url = f"https://www.youtube.com/watch?v={v_id}"
                        
                        with v_cols[idx % 3]:
                            st.subheader(v_title)
                            st.video(v_url)
                            st.divider()

        except Exception as e:
            st.error(f"Virhe: {e}")

    elif mode == "🔴 Maailman Live-lähetykset & Kamerat":
        st.subheader("🔴 Aktiiviset 24/7-lähetykset ja kamerat ympäri maailmaa")
        
        # Valitaan pikavalinta tai kirjoitetaan itse
        selected_preset_name = st.sidebar.selectbox("Valitse live-kategoria:", list(LIVE_PRESETS.keys()))
        custom_live_query = st.sidebar.text_input("Tai kirjoita oma haku:", value=LIVE_PRESETS[selected_preset_name])

        search_query = custom_live_query if custom_live_query else LIVE_PRESETS[selected_preset_name]

        try:
            with st.spinner(f"Etsitään suoria lähetyksiä haulla '{search_query}'..."):
                # Haetaan videot, joissa eventType on 'live'
                live_response = youtube.search().list(
                    part="snippet",
                    q=search_query,
                    type="video",
                    eventType="live",
                    maxResults=12
                ).execute()

            live_items = live_response.get("items", [])

            if not live_items:
                st.info("Aktiivisia live-lähetyksiä tällä hakusanalla ei löytynyt tällä hetkellä. Kokeile toista hakua.")
            else:
                cols = st.columns(3)
                for idx, item in enumerate(live_items):
                    v_title = item["snippet"]["title"]
                    channel_title = item["snippet"]["channelTitle"]
                    v_id = item["id"]["videoId"]
                    v_url = f"https://www.youtube.com/watch?v={v_id}"

                    with cols[idx % 3]:
                        st.subheader(v_title)
                        st.write(f"📺 **Kanava:** {channel_title}")
                        st.markdown("🔴 **LIVE NYT (24/7)**")
                        st.video(v_url)
                        st.divider()

        except Exception as e:
            st.error(f"Virhe live-haussa: {e}")
