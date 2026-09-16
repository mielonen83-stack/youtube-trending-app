import streamlit as st
from googleapiclient.discovery import build

st.set_page_config(page_title="YouTube Uutis- ja Shorts-kanavat", page_icon="📺", layout="wide")

st.title("📺 Uutis- ja Shorts-kanavien ideapankki (Koti & Ulkomaat)")
st.write("Valitse alta haluamasi kanava, niin näet sen tilastot ja tuoreimmat videot suoraan ruudulla!")

# Laaja lista suomalaisia ja kansainvälisiä uutis- ja ajankohtaiskanavia
CHANNELS = {
    # 🇫🇮 Suomi
    "🇫🇮 MTV Uutiset": "MTV Uutiset",
    "🇫🇮 Yle Uutiset": "Yle Uutiset",
    "🇫🇮 Iltalehti": "Iltalehti",
    "🇫🇮 Ilta-Sanomat": "Ilta-Sanomat",
    "🇫🇮 Nelonen Uutiset": "Nelonen Uutiset",
    
    # 🌍 Kansainväliset uutiset
    "🌍 BBC News": "BBC News",
    "🌍 CNN": "CNN",
    "🌍 Reuters": "Reuters",
    "🌍 Sky News": "Sky News",
    "🌍 ABC News (USA)": "ABC News",
    "🌍 CBS News": "CBS News",
    "🌍 NBC News": "NBC News",
    "🌍 Fox News": "Fox News",
    "🌍 Al Jazeera English": "Al Jazeera English",
    "🌍 DW News (Saksa)": "DW News",
    "🌍 FRANCE 24 (Ranska)": "FRANCE 24",
    
    # 🚀 Shorts-henkiset / Selittävät uutiskanavat (Loistvia ideoille!)
    "💡 Insider News": "Insider News",
    "💡 Vox": "Vox",
    "💡 Vice News": "VICE News",
    "💡 The Wall Street Journal": "The Wall Street Journal",
    "💡 Bloomberg Technology": "Bloomberg Technology"
}

st.sidebar.header("Valitse kanava")
selected_channel_name = st.sidebar.selectbox("Kanavalista:", list(CHANNELS.keys()))
search_query = CHANNELS[selected_channel_name]

try:
    api_key = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.error("YouTube API-avainta ei ole asetettu Streamlitin salaisuuksiin (Secrets). Lisää YOUTUBE_API_KEY asetuksiin.")
else:
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        
        with st.spinner(f"Etsitään kanavaa '{search_query}'..."):
            # Etsitään kanavaa nimellä, jotta ID pysyy aina oikeana
            search_request = youtube.search().list(
                part="snippet",
                q=search_query,
                type="channel",
                maxResults=1
            )
            search_response = search_request.execute()

        search_items = search_response.get("items", [])
        
        if not search_items:
            st.warning(f"Kanavaa '{search_query}' ei löytynyt.")
        else:
            channel_id = search_items["id"]["channelId"]
            
            # Haetaan kanavan tarkat tiedot
            channel_request = youtube.channels().list(
                part="snippet,statistics,contentDetails",
                id=channel_id
            )
            channel_response = channel_request.execute()
            
            ch_data = channel_response["items"]
            title = ch_data["snippet"]["title"]
            description = ch_data["snippet"]["description"]
            subs = int(ch_data["statistics"].get("subscriberCount", 0))
            views = int(ch_data["statistics"].get("viewCount", 0))
            avatar = ch_data["snippet"]["thumbnails"]["high"]["url"]
            
            # Näytetään kanavan tiedot siististi
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(avatar, width=150)
            with col2:
                st.header(title)
                st.write(description[:300] + "..." if description else "Ei kuvausta.")
                st.metric("Tilaajia", f"{subs:,}".replace(",", " "))
                st.metric("Katselukertoja yhteensä", f"{views:,}".replace(",", " "))
            
            st.divider()
            st.subheader(f"Kanavan tuoreimmat videot: {title}")

            # Haetaan uusin sisältö uploads-soittolistasta
            uploads_playlist_id = ch_data["contentDetails"]["relatedPlaylists"]["uploads"]
            
            playlist_request = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=12
            )
            playlist_response = playlist_request.execute()
            
            video_items = playlist_response.get("items", [])
            
            if not video_items:
                st.info("Videoita ei löytynyt tältä kanavalta.")
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
        st.error(f"Virhe haussa: {e}")
