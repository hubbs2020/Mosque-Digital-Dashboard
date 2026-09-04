import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import pytz
import time
import urllib.request
import json
import os

st.set_page_config(
    page_title="Mosque Digital Dashboard",
    page_icon="🕌",
    layout="wide"
)

# Robust Multi-Source Live Weather Fetcher
@st.cache_data(ttl=600)
def get_live_temp():
    try:
        url = "https://wttr.in/Hyderabad?format=j1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            temp_c = data['current_condition'][0]['temp_C']
            condition = data['current_condition'][0]['weatherDesc'][0]['value']
            return f"{temp_c}°C | {condition}"
    except Exception:
        pass

    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=17.3850&longitude=78.4867&current_weather=true"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            temp_c = int(round(data['current_weather']['temperature']))
            return f"{temp_c}°C"
    except Exception:
        return "30°C"

# Fetch Prayer Times & Hijri Calendar
@st.cache_data(ttl=3600)
def get_hyderabad_prayer_times():
    try:
        url = "http://api.aladhan.com/v1/timingsByCity?city=Hyderabad&country=India&method=1&school=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode())['data']
            timings = res_data['timings']
            hijri = res_data['date']['hijri']
            hijri_date_str = f"{hijri['day']} {hijri['month']['en']} {hijri['year']} AH"
            return timings, hijri_date_str
    except Exception:
        return None, ""

def parse_time(time_str):
    time_clean = time_str.split(" ")[0]
    return datetime.strptime(time_clean, "%H:%M")

def format_12hr(dt_obj):
    return dt_obj.strftime("%I:%M %p")

def add_minutes(dt_obj, mins):
    return dt_obj + timedelta(minutes=mins)

# Fetch Data
temp_display = get_live_temp()
api_timings, hijri_date = get_hyderabad_prayer_times()

now_hyd = datetime.now(pytz.timezone("Asia/Kolkata"))
current_time_dt = datetime.strptime(now_hyd.strftime("%H:%M:%S"), "%H:%M:%S")

if api_timings:
    fajr_start_dt = parse_time(api_timings['Fajr'])
    sunrise_dt = parse_time(api_timings['Sunrise'])
    maghrib_dt = parse_time(api_timings['Maghrib'])

    fajr_azan_dt = add_minutes(fajr_start_dt, 25)
    fajr_jamaat_dt = add_minutes(fajr_azan_dt, 15)
    fajr_azan = format_12hr(fajr_azan_dt)
    fajr_jamaat = format_12hr(fajr_jamaat_dt)

    maghrib_azan = format_12hr(maghrib_dt)
    maghrib_jamaat_dt = add_minutes(maghrib_dt, 3)
    maghrib_jamaat = format_12hr(maghrib_jamaat_dt)

    sunrise_str = format_12hr(sunrise_dt)
    zawal_dt = add_minutes(parse_time(api_timings['Dhuhr']), -10)
    zawal_str = format_12hr(zawal_dt)
    ishraq_str = format_12hr(add_minutes(sunrise_dt, 15))
    chast_str = format_12hr(add_minutes(sunrise_dt, 120))
else:
    sunrise_dt = parse_time("06:22")
    maghrib_dt = parse_time("18:32")
    fajr_azan, fajr_jamaat = "05:15 AM", "05:30 AM"
    maghrib_azan, maghrib_jamaat = "06:32 PM", "06:35 PM"
    sunrise_str, zawal_str, ishraq_str, chast_str = "06:22 AM", "12:15 PM", "06:37 AM", "08:22 AM"
    fajr_jamaat_dt = parse_time("05:30")
    maghrib_jamaat_dt = parse_time("18:35")

zuhr_azan, zuhr_jamaat = "01:00 PM", "01:15 PM"
asr_azan, asr_jamaat = "04:45 PM", "05:00 PM"
isha_azan, isha_jamaat = "07:45 PM", "08:00 PM"
jumaa_azan, jumaa_jamaat = "12:45 PM", "01:30 PM"

zuhr_jamaat_dt = parse_time("13:15")
asr_jamaat_dt = parse_time("17:00")
isha_jamaat_dt = parse_time("20:00")
jumaa_jamaat_dt = parse_time("13:30")

