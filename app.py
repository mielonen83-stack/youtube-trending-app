import streamlit as st
import feedparser
import requests
import re
from googleapiclient.discovery import build

# Sivuston asetukset
st.set_page_config(
    page_title="Global News & Live Command Center", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"

    # Nopea testauskoodi avaimille
with st.sidebar.expander("🔑 API-avaimien tila"):
    if openai_key:
        try:
            from openai import OpenAI
            test_client = OpenAI(api_key=openai_key)
            # Tehdään kevyt testikutso
            test_client.models.list()
            st.success("OpenAI-avain toimii! ✅")
        except Exception as e:
            st.error(f"OpenAI-virhe: {e}")
    else:
      st.warning("OPENAI_API_KEY puuttuu secretsistä.")

    if api_key:
        st.success("YouTube-avain löytyy! ✅")
    else:
        st.warning("YouTube API-avain puuttuu.")
)

# --- AMMATTIMAINEN CSS-MUOTOILU ---
st.markdown("""
    <style>
    .stVideo {
        margin-bottom: -15px;
        border-radius: 8px;
    }
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
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
    </style>
""", unsafe_allow_html=True)

# --- YLÄBANNERI ---
st.markdown("""
    <div class="breaking-banner">
        <span>🔴 GLOBAL COMMAND CENTER & MASSIVE NEWS WIRE</span>
        <span>Reaaliaikainen globaali uutis- ja valvontaverkko</span>
    </div>
""", unsafe_allow_html=True)

st.title("🌐 Maailmanluokan Uutis- ja Live-keskus")
st.write("Kattava, massiivinen uutisarkisto, joka kerää uutiset kymmenistä maailman johtavista medioista ja jalostaa ne tekoälyllä suomeksi.")

# --- SIVUPALKIN NAVIGOINTI ---
st.sidebar.markdown("### 🎛️ Navigaatio")
mode = st.sidebar.radio("Valitse osasto:", [
    "📰 Globaalit & Kotimaiset Pääuutiset (Massiivi-RSS + AI)", 
    "📺 Kansainväliset Uutiskanavat (Live)", 
    "🔴 Maailman Live-kamerat & 24/7", 
    "❄️ Suomen Kelikamerat & Liikenne"
])

# API-avaimet
try:
    api_key = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    api_key = None

try:
    openai_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    openai_key = None

youtube = build("youtube", "v3", developerKey=api_key) if api_key else None


