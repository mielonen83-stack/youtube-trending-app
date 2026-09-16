# ==========================================
# 1. GLOBAALIT & KOTIMAISET UUTISET (RSS + OpenAI AI + YouTube)
# ==========================================
elif mode == "📰 Globaalit & Kotimaiset Uutiset (RSS + AI / YouTube)":
    st.subheader("📰 Pääuutiset ja AI-toimitusverkko")
    st.write("Uutiset haetaan maailmalta ja tekoäly tiivistää tärkeimmät uutisnostot luettavaan muotoon.")

    # Luotettavat RSS-lähteet
    FEEDS = {
        "🇫🇮 Yle Uutiset (Kotimaa)": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=yle_uutiset",
        "🇫🇮 Ilta-Sanomat": "https://www.is.mobi/rss/tuoreimmat.xml",
        "🌍 BBC News (World)": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "🌍 CNN Top Stories": "http://rss.cnn.com/rss/edition.rss",
        "🌍 Al Jazeera English": "https://www.aljazeera.com/xml/rss/all.rss",
        "🌍 Euronews": "https://www.euronews.com/rss?format=mrss"
    }

    selected_feed_name = st.sidebar.selectbox("Valitse uutislähde:", list(FEEDS.keys()))
    feed_url = FEEDS[selected_feed_name]

    # Valintanappi käyttäjälle: Halutaanko käyttää AI-tiivistystä vai ei
    use_ai = st.sidebar.checkbox("Käytä OpenAI-päätoimittajaa (tiivistää uutiset)", value=True if openai_key else False)

    try:
        with st.spinner(f"Haetaan uutisia lähteestä {selected_feed_name}..."):
            import requests
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(feed_url, headers=headers, timeout=10)
            
            parsed_feed = feedparser.parse(response.content)
            entries = parsed_feed.entries[:8] # Otetaan top 8 uutista

        if not entries:
            st.warning(f"Uutisia ei löytynyt lähteestä '{selected_feed_name}'.")
        else:
            for entry in entries:
                title = getattr(entry, "title", "Ei otsikkoa")
                summary = getattr(entry, "summary", getattr(entry, "description", "Ei kuvausta"))
                link = getattr(entry, "link", "#")
                published = getattr(entry, "published", "")

                import re
                clean_summary = re.sub('<.*?>', '', summary)

                with st.container():
                    st.markdown(f"### [{title}]({link})")
                    if published:
                        st.caption(f"📅 Julkaistu: {published}")

                    # JOS OpenAI on käytössä, pyydetään tekoälyä tiivistämään uutinen ammattimaisesti
                    if use_ai and openai_key:
                        try:
                            from openai import OpenAI
                            client = OpenAI(api_key=openai_key)
                            
                            prompt = f"Tiivistä ja kirjoita seuraavasta uutisesta ammattimainen, selkeä ja sujuva uutisnosto suomeksi (enintään 2-3 lausetta):\nOtsikko: {title}\nSisältö: {clean_summary}"
                            
                            ai_response = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=150
                            )
                            ai_text = ai_response.choices[0].message.content
                            st.info(f"🤖 **Toimituksen tiivistelmä:**\n\n{ai_text}")
                        except Exception as ai_err:
                            # Jos AI-kutsu epäonnistuu, näytetään normaali siivottu teksti
                            st.write(clean_summary[:350] + ("..." if len(clean_summary) > 350 else ""))
                    else:
                        # Normaali teksti jos AI ei ole päällä
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