# 99 Names of Allah in sequence
names_of_allah = [
    ("الرَّحْمَنُ", "AR-RAHMAAN"),
    ("الرَّحِيمُ", "AR-RAHEEM"),
    ("الْمَلِكُ", "AL-MALIK"),
    ("الْقُدُّوسُ", "AL-QUDDUS"),
    ("السَّلاَمُ", "AS-SALAM"),
    ("الْمُؤْمِنُ", "AL-MU’MIN"),
    ("الْمُهَيْمِنُ", "AL-MUHAYMIN"),
    ("الْعَزِيزُ", "AL-AZIZ"),
    ("الْجَبَّارُ", "AL-JABBAR"),
    ("الْمُتَكَبِّرُ", "AL-MUTAKABBIR"),
    ("الْخَالِقُ", "AL-KHAALIQ"),
    ("الْبَارِئُ", "AL-BAARI"),
    ("الْمُصَوِّرُ", "AL-MUSAWWIR"),
    ("الْغَفَّارُ", "AL-GHAFFAR"),
    ("الْقَهَّارُ", "AL-QAHHAR"),
    ("الْوَهَّابُ", "AL-WAHHAAB"),
    ("الرَّزَّاقُ", "AR-RAZZAAQ"),
    ("الْفَتَّاحُ", "AL-FATTAAH"),
    ("الْعَلِيمُ", "AL-‘ALEEM"),
    ("الْقَابِضُ", "AL-QAABID"),
    ("الْبَاسِطُ", "AL-BAASIT"),
    ("الْخَافِضُ", "AL-KHAAFIDH"),
    ("الرَّافِعُ", "AR-RAAFI’"),
    ("الْمُعِزُّ", "AL-MU’IZZ"),
    ("الْمُذِلُّ", "AL-MUZIL"),
    ("السَّمِيعُ", "AS-SAMEE’"),
    ("الْبَصِيرُ", "AL-BASEER"),
    ("الْحَكَمُ", "AL-HAKAM"),
    ("الْعَدْلُ", "AL-‘ADL"),
    ("اللَّطِيفُ", "AL-LATEEF"),
    ("الْخَبِيرُ", "AL-KHABEER"),
    ("الْحَلِيمُ", "AL-HALEEM"),
    ("الْعَظِيمُ", "AL-‘AZEEM"),
    ("الْغَفُورُ", "AL-GHAFOOR"),
    ("الشَّكُورُ", "ASH-SHAKOOR"),
    ("الْعَلِيُّ", "AL-‘ALEE"),
    ("الْكَبِيرُ", "AL-KABEER"),
    ("الْحَفِيظُ", "AL-HAFEEDH"),
    ("الْمُقِيتُ", "AL-MUQEET"),
    ("الْحَسِيبُ", "AL-HASEEB"),
    ("الْجَلِيلُ", "AL-JALEEL"),
    ("الْكَرِيمُ", "AL-KAREEM"),
    ("الرَّقِيبُ", "AR-RAQEEB"),
    ("الْمُجِيبُ", "AL-MUJEEB"),
    ("الْوَاسِعُ", "AL-WAASI’"),
    ("الْحَكِيمُ", "AL-HAKEEM"),
    ("الْوَدُودُ", "AL-WADUD"),
    ("الْمَجِيدُ", "AL-MAJEED"),
    ("الْبَاعِثُ", "AL-BA’ITH"),
    ("الشَّهِيدُ", "ASH-SHAHEED"),
    ("الْحَقُّ", "AL-HAQQ"),
    ("الْوَكِيلُ", "AL-WAKEEL"),
    ("الْقَوِيُّ", "AL-QAWIYY"),
    ("الْمَتِينُ", "AL-MATEEN"),
    ("الْوَلِيُّ", "AL-WALIYY"),
    ("الْحَمِيدُ", "AL-HAMEED"),
    ("الْمُحْصِي", "AL-MUHSEE"),
    ("الْمُبْدِئُ", "AL-MUBDI"),
    ("الْمُعِيدُ", "AL-MUEED"),
    ("الْمُحْيِي", "AL-MUHYI"),
    ("الْمُمِيتُ", "AL-MUMEET"),
    ("الْحَيُّ", "AL-HAYY"),
    ("الْقَيُّومُ", "AL-QAYYOOM"),
    ("الْوَاجِدُ", "AL-WAAJID"),
    ("الْمَاجِدُ", "AL-MAAJID"),
    ("الْوَاحِدُ", "AL-WAAHID"),
    ("الْأَحَدُ", "AL-AHAD"),
    ("الصَّمَدُ", "AS-SAMAD"),
    ("الْقَادِرُ", "AL-QADEER"),
    ("الْمُقْتَدِرُ", "AL-MUQTADIR"),
    ("الْمُقَدِّمُ", "AL-MUQADDIM"),
    ("الْمُؤَخِّرُ", "AL-MU’AKHKHIR"),
    ("الْأَوَّلُ", "AL-AWWAL"),
    ("الْآخِرُ", "AL-AAKHIR"),
    ("الظَّاهِرُ", "AZ-ZAAHIR"),
    ("الْبَاطِنُ", "AL-BAATIN"),
    ("الْوَالِي", "AL-WAALI"),
    ("الْمُتَعَالِي", "AL-MUTA’ALI"),
    ("الْبَرُّ", "AL-BARR"),
    ("التَّوَابُ", "AT-TAWWAB"),
    ("الْمُنْتَقِمُ", "AL-MUNTAQIM"),
    ("الْعَفُوُّ", "AL-‘AFUWW"),
    ("الرَّؤُوفُ", "AR-RA’OOF"),
    ("مَالِكُ الْمُلْكِ", "MAALIK-UL-MULK"),
    ("ذُو الْجَلَالِ وَالْإِكْرَامِ", "DHUL-JALAALI WAL-IKRAAM"),
    ("الْمُقْسِطُ", "AL-MUQSIT"),
    ("الْجَامِعُ", "AL-JAAMI’"),
    ("الْغَنِيُّ", "AL-GHANIYY"),
    ("الْمُغْنِي", "AL-MUGHNI"),
    ("الْمَانِعُ", "AL-MANI’"),
    ("الضَّارُّ", "AD-DHARR"),
    ("النَّافِعُ", "AN-NAFI’"),
    ("النُّورُ", "AN-NUR"),
    ("الْهَادِي", "AL-HAADI"),
    ("الْبَدِيعُ", "AL-BADEE’"),
    ("الْبَاقِي", "AL-BAAQI"),
    ("الْوَارِثُ", "AL-WAARITH"),
    ("الْرَّشِيدُ", "AR-RASHEED"),
    ("الصَّبُورُ", "AS-SABOOR")
]