# ==========================================
# 1. GLOBAALIT & KOTIMAISET UUTISET (MASSIIVINEN LÄHDELISTÄ + AI)
# ==========================================
if mode == "📰 Globaalit & Kotimaiset Pääuutiset (Massiivi-RSS + AI)":
    st.subheader("📰 Globaali Toimitusverkko ja AI-päätoimittaja")
    st.write("Valitse alta haluamasi mediakategoria tai yksittäinen lähde. Tekoäly kääntää ja tiivistää uutiset suomeksi.")

    # MASSIIVINEN UUTISLÄHDELISTÄ KOKO MAAILMASTA
    FEEDS = {
        # --- SUOMI ---
        "🇫🇮 Yle Uutiset (Pääuutiset)": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=yle_uutiset",
        "🇫🇮 Yle Uutiset (Ulkomaat)": "https://feeds.yle.fi/uutiset/v1/majorHeadlines.rss?publisherIds=yle_uutiset&category=18-348",
        "🇫🇮 Ilta-Sanomat (Tuoreimmat)": "https://www.is.mobi/rss/tuoreimmat.xml",
        "🇫🇮 Iltalehti (Uutiset)": "https://www.iltalehti.fi/rss/uutiset.xml",
        "🇫🇮 Kauppalehti (Talous)": "https://www.kauppalehti.fi/rss/uutiset",
        "🇫🇮 Talouselämä": "https://www.talouselama.fi/rss/uutiset",

        # --- MAAILMAN UUTISTOIMISTOT & KANSAINVÄLISET ---
        "🌍 BBC News (World)": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "🌍 CNN Top Stories": "http://rss.cnn.com/rss/edition.rss",
        "🌍 Reuters (Top News)": "https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best",
        "🌍 Al Jazeera English": "https://www.aljazeera.com/xml/rss/all.rss",
        "🌍 Euronews": "https://www.euronews.com/rss?format=mrss",
        "🌍 The Guardian (World)": "https://www.theguardian.com/world/rss",
        "🌍 France 24": "https://www.france24.com/en/rss",
        "🌍 Deutsche Welle (DW Top Stories)": "https://rss.dw.com/rdf/rss-en-all",
        "🌍 Associated Press (AP News)": "https://rsshub.app/apnews/topics/ap-top-news",

        # --- TALOUS & MARKKINAT ---
        "💰 Bloomberg (Markets)": "https://feeds.bloomberg.com/markets/news.rss",
        "💰 CNBC (Top News)": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",

        # --- TEKNOLOGIA & AI ---
        "💻 TechCrunch": "https://techcrunch.com/feed/",
        "💻 The Verge": "https://www.theverge.com/rss/index.xml",
        "💻 Wired": "https://www.wired.com/feed/rss",
        "💻 MIT Technology Review": "https://www.technologyreview.com/feed/",

        # --- TIEDE & AVARUUS ---
        "🚀 NASA Breaking News": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "🔬 ScienceDaily": "https://www.sciencedaily.com/rss/top.xml"
    }

    selected_feed_name = st.sidebar.selectbox("Valitse uutislähde:", list(FEEDS.keys()))
    feed_url = FEEDS[selected_feed_name]
    
    # Oletuksena päällä jos OpenAI-avain löytyy
    use_ai = st.sidebar.checkbox("Käytä OpenAI-päätoimittajaa (kääntää ja tiivistää suomeksi)", value=True if openai_key else False)
    max_news_count = st.sidebar.slider("Näytettävien uutisten määrä:", min_value=5, max_value=20, value=10)

    try:
        with st.spinner(f"Ladataan tuoreimpia uutisia lähteestä: {selected_feed_name}..."):
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(feed_url, headers=headers, timeout=10)
            
            parsed_feed = feedparser.parse(response.content)
            entries = parsed_feed.entries[:max_news_count]

        if not entries:
            st.warning(f"Uutisia ei löytynyt lähteestä '{selected_feed_name}'. Kokeile toista lähdettä.")
        else:
            st.success(f"Löytyi {len(entries)} uutisartikkelia lähteestä {selected_feed_name}.")
            
            for entry in entries:
                title = getattr(entry, "title", "Ei otsikkoa")
                summary = getattr(entry, "summary", getattr(entry, "description", "Ei kuvausta"))
                link = getattr(entry, "link", "#")
                published = getattr(entry, "published", "")

                clean_summary = re.sub('<.*?>', '', summary)

                with st.container():
                    st.markdown(f"### [{title}]({link})")
                    if published:
                        st.caption(f"📅 Julkaistu: {published}")

                    # JOS OpenAI on käytössä, käännetään ja tiivistetään uutinen ammattimaisesti suomeksi
                    if use_ai and openai_key:
                        try:
                            from openai import OpenAI
                            client = OpenAI(api_key=openai_key)
                            
                            prompt = (
                                "Olet maailmanluokan uutistoimituksen päätoimittaja. "
                                "Lue seuraava uutisartikkeli (joka saattaa olla englanniksi tai suomeksi), "
                                "käännä se tarvittaessa ja tiivistä se ammattimaisesti, selkeäksi ja "
                                "objektiiviseksi suomenkieliseksi uutisnostoksi (enintään 2-3 lausetta):\n\n"
                                f"Alkuperäinen otsikko: {title}\n"
                                f"Alkuperäinen sisältö: {clean_summary}"
                            )
                            
                            ai_response = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=180
                            )
                            ai_text = ai_response.choices[0].message.content
                            st.info(f"🤖 **Toimituksen tiivistelmä (Suomi):**\n\n{ai_text}")
                        except Exception:
                            st.write(clean_summary[:350] + ("..." if len(clean_summary) > 350 else ""))
                    else:
                        st.write(clean_summary[:350] + ("..." if len(clean_summary) > 350 else ""))

                    # YouTube-videon täsmäytys uutiselle
                    if youtube:
                        try:
                            search_res = youtube.search().list(
                                part="snippet",
                                q=title[:50],
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
# 2. KANSAINVÄLISET UUTISKANAVAT (LIVE)
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
