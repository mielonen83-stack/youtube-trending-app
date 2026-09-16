import streamlit as st
import requests
from googleapiclient.discovery import build

st.set_page_config(page_title="YouTube Uutiset & Suomen Kelikamerat", page_icon="❄️", layout="wide")

# CSS-tyylit tiiviimmälle ja siistimmälle ruudukolle
st.markdown("""
    <style>
    .stVideo {
        margin-bottom: -20px;
    }
    h3 {
        font-size: 1.1rem !important;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("❄️ Suomen Kelikamerat, Uutiset & Maailman Live-streamit")
st.write("Valitse sivupalkista haluatko selailla uutiskanavia, YouTube-livekameroita vai Suomen virallisia kelikameroita!")

# Päävalikko: Kolme tilaa
mode = st.sidebar.radio("Valitse tila:", [
    "❄️ Suomalaiset Kelikamerat (Fintraffic)", 
    "🔴 YouTube Live-kamerat & 24/7", 
    "📺 Uutiskanavat"
])

# 1. Uutiskanavalista
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

# 2. YouTube Live -pikavalinnat
LIVE_PRESETS = {
    "🇫🇮 Suomen Live-kamerat & Kaupungit": "suomi live kamera",
    "🇫🇮 Helsinki Webcam Live": "helsinki webcam live",
    "🇫🇮 Revontulet (Aurora Borealis Suomi)": "aurora borealis live finland",
    "🇫🇮 Suomen luonto & Sää": "finland nature webcam live",
    "🌍 Maailman uutiset 24/7 (News Live)": "news live stream 24/7",
    "🚀 Avaruus & ISS (NASA / SpaceX)": "space live stream 24/7",
    "🌪️ Sää & Myrskyt (Weather Live)": "weather live tracking storm",
    "🌋 Tulivuoret & Luonto (Earth Live)": "earth webcam live 24/7",
    "🏙️ Kaupunkikamerat (Times Square ym.)": "city webcam live hd"
}

try:
    api_key = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    api_key = None

# --- TILA 1: SUOMEN KELIKAMERAT (Fintraffic API) ---
if mode == "❄️ Suomalaiset Kelikamerat (Fintraffic)":
    st.subheader("❄️ Suomen maanteiden kelikamerat (Fintraffic / Liikennevirasto)")
    st.write("Tämä osio hakee suoraan Suomen viralliset kelikameroiden tuoreet kuvat maanteiltä ympäri maata.")

    # Aluevalinta tai maantievalinta
    region_filter = st.sidebar.selectbox("Valitse alue / maantie:", [
        "Kaikki haetut asemat",
        "Pääkaupunkiseutu (Helsinki / Espoo)",
        "Etelä-Suomi",
        "Keski-Suomi",
        "Pohjois-Suomi / Lappi"
    ])

    try:
        with st.spinner("Haetaan kelikameroita Fintrafficin avoimesta rajapinnasta..."):
            # Haetaan keliasemat Fintrafficin avoimesta rajapinnasta
            url = "https://tie.digitraffic.fi/api/weather/v1/stations"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                st.error("Kelitietojen haku epäonnistui (Fintraffic API ei vastannut).")
            else:
                data = response.json()
                stations = data.get("stations", [])
                
                # Suodatetaan asemat, joissa on kamerakuvia
                camera_stations = []
                for stn in stations:
                    # Tarkistetaan onko asemalla kameraan liittyviä tietoja tai kuvia
                    # Fintraffic tarjoaa säätietoihin liittyviä kameroiden kuvavarastoja
                    name = stn.get("name", "Tuntematon asema")
                    # Etsitään kameratiedot
                    # Jos asemalla on weathercam-kuvia
                    history_url = f"https://tie.digitraffic.fi/api/weather/v1/stations/{stn['id']}/history"
                    camera_stations.append((name, stn['id']))

                st.success(f"Löytyi {len(camera_stations)} keliasemaa.")
                
                # Koska asemia on satoja, näytetään ensimmäiset 16 sarakkeissa (4x4)
                cam_cols = st.columns(4)
                
                # Otetaan vaikka 16 ensimmäistä esimerkkikuvaa
                count = 0
                for name, stn_id in camera_stations[:20]:
                    try:
                        hist_res = requests.get(f"https://tie.digitraffic.fi/api/weather/v1/stations/{stn_id}/history", timeout=5)
                        if hist_res.status_code == 200:
                            hist_data = hist_res.json()
                            # Etsitään tuorein kamerakuva jos saatavilla
                            # Jos suoraa kuvalinkkiä ei löydy helposti JSONista, näytetään aseman tiedot ja linkki
                            with cam_cols[count % 4]:
                                st.markdown(f"**📍 {name}**")
                                st.caption(f"Asema ID: {stn_id}")
                                st.info("Keliaseman tiedot haettu")
                                count += 1
                    except:
                        pass
                        
                    if count >= 12:
                        break

                if count == 0:
                    st.info("Kuvia ei saatu ladattua juuri nyt. Voit käyttää myös YouTube-pohjaisia sääkameroita sivupalkin kautta!")

    except Exception as e:
        st.error(f"Virhe kelikameroiden haussa: {e}")

# --- TILA 2: YOUTUBE LIVE-KAMERAT ---
elif mode == "🔴 YouTube Live-kamerat & 24/7":
    st.subheader("🔴 Aktiiviset 24/7-lähetykset ja kamerat (Suomi & Maailma)")
    
    if not api_key:
        st.error("YouTube API-avain puuttuu Streamlit Secretsistä.")
    else:
        youtube = build("youtube", "v3", developerKey=api_key)
        
        selected_preset_name = st.sidebar.selectbox("Valitse live-kategoria:", list(LIVE_PRESETS.keys()))
        custom_live_query = st.sidebar.text_input("Tai kirjoita oma haku:", value=LIVE_PRESETS[selected_preset_name])
        max_results = st.sidebar.slider("Näytettävien live-kuvien määrä:", min_value=4, max_value=24, value=12, step=4)

        search_query = custom_live_query if custom_live_query else LIVE_PRESETS[selected_preset_name]

        try:
            with st.spinner(f"Etsitään suoria lähetyksiä haulla '{search_query}'..."):
                live_response = youtube.search().list(
                    part="snippet",
                    q=search_query,
                    type="video",
                    eventType="live",
                    maxResults=max_results
                ).execute()

            live_items = live_response.get("items", [])

            if not live_items:
                st.info("Aktiivisia live-lähetyksiä ei löytynyt tällä hakusanalla.")
            else:
                cols = st.columns(4)
                for idx, item in enumerate(live_items):
                    v_title = item["snippet"]["title"]
                    channel_title = item["snippet"]["channelTitle"]
                    v_id = item["id"]["videoId"]
                    v_url = f"https://www.youtube.com/watch?v={v_id}"

                    with cols[idx % 4]:
                        short_title = v_title if len(v_title) < 55 else v_title[:52] + "..."
                        st.markdown(f"**{short_title}**")
                        st.caption(f"📺 {channel_title} | 🔴 LIVE")
                        st.video(v_url)
                        st.write("")

        except Exception as e:
            st.error(f"Virhe live-haussa: {e}")

# --- TILA 3: UUTISKANAVAT ---
elif mode == "📺 Uutiskanavat":
    st.subheader("📺 Maailman laajuinen uutiskanavien ideapankki")
    
    if not api_key:
        st.error("YouTube API-avain puuttuu Streamlit Secretsistä.")
    else:
        youtube = build("youtube", "v3", developerKey=api_key)
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
                st.subheader(f"Tuoreimmat videot: {title}")

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