# All 99 blessed Names/Titles of Prophet Muhammad (S.A.W.S.)
names_of_muhammad = [
    ("مُحَمَّد", "Muhammad"), ("أَحْمَد", "Ahmad"), ("حَامِد", "Hamid"), ("مَحْمُود", "Mahmud"),
    ("قَاسِم", "Qasim"), ("عَاقِب", "Aqib"), ("حَاشِر", "Hashir"), ("مَاحِي", "Mahi"),
    ("شَاهِد", "Shahid"), ("بَشِير", "Bashir"), ("نَذِير", "Nadhir"), ("دَاعِي", "Da'i"),
    ("سِرَاج", "Siraj"), ("مُنِير", "Munir"), ("مُذَكِّر", "Muzakkir"), ("رَحْمَة", "Rahmah"),
    ("صَحِب", "Sahib"), ("مُصْطَفَى", "Mustafa"), ("مُجْتَبَى", "Mujtaba"), ("مُخْتَار", "Mukhtar"),
    ("أَمِين", "Amin"), ("وَلِيّ", "Wali"), ("فَاتِح", "Fatih"), ("خَاتِم", "Khatim"),
    ("طَاهِر", "Tahir"), ("مُطَهَّر", "Mutahhar"), ("طَيِّب", "Tayyib"), ("سَيِّد", "Sayyid"),
    ("رَسُول", "Rasul"), ("نَبِيّ", "Nabi"), ("حَبِيب", "Habib"), ("صَفِيّ", "Safiy"),
    ("نَجِيّ", "Najiy"), ("مُصَدِّق", "Musaddiq"), ("مُبَشِّر", "Mubashshir"), ("نَذِير", "Nadhir"),
    ("دَاعِي", "Da'i"), ("هَادِي", "Hadi"), ("مَهْدِي", "Mahdi"), ("مُعِين", "Mu'in"),
    ("شَفِيع", "Shafi'"), ("مُشَفَّع", "Mushaffa'"), ("أَوَّاه", "Awwah"), ("مُنِيب", "Munib"),
    ("حَرِيص", "Haris"), ("رَءُوف", "Ra'uf"), ("رَحِيم", "Rahim"), ("سَجِيد", "Sajid"),
    ("قَائِم", "Qaim"), ("ثَابِت", "Thabit"), ("مَقَام", "Maqam"), ("فَاضِل", "Fadil"),
    ("مَفْضُول", "Mafdoul"), ("جَوَاد", "Jawad"), ("مِعْطَاف", "Mi'taf"), ("سَخِيّ", "Sakhiy"),
    ("قَيِّم", "Qayyim"), ("مُقْتَصِد", "Muqtasid"), ("بَهِيّ", "Bahiyy"), ("زَكِيّ", "Zakiyy"),
    ("مُبِين", "Mubin"), ("خَلِيل", "Khalil"), ("نَجِيّ", "Najiyy"), ("مُهَذَّب", "Muhadhdhab"),
    ("حَافِظ", "Hafiz"), ("رَاعِي", "Ra'i"), ("مُنْذِر", "Mundhir"), ("مُبَيِّن", "Mubayyin"),
    ("مُبَارَك", "Mubarak"), ("مَدْعُوّ", "Mad'uw"), ("سَافِر", "Safir"), ("قَرِيب", "Qarib"),
    ("سَرِيع", "Sari'"), ("رَفِيع", "Rafic"), ("مَنِيع", "Mani'"), ("قَوِيّ", "Qawiyy"),
    ("أَمِين", "Amin"), ("مَأْمُون", "Ma'mun"), ("مُكَرَّم", "Mukarram"), ("مُعَظَّم", "Mu'azzam"),
    ("مُبَجَّل", "Mubajjal"), ("مُحْتَرَم", "Muhtaram"), ("مُقَدَّس", "Muqaddas"), ("رُوح", "Ruh"),
    ("نُور", "Nur"), ("سِرَاج", "Siraj"), ("مِصْبَاح", "Misbah"), ("بُرْهَان", "Burhan"),
    ("حُجَّة", "Hujjah"), ("دَلِيل", "Dalil"), ("شَاهِد", "Shahid"), ("مَشْهُود", "Mashhud"),
    ("بَشِير", "Bashir"), ("نَذِير", "Nadhir"), ("دَاعِي", "Da'i"), ("رَحْمَة", "Rahmah")
]

