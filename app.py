import streamlit as st
import feedparser
from googleapiclient.discovery import build

# Sivuston asetukset
st.set_page_config(
    page_title="Global News & Live Command Center", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AMMATTIMAINEN CSS-MUOTOILU ---
st.markdown("""
    <style>
    /* Yleiset tyylit ja siistimmät otsikot */
    .stVideo {
        margin-bottom: -15px;
        border-radius: 8px;
    }
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    /* Breaking news / yläbanneri */
    .breaking-banner {
        background: linear-gradient(90deg, #b91c1c 0%, #dc2626 100%);
        color: white;
        padding: 10px 15px;
        border-radius: 6px;
        font-weight: bold;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    /* Korttityylit */
    .news-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- YLÄBANNERI / BREAKING NEWS ---
st.markdown("""
    <div class="breaking-banner">
        <span>🔴 GLOBAL COMMAND CENTER & NEWS WIRE</span>
        <span>Reaaliaikainen uutis- ja valvontaverkko</span>
    </div>
""", unsafe_allow_html=True)

st.title("🌐 Maailmanluokan Uutis- ja Live-keskus")
st.write("Kattava ja keskitetty näkymä maailman medioihin, reaaliaikaisiin 24/7-lähetyksiin, avaruuskameroihin ja Suomen tieverkkoon.")

# --- SIVUPALKIN NAVIGOINTI ---
st.sidebar.markdown("### 🎛️ Navigaatio")
mode = st.sidebar.radio("Valitse osasto:", [
    "📰 Globaalit & Kotimaiset Uutiset (RSS + AI / YouTube)", 
    "📺 Kansainväliset Uutiskanavat (Live)", 
    "🔴 Maailman Live-kamerat & 24/7", 
    "❄️ Suomen Kelikamerat & Liikenne"
])

# API-avaimen haku turvallisesti
try:
    api_key = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    api_key = None

youtube = build("youtube", "v3", developerKey=api_key) if api_key else None

# Tarkistetaan onko OpenAI-avainta määritetty (valinnainen lisäteho)
try:
    openai_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    openai_key = None


# ==========================================
# 1. GLOBAALIT & KOTIMAISET UUTISET (RSS + YouTube)
# ==========================================
if mode == "📰 Globaalit & Kotimaiset Uutiset (RSS + AI / YouTube)":
    st.subheader("📰 Pääuutiset ja toimitusverkko")
    st.write("Uutiset haetaan reaaliajassa johtavista kotimaisista ja kansainvälisistä RSS-lähteistä.")

    # RSS-lähteet
    FEEDS = {
        "🇫🇮 Yle Uutiset (Kotimaa)": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=yle_uutiset",
        "🇫🇮 Ilta-Sanomat": "https://www.is.mobi/rss/tuoreimmat.xml",
        "🌍 BBC News (World)": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "🌍 CNN Top Stories": "http://rss.cnn.com/rss/edition.rss",
        "🌍 Reuters (Top News)": "https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best",
        "🌍 Al Jazeera English": "https://www.aljazeera.com/xml/rss/all.rss"
    }

    selected_feed_name = st.sidebar.selectbox("Valitse uutislähde:", list(FEEDS.keys()))
    feed_url = FEEDS[selected_feed_name]

    try:
        with st.spinner(f"Haetaan uutisia lähteestä {selected_feed_name}..."):
            parsed_feed = feedparser.parse(feed_url)
            entries = parsed_feed.entries[:10] # Top 10 uutista

        if not entries:
            st.warning("Uutisia ei löytynyt tällä hetkellä tästä lähteestä.")
        else:
            for entry in entries:
                title = getattr(entry, "title", "Ei otsikkoa")
                summary = getattr(entry, "summary", getattr(entry, "description", "Ei kuvausta"))
                link = getattr(entry, "link", "#")
                published = getattr(entry, "published", "")

                with st.container():
                    st.markdown(f"### [{title}]({link})")
                    if published:
                        st.caption(julkaistu := f"📅 Julkaistu: {published}")
                    
                    # Siivotaan HTML-tagit summariesta lyhyesti
                    import re
                    clean_summary = re.sub('<.*?>', '', summary)
                    st.write(clean_summary[:350] + ("..." if len(clean_summary) > 350 else ""))

                    # Yritetään etsiä aiheeseen liittyvä YouTube-video, jos YouTube API on käytössä
                    if youtube:
                        try:
                            search_res = youtube.search().list(
                                part="snippet",
                                q=title[:50], # Haetaan otsikon perusteella
                                type="video",
                                maxResults=1
                            ).execute()
                            items = search_res.get("items", [])
                            if items:
                                v_id = items[0]["id"]["videoId"]
                                v_title = items[0]["snippet"]["title"]
                                with st.expander(f"📺 Katso aiheeseen liittyvä video: {v_title[:60]}..."):
                                    st.video(f"https://www.youtube.com/watch?v={v_id}")
                        except:
                            pass

                    st.markdown("---")

    except Exception as e:
        st.error(f"Virhe uutisten latauksessa: {e}")


# ==========================================
# 2. KANSAINVÄLISET UUTISKANAVAT (LIVE / ARKISTO)
# ==========================================
elif mode == "📺 Kansainväliset Uutiskanavat (Live)":
    st.subheader("📺 Kansainväliset ja kotimaiset uutismediat")
    
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

    if not api_key:
        st.error("YouTube API-avain puuttuu Streamlit Secretsistä.")
    else:
        selected_channel_name = st.sidebar.selectbox("Valitse uutistoimitus:", list(CHANNELS.keys()))
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
                    st.image(avatar, width=140)
                with col2:
                    st.header(title)
                    st.write(description[:300] + "..." if description else "Ei kuvausta.")
                    st.metric("Tilaajia", f"{subs:,}".replace(",", " "))
                
                st.divider()
                st.subheader("Tuoreimmat lähetykset ja videot")

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
                            st.markdown(f"**{v_title}**")
                            st.video(v_url)
                            st.divider()

        except Exception as e:
            st.error(f"Virhe: {e}")


# ==========================================
# 3. MAAILMAN LIVE-KAMERAT & 24/7
# ==========================================
elif mode == "🔴 Maailman Live-kamerat & 24/7":
    st.subheader("🔴 Aktiiviset 24/7-lähetykset ja kamerat (Suomi & Maailma)")
    
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

    if not api_key:
        st.error("YouTube API-avain puuttuu Streamlit Secretsistä.")
    else:
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
                st.info("Aktiivisia live-lähetyksiä ei löytynyt tällä hakusanalla tällä hetkellä.")
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


# ==========================================
# 4. SUOMEN KELIKAMERAT & LIIKENNE
# ==========================================
elif mode == "❄️ Suomalaiset Kelikamerat & Liikenne":
    st.subheader("❄️ Suomen tie- ja kelikamerat sekä liikennevalvonta (Live)")
    st.write("Suorat live-syötteet ja kamerat Suomen teiltä, kaupungeista ja säätilasta.")

    road_query = st.sidebar.selectbox("Valitse kelialue:", [
        "Suomen maantiet ja kelikamerat",
        "Helsinki liikenne ja kamerat",
        "Tampere ja Turku kelikamerat",
        "Pohjois-Suomi ja Lappi kelikamerat",
        "Suomen säätila ja taivas"
    ])
    
    max_results = st.sidebar.slider("Näytettävien kameroiden määrä:", min_value=4, max_value=24, value=12, step=4)

    if not api_key:
        st.error("YouTube API-avain puuttuu Streamlit Secretsistä.")
    else:
        try:
            with st.spinner(f"Haetaan kelikameroita haulla '{road_query}'..."):
                response = youtube.search().list(
                    part="snippet",
                    q=road_query,
                    type="video",
                    eventType="live",
                    maxResults=max_results
                ).execute()

            items = response.get("items", [])
            if not items:
                st.info("Aktiivisia kelikameroita ei löytynyt tällä haulla tällä hetkellä.")
            else:
                cols = st.columns(4)
                for idx, item in enumerate(items):
                    v_title = item["snippet"]["title"]
                    channel_title = item["snippet"]["channelTitle"]
                    v_id = item["id"]["videoId"]
                    v_url = f"https://www.youtube.com/watch?v={v_id}"

                    with cols[idx % 4]:
                        short_title = v_title if len(v_title) < 55 else v_title[:52] + "..."
                        st.markdown(f"**{short_title}**")
                        st.caption(f"📺 {channel_title} | ❄️ KELI LIVE")
                        st.video(v_url)
                        st.write("")

        except Exception as e:
            st.error(f"Virhe kelikameroiden haussa: {e}")
