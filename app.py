import streamlit as st
from googleapiclient.discovery import build

st.set_page_config(page_title="Maailman Uutiskanavat & Shorts-ideat", page_icon="📺", layout="wide")

st.title("📺 Maailman laajuinen uutiskanavien ideapankki")
st.write("Valitse alta haluamasi uutismedia (Suomi, Eurooppa, USA tai maailma), niin näet sen tuoreimmat videot ja tilastot!")

# Jättilista uutissivustoista ja -kanavista koti- ja ulkomailta
CHANNELS = {
    # 🇫🇮 Suomi - Yleiset ja sanomalehdet
    "🇫🇮 MTV Uutiset": "MTV Uutiset",
    "🇫🇮 Yle Uutiset": "Yle Uutiset",
    "🇫🇮 Yle Kioski": "Yle Kioski",
    "🇫🇮 Iltalehti": "Iltalehti",
    "🇫🇮 Ilta-Sanomat": "Ilta-Sanomat",
    "🇫🇮 Helsingin Sanomat": "Helsingin Sanomat",
    "🇫🇮 Aamulehti": "Aamulehti",
    "🇫🇮 Turun Sanomat": "Turun Sanomat",
    "🇫🇮 Kaleva": "Kaleva",
    "🇫🇮 Nelonen Uutiset": "Nelonen Uutiset",

    # 🇸🇪 Pohjoismaat & Eurooppa
    "🇸🇪 SVT Nyheter (Ruotsi)": "SVT Nyheter",
    "🇳🇴 NRK Nyheter (Norja)": "NRK Nyheter",
    "🇩🇰 DR Nyheder (Tanska)": "DR Nyheder",
    "🌍 BBC News": "BBC News",
    "🌍 Sky News": "Sky News",
    "🌍 Euronews": "Euronews",
    "🌍 DW News (Saksa)": "DW News",
    "🌍 FRANCE 24 (Ranska)": "FRANCE 24",
    "🌍 The Guardian": "The Guardian",
    "🌍 Le Monde (Ranska)": "Le Monde",

    # 🇺🇸 USA & Maailman jättiläiset
    "🇺🇸 CNN": "CNN",
    "🇺🇸 Fox News": "Fox News",
    "🇺🇸 MSNBC": "MSNBC",
    "🇺🇸 ABC News": "ABC News",
    "🇺🇸 CBS News": "CBS News",
    "🇺🇸 NBC News": "NBC News",
    "🇺🇸 Reuters": "Reuters",
    "🇺🇸 Associated Press (AP)": "Associated Press",
    "🇺🇸 Bloomberg": "Bloomberg News",
    "🇺🇸 CNBC": "CNBC",
    "🇺🇸 The Wall Street Journal": "The Wall Street Journal",
    "🇺🇸 The New York Times": "The New York Times",
    "🇺🇸 Washington Post": "Washington Post",

    # 🌍 Muut maanosat ja kansainväliset
    "🌍 Al Jazeera English": "Al Jazeera English",
    "🌍 WION (Aasia)": "WION",
    "🌍 ABC News (Australia)": "ABC News In-depth",
    "🌍 CBC News (Kanada)": "CBC News",
    "🌍 Channel NewsAsia (Singapore)": "CNA",

    # 🚀 Visuaaliset uutiset ja taustoittavat (Parhaat Shorts-ideat!)
    "💡 Johnny Harris": "Johnny Harris",
    "💡 Vox": "Vox",
    "💡 Vice News": "VICE News",
    "💡 Wendover Productions": "Wendover Productions",
    "💡 RealLifeLore": "RealLifeLore",
    "💡 The Infographics Show": "The Infographics Show",
    "💡 Caspian Report": "Caspian Report"
}

st.sidebar.header("Valitse uutislähde")
selected_channel_name = st.sidebar.selectbox("Uutiskanavat:", list(CHANNELS.keys()))
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
        
        with st.spinner(f"Haetaan uutisia kanavalta '{search_query}'..."):
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
            channel_id = search_items[0]["id"]["channelId"]
            
            channel_request = youtube.channels().list(
                part="snippet,statistics,contentDetails",
                id=channel_id
            )
            channel_response = channel_request.execute()
            
            ch_data = channel_response["items"][0]
            title = ch_data["snippet"]["title"]
            description = ch_data["snippet"]["description"]
            subs = int(ch_data["statistics"].get("subscriberCount", 0))
            views = int(ch_data["statistics"].get("viewCount", 0))
            avatar = ch_data["snippet"]["thumbnails"]["high"]["url"]
            
            # Näytetään tiedot
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(avatar, width=150)
            with col2:
                st.header(title)
                st.write(description[:300] + "..." if description else "Ei kuvausta.")
                st.metric("Tilaajia", f"{subs:,}".replace(",", " "))
                st.metric("Katselukertoja yhteensä", f"{views:,}".replace(",", " "))
            
            st.divider()
            st.subheader(f"Tuoreimmat videot: {title}")

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