# Color pool for rotation
rotation_colors = ["#34d399", "#38bdf8", "#f59e0b", "#f43f5e", "#a78bfa", "#fbbf24", "#6ee7b7", "#60a5fa", "#f87171", "#c084fc"]

# Calculate active indices based on current Unix epoch time (changes every 10 seconds)
epoch_seconds = int(time.time())
allah_index = (epoch_seconds // 10) % len(names_of_allah)
muhammad_index = (epoch_seconds // 10) % len(names_of_muhammad)
color_index = (epoch_seconds // 10) % len(rotation_colors)
muhammad_color_index = ((epoch_seconds // 10) + 5) % len(rotation_colors)

active_allah_ar, active_allah_en = names_of_allah[allah_index]
active_muhammad_ar, active_muhammad_en = names_of_muhammad[muhammad_index]
active_item_color = rotation_colors[color_index]
active_muhammad_color = rotation_colors[muhammad_color_index]

# Fonts pool
fonts_pool = [
    ("Helvetica", "'Helvetica Neue', Helvetica, Arial, sans-serif"),
    ("Garamond", "Garamond, serif"),
    ("Futura", "Futura, 'Trebuchet MS', sans-serif"),
    ("Times New Roman", "'Times New Roman', Times, serif"),
    ("Roboto", "'Roboto', sans-serif"),
    ("Bodoni", "'Bodoni MT', Didot, 'Didot LT STD', serif"),
    ("Montserrat", "'Montserrat', sans-serif"),
    ("Playfair Display", "'Playfair Display', serif"),
    ("Lato", "'Lato', sans-serif"),
    ("Courier", "Courier, monospace")
]

current_hour = now_hyd.hour
font_index = (current_hour // 2) % len(fonts_pool)
active_font_name, active_font_family = fonts_pool[font_index]

# Initialize Theme State
if 'theme' not in st.session_state:
    is_day_auto = sunrise_dt.time() <= current_time_dt.time() < maghrib_dt.time()
    st.session_state.theme = 'night' if not is_day_auto else 'day'

# Top Bar with Clean Night/Day Mode Toggle Button
top_col1, top_col2 = st.columns([8, 2])
with top_col1:
    st.empty()

with top_col2:
    if st.session_state.theme == 'night':
        if st.button("☀️ Day Mode", key="btn_day", use_container_width=True):
            st.session_state.theme = 'day'
            st.rerun()
    else:
        if st.button("🌙 Night Mode", key="btn_night", use_container_width=True):
            st.session_state.theme = 'night'
            st.rerun()

is_day = (st.session_state.theme == 'day')

# Dynamic CSS Theme Palette
if is_day:
    bg_style = "radial-gradient(circle at top center, #f1f5f9 0%, #cbd5e1 100%)"
    card_bg = "linear-gradient(135deg, rgba(255, 255, 255, 0.85), rgba(241, 245, 249, 0.9))"
    card_border = "rgba(0, 0, 0, 0.12)"
    card_shadow = "0 10px 25px rgba(0, 0, 0, 0.1)"
    text_primary = "#0f172a"
    text_secondary = "#475569"
    clock_color = "#0284c7"
    hijri_color = "#047857"
    led_amber = "#d97706"
    led_green = "#059669"
    ticker_bg = "rgba(255, 255, 255, 0.7)"
    ticker_border = "rgba(4, 120, 87, 0.5)"
    btn_bg = "#ffffff"
    btn_text = "#0f172a"
    btn_border = "#047857"
else:
    bg_style = "radial-gradient(circle at top center, #0d1b2a 0%, #030712 100%)"
    card_bg = "linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(11, 15, 25, 0.85))"
    card_border = "rgba(255, 255, 255, 0.15)"
    card_shadow = "0 12px 30px rgba(0, 0, 0, 0.7)"
    text_primary = "#ffffff"
    text_secondary = "#9ca3af"
    clock_color = "#38bdf8"
    hijri_color = "#34d399"
    led_amber = "#f59e0b"
    led_green = "#10b981"
    ticker_bg = "rgba(9, 18, 29, 0.7)"
    ticker_border = "rgba(16, 185, 129, 0.6)"
    btn_bg = "rgba(15, 23, 42, 0.8)"
    btn_text = "#ffffff"
    btn_border = "rgba(255, 255, 255, 0.3)"

# Color pool for Kalima Tayyiba rotating every 2 minutes based on minute index
kalima_colors = [
    "#34d399", "#38bdf8", "#f59e0b", "#f43f5e", "#a78bfa", 
    "#fbbf24", "#6ee7b7", "#60a5fa", "#f87171", "#c084fc"
]
current_minute = now_hyd.minute
kalima_color_index = (current_minute // 2) % len(kalima_colors)
active_kalima_color = kalima_colors[kalima_color_index]

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Orbitron:wght@700;900&family=Roboto:wght@700&family=Montserrat:wght@700&family=Playfair+Display:wght@700&family=Lato:wght@700&display=swap');

    .stApp {{
        background: {bg_style};
        color: {text_primary};
        font-family: {active_font_family};
    }}
    header, footer {{visibility: hidden;}}

    .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
    }}

    div.stButton > button {{
        background-color: {btn_bg} !important;
        color: {btn_text} !important;
        border: 1.5px solid {btn_border} !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        box-shadow: {card_shadow} !important;
        font-family: {active_font_family} !important;
    }}

    .kalima-banner-box {{
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 6px 0;
        margin-bottom: 4px;
        background-color: transparent;
    }}

    .kalima-arabic-text {{
        font-family: 'Amiri', serif;
        width: 17cm !important;
        max-width: 100% !important;
        font-size: 3.6rem;
        font-weight: 700;
        color: {active_kalima_color};
        text-align: center;
        text-shadow: 0 0 25px {active_kalima_color}aa;
        direction: rtl;
        line-height: 1.25;
        letter-spacing: 1px;
    }}

    .allah-name-box {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        border: 1px solid {card_border};
        box-shadow: {card_shadow};
        border-radius: 16px;
        padding: 10px;
        text-align: center;
        margin-bottom: 12px;
    }}

    .allah-arabic-display {{
        font-family: 'Amiri', serif;
        font-size: 2.7rem;
        font-weight: 700;
        color: {active_item_color};
        line-height: 1.2;
        direction: rtl;
        text-shadow: 0 0 15px {active_item_color}88;
    }}

    .allah-english-display {{
        font-size: 1.2rem;
        font-weight: 700;
        color: {text_primary};
        margin-top: 4px;
    }}

    .muhammad-name-box {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        border: 1px solid {card_border};
        box-shadow: {card_shadow};
        border-radius: 16px;
        padding: 10px;
        text-align: center;
        margin-bottom: 12px;
    }}

    .muhammad-arabic-display {{
        font-family: 'Amiri', serif;
        font-size: 2.7rem;
        font-weight: 700;
        color: {active_muhammad_color};
        line-height: 1.2;
        direction: rtl;
        text-shadow: 0 0 15px {active_muhammad_color}88;
    }}

    .muhammad-english-display {{
        font-size: 1.2rem;
        font-weight: 700;
        color: {text_primary};
        margin-top: 4px;
    }}

    [data-testid="stImage"] img {{
        height: 620px !important;
        object-fit: cover !important;
        border-radius: 20px !important;
        border: 2px solid {card_border};
        box-shadow: {card_shadow};
    }}

    .clock-box {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid {card_border};
        box-shadow: {card_shadow};
        border-radius: 20px;
        padding: 12px;
        text-align: center;
        margin-bottom: 12px;
    }}

    .clock-time {{
        font-family: 'Orbitron', monospace;
        font-size: 4.8rem;
        font-weight: 900;
        color: {clock_color};
        letter-spacing: 2px;
        text-shadow: 0 0 20px {clock_color}aa;
        line-height: 1;
        margin: 6px 0;
    }}

    .clock-date {{
        font-size: 1.6rem;
        color: {text_primary};
        font-weight: 700;
        font-family: {active_font_family};
    }}

    .hijri-date {{
        font-size: 1.7rem;
        color: {hijri_color};
        font-weight: 800;
        font-family: {active_font_family};
    }}

    .temp-badge {{
        display: inline-block;
        font-family: 'Orbitron', monospace;
        font-size: 1.25rem;
        font-weight: 700;
        color: {led_amber};
        background: {card_bg};
        border: 1px solid {card_border};
        padding: 4px 18px;
        border-radius: 12px;
        margin-top: 4px;
    }}

    .solar-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-bottom: 12px;
    }}

    .solar-card {{
        background: {card_bg};
        backdrop-filter: blur(10px);
        border: 1px solid {card_border};
        box-shadow: {card_shadow};
        border-radius: 12px;
        padding: 6px;
        text-align: center;
    }}

    .solar-title {{
        font-size: 0.8rem;
        color: {text_secondary};
        font-weight: 700;
        font-family: {active_font_family};
    }}

    .solar-time {{
        font-family: 'Orbitron', monospace;
        font-size: 1.15rem;
        color: {led_amber};
        font-weight: 700;
    }}

    .table-box {{
        background: {card_bg};
        backdrop-filter: blur(14px);
        border: 1px solid {card_border};
        box-shadow: {card_shadow};
        border-radius: 20px;
        padding: 10px 15px;
    }}

    .timing-table {{
        width: 100%;
        border-collapse: collapse;
    }}

    .timing-table th {{
        color: {text_secondary};
        font-size: 1.1rem;
        padding-bottom: 6px;
        border-bottom: 2px solid {card_border};
        text-align: center;
        font-family: {active_font_family};
    }}

    .timing-table td {{
        padding: 8px 4px;
        text-align: center;
        font-family: 'Orbitron', monospace;
        font-size: 1.4rem;
        border-bottom: 1px solid {card_border};
    }}

    .led-green {{ color: {led_green}; font-weight: 800; }}
    .led-amber {{ color: {led_amber}; font-weight: 800; }}
    .arabic-text {{ font-family: 'Amiri', serif !important; font-size: 1.6rem !important; color: {hijri_color}; }}

    .countdown-box {{
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.9), rgba(185, 28, 28, 0.95));
        border: 2px solid #f87171;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.8);
        border-radius: 12px;
        padding: 8px;
        text-align: center;
        margin-bottom: 10px;
        animation: pulse 1s infinite alternate;
    }}

    .countdown-text {{
        font-family: 'Orbitron', monospace;
        font-size: 1.4rem;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 1px;
    }}

    @keyframes pulse {{
        0% {{ transform: scale(0.99); opacity: 0.9; }}
        100% {{ transform: scale(1.01); opacity: 1; }}
    }}
