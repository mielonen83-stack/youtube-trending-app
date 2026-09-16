import streamlit as st
import feedparser
from bs4 import BeautifulSoup

st.set_page_config(page_title="Shorts-ideat Uutisista", page_icon="📰", layout="wide")

st.title("📰 Shorts-ideat koti- ja ulkomailta")
st.write("Valitse lähde sivupalkista. Poimi uutisista aiheet, joista teet napakoita YouTube Shorts / TikTok -videoita!")

# Laajempi lista: sekä suomalaisia että ulkomaisia uutislähteitä
FEEDS = {
    "🇫🇮 MTV Uutiset": "https://www.mtv.fi/api/feed/rss/uutiset",
    "🇫🇮 Yle Uutiset": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=yle_uutiset",
    "🌍 BBC News (World)": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "🌍 CNN Top Stories": "http://rss.cnn.com/rss/edition.rss",
    "🌍 Reuters (Top News)": "https://www.reutersagency.com/feed/?best-topics=top-news&post_type=best"
}

st.sidebar.header("Uutislähteet")
selected_source = st.sidebar.selectbox("Valitse lähde:", list(FEEDS.keys()))

try:
    with st.spinner(f"Haetaan uutisia lähteestä {selected_source}..."):
        feed_url = FEEDS[selected_source]
        feed = feedparser.parse(feed_url)
        entries = feed.entries[:20]  # Otetaan 20 tuoreinta

    if not entries:
        st.info("Uutisia ei löytynyt tällä hetkellä.")
    else:
        st.header(f"Tuoreimmat uutiset: {selected_source}")
        st.write("Vinkki: Kansainvälisistä uutisista löydät usein erikoisia tai shokeeraavia aiheita, jotka toimivat loistavasti lyhytvideoissa!")
        
        for index, entry in enumerate(entries):
            title = entry.get("title", "Ei otsikkoa")
            link = entry.get("link", "#")
            published = entry.get("published", "")
            summary = entry.get("summary", "Ei tiivistelmää saatavilla.")
            
            # Siistitään HTML-tagit tiivistelmästä
            soup = BeautifulSoup(summary, "html.parser")
            clean_summary = soup.get_text()

            with st.container():
                st.subheader(title)
                if published:
                    st.caption(f"📅 Julkaistu: {published}")
                st.write(clean_summary if clean_summary else "Ei kuvausta saatavilla.")
                st.markdown(f"[Lue alkuperäinen artikkeli]({link})")
                
                # Ideointinappi
                if st.button(f"💡 Generoi Shorts-käsikirjoitus", key=f"btn_{index}_{link}"):
                    st.success(f"Idean runko:\n1. Koukku: 'Et ikinä arvaa mitä tapahtui...' tai 'Tästä puhutaan nyt maailmalla!'\n2. Aihe: {title}\n3. Loppuun kysymys katsojille.")
                
                st.divider()

except Exception as e:
    st.error(f"Virhe uutisten haussa: {e}")
