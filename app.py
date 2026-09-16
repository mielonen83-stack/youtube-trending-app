import streamlit as st
from googleapiclient.discovery import build

st.set_page_config(page_title="YouTube-kanavien vakoilija", page_icon="📺", layout="wide")

st.title("📺 Suositut uutis- ja Shorts-kanavat (Koti & Ulkomaat)")
st.write("Valitse alta kanavaryhmä, niin näet kanavien tilastoja ja tuoreimpia videoita ideoinnin avuksi!")

# Esimerkkikanavien YouTube Channel ID:t
# (Voit lisätä tai vaihtaa näitä halutessasi!)
CHANNELS = {
    "🇫🇮 MTV Uutiset": "UC1-82B-7b952Z505d9l653A", # Esimerkki ID, korjataan tarvittaessa tai haetaan haulla
    "🇫🇮 Yle Uutiset": "UCl2cK_N1oZ20mCkkzJv6mDQ",
    "🌍 BBC News": "UC16niRr50-MSBwiO3YDb3RA",
    "🌍 CNN": "UCupvZG-5ko_eiXAupbDfxWw",
    "🌍 Insider": "UCZXgSjDfc2GLjDvF3cSOSSQ" # Tunnettu Shorts- ja erikoisjutuistaan
}

# Vaihtoehtoisesti annetaan käyttäjän valita kanava
selected_channel_name = st.sidebar.selectbox("Valitse kanava:", list(CHANNELS.keys()))
channel_id = CHANNELS[selected_channel_name]

try:
    api_key = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.error("YouTube API-avainta ei ole asetettu Streamlitin salaisuuksiin (Secrets). Lisää YOUTUBE_API_KEY asetuksiin.")
else:
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        
        with st.spinner(f"Haetaan tietoja kanavasta {selected_channel_name}..."):
            # Haetaan kanavan tiedot (tilastot, kuvaus jne.)
            channel_request = youtube.channels().list(
                part="snippet,statistics,contentDetails",
                id=channel_id
            )
            channel_response = channel_request.execute()

        if not channel_response.get("items"):
            st.warning("Kanavaa ei löytynyt tällä ID:llä. (Huom: Joillakin kanavilla ID voi muuttua, tarkistetaan tarvittaessa!)")
        else:
            ch_data = channel_response["items"][0]
            title = ch_data["snippet"]["title"]
            description = ch_data["snippet"]["description"]
            subs = int(ch_data["statistics"].get("subscriberCount", 0))
            views = int(ch_data["statistics"].get("viewCount", 0))
            avatar = ch_data["snippet"]["thumbnails"]["high"]["url"]
            
            # Näytetään kanavan tiedot
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(avatar, width=150)
            with col2:
                st.header(title)
                st.write(description[:300] + "...")
                st.metric("Tilaajia", f"{subs:,}".replace(",", " "))
                st.metric("Katselukertoja yhteensä", f"{views:,}".replace(",", " "))
            
            st.divider()
            st.subheader(f"Kanavan tuoreimmat videot: {title}")

            # Haetaan kyseisen kanavan viimeisimmät videot uploads-soittolistasta
            uploads_playlist_id = ch_data["contentDetails"]["relatedPlaylists"]["uploads"]
            
            playlist_request = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=12
            )
            playlist_response = playlist_request.execute()
            
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
                        st.write(f"**{v_title}**")
                        st.video(v_url)
                        st.divider()

    except Exception as e:
        st.error(f"Virhe haussa: {e}")