</style>
""", unsafe_allow_html=True)

# 1. Full Width Bold Kalima Header
st.markdown(f"""
<div class="kalima-banner-box">
    <div class="kalima-arabic-text">لَا إِلٰهَ إِلَّا اللهُ مُحَمَّدٌ رَسُولُ اللهِ</div>
</div>
""", unsafe_allow_html=True)

# 2. Dua Ticker Marquee Component (Including all original duas)
duas_list = [
    "لَا إِلٰهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ يُحْيِي وَيُمِيتُ وَهُوَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ",
    "سُبْحَانَ اللهِ وَالْحَمْدُ لِلَّهِ وَلَا إِلٰهَ إِلَّا اللهُ وَاللهُ أَكْبَرُ",
    "سُبْحَانَ اللهِ وَبِحَمْدِهِ سُبْحَانَ اللهِ الْعَظِيمِ وَبِحَمْدِهِ أَسْتَغْفِرُ اللهَ",
    "رَبِّ اغْفِرْ لَنَا وَتُبْ عَلَيْنَا إِنَّكَ أَنْتَ التَّوَّابُ الرَّحِيمُ",
    "اللَّهُمَّ صَلِّ عَلَى سَيِّدِنَا مُحَمَّدٍ اللَّهُمَّ صَلِّ عَلَيْهِ وَآلِهِ وَصَحْبِهِ وَسَلِّمْ",
    "أَعُوذُ بِكَلِمَاتِ اللهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ",
    "بِسْمِ اللهِ الَّذِي لَا يَضُرُّ مَعَ اسْمِهِ شَيْءٌ فِي الْأَرْضِ وَلَا فِي السَّمَاءِ وَهُوَ السَّمِيعُ الْعَلِيمُ",
    "رَضِينَا بِاللهِ رَبًّا وَبِالْإِسْلَامِ دِينًا وَبِسَيِّدِنَا مُحَمَّدٍ صَلَّى اللهُ عَلَيْهِ وَآلِهِ وَسَلَّمَ نَبِيًّا",
    "بِسْمِ اللهِ وَالْحَمْدُ لِلَّهِ وَالْخَيْرُ وَالشَّرُّ بِمَشِيئَةِ اللهِ",
    "آمَنَّا بِاللهِ وَالْيَوْمِ الْآخِرِ تُبْنَا إِلَى اللهِ بَاطِنًا وَظَاهِرًا",
    "يَا رَبَّنَا وَاعْفُ عَنَّا وَامْحُ الَّذِي كَانَ مِنَّا",
    "يَا ذَا الْجَلَالِ وَالْإِكْرَامِ أَمِتْنَا عَلَى دِينِ الْإِسْلَامِ",
    "يَا قَوِيُّ يَا مَتِينُ إِكْفِ شَرَّ الظَّالِمِينَ",
    "أَصْلَحَ اللهُ أُمُورَ الْمُسْلِمِينَ صَرَفَ اللهُ شَرَّ الْمُؤْذِينَ",
    "أَسْتَغْفِرُ اللهَ رَبَّ الْبَرَايَا أَسْتَغْفِرُ اللهَ مِنَ الْخَطَايَا"
]

ticker_colors = ["#0284c7", "#d97706", "#059669", "#dc2626", "#8b5cf6"] if is_day else ["#34d399", "#f59e0b", "#38bdf8", "#f43f5e", "#a78bfa"]
colored_duas = [f"<span style='color: {ticker_colors[i % len(ticker_colors)]};'>{dua}</span>" for i, dua in enumerate(duas_list)]
dua_string = " &nbsp;&nbsp;&nbsp; 🕋 &nbsp;&nbsp;&nbsp; ".join(colored_duas)

ticker_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&display=swap');
        body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
        .ticker-wrap {{
            width: 100%;
            border-top: 1px solid {ticker_border};
            border-bottom: 1px solid {ticker_border};
            background: {ticker_bg};
            backdrop-filter: blur(8px);
            padding: 8px 0;
            overflow: hidden;
            white-space: nowrap;
        }}
        .ticker-text {{ font-family: 'Amiri', serif; font-size: 2.2rem; font-weight: 700; direction: rtl; }}
    </style>
</head>
<body>
    <div class="ticker-wrap">
        <marquee behavior="scroll" direction="right" scrollamount="6">
            <span class="ticker-text">{dua_string}</span>
        </marquee>
    </div>
</body>
</html>
"""
components.html(ticker_html, height=65)

# 3. Time Calculations & Jama'at Countdown/Beep Logic
is_friday = (now_hyd.weekday() == 4)
jamaat_schedule = [
    ("FAJR", fajr_jamaat_dt),
    ("JUMAA" if is_friday else "ZUHR", jumaa_jamaat_dt if is_friday else zuhr_jamaat_dt),
    ("ASR", asr_jamaat_dt),
    ("MAGHRIB", maghrib_jamaat_dt),
    ("ISHA", isha_jamaat_dt)
]

countdown_msg = None
trigger_beep = False

for name, j_dt in jamaat_schedule:
    j_time_today = datetime.strptime(j_dt.strftime("%H:%M:00"), "%H:%M:%S")
    diff_seconds = (j_time_today - current_time_dt).total_seconds()

    if 0 < diff_seconds <= 60:
        countdown_msg = f"⏳ {name} JAMA'AT IN {int(diff_seconds)} SECONDS"
        break
    elif diff_seconds == 0 or diff_seconds == 1:
        trigger_beep = True
        break

# 4. Main Dashboard Layout
col_left, col_center, col_right = st.columns([1.2, 2.6, 1.2])

base_dir = os.path.dirname(__file__)
dome_img_path = os.path.join(base_dir, "Madina.jpg")
kaaba_img_path = os.path.join(base_dir, "Kaaba.jpg")

with col_left:
    # Names of Prophet Muhammad (S.A.W.S.) display right above the Madina image
    st.markdown(f"""
    <div class="muhammad-name-box">
        <div class="muhammad-arabic-display">{active_muhammad_ar}</div>
        <div class="muhammad-english-display">{active_muhammad_en} ﷺ</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.image(dome_img_path, use_container_width=True)

with col_center:
    time_str = now_hyd.strftime("%I:%M:%S %p")
    date_str = now_hyd.strftime("%A, %d %B %Y")

    if countdown_msg:
        st.markdown(f'<div class="countdown-box"><div class="countdown-text">{countdown_msg}</div></div>', unsafe_allow_html=True)

    if trigger_beep:
        beep_html = """
        <script>
            var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            var osc = audioCtx.createOscillator();
            var gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.value = 1000;
            gain.gain.value = 0.8;
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            setTimeout(function() { osc.stop(); }, 1200);
        </script>
        """
        components.html(beep_html, height=0, width=0)

    st.markdown(f"""
    <div class="clock-box">
        <div class="clock-date">{date_str}</div>
        <div class="hijri-date">{hijri_date}</div>
        <div class="clock-time">{time_str}</div>
        <div class="temp-badge">🌡️ {temp_display}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="solar-grid">
        <div class="solar-card"><div class="solar-title">TULU</div><div class="solar-time">{sunrise_str}</div></div>
        <div class="solar-card"><div class="solar-title">ZAWAL</div><div class="solar-time">{zawal_str}</div></div>
        <div class="solar-card"><div class="solar-title">ISHRAQ</div><div class="solar-time">{ishraq_str}</div></div>
        <div class="solar-card"><div class="solar-title">CHAST</div><div class="solar-time">{chast_str}</div></div>
    </div>
    """, unsafe_allow_html=True)

    prayers_data = [
        {"event": "🌙 FAJR", "azaan": fajr_azan, "jamaat": fajr_jamaat, "arabic": "فَجْر"},
        {"event": "☀️ ZUHR", "azaan": zuhr_azan, "jamaat": zuhr_jamaat, "arabic": "ظُهْر"},
        {"event": "🌤️ ASR", "azaan": asr_azan, "jamaat": asr_jamaat, "arabic": "عَصْر"},
        {"event": "🌇 MAGHRIB", "azaan": maghrib_azan, "jamaat": maghrib_jamaat, "arabic": "مَغْرِب"},
        {"event": "🌙 ISHA", "azaan": isha_azan, "jamaat": isha_jamaat, "arabic": "عِشَاء"},
        {"event": "🕌 JUMAA", "azaan": jumaa_azan, "jamaat": jumaa_jamaat, "arabic": "جُمُعَة"}
    ]

    rows_html = "".join([f"<tr><td style='text-align:left; font-weight:700;'>{item['event']}</td><td class='led-amber'>{item['azaan']}</td><td class='led-green'>{item['jamaat']}</td><td class='arabic-text' style='text-align:right;'>{item['arabic']}</td></tr>" for item in prayers_data])

    st.markdown(f"""
    <div class="table-box">
        <table class="timing-table">
            <thead>
                <tr>
                    <th style="text-align:left;">PRAYER</th>
                    <th>AZAN</th>
                    <th>JAMA'AT</th>
                    <th style="text-align:right;">نَماز</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    # 99 Names of Allah display right above the Kaaba image
    st.markdown(f"""
    <div class="allah-name-box">
        <div class="allah-arabic-display">{active_allah_ar}</div>
        <div class="allah-english-display">{active_allah_en}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.image(kaaba_img_path, use_container_width=True)

time.sleep(1)
st.rerun()