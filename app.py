import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import pytz
import time
import json
import os
import requests

st.set_page_config(
    page_title="Mosque Digital Dashboard",
    page_icon="🕌",
    layout="wide"
)

# ============================================================
# 1. AUTO-LOCATION (IP-based, falls back to Hyderabad)
# ============================================================
@st.cache_data(ttl=86400)
def get_location():
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return data['city'], data['country'], float(data['lat']), float(data['lon'])
    except:
        pass
    return "Hyderabad", "India", 17.3850, 78.4867

city, country, LAT, LON = get_location()

# ============================================================
# 2. WEATHER (Open-Meteo API with fallback)
# ============================================================
@st.cache_data(ttl=1800)
def get_live_temp():
    # ==========================================================
    # MANUAL OVERRIDE FOR HYDERABAD
    # If you want to force a specific temperature, uncomment the
    # line below and set your desired temperature and condition.
    # ==========================================================
    # return "32°C", "☀️ Clear Sky"  # <-- UNCOMMENT THIS AND EDIT IF NEEDED
    
    # PRIMARY: Open-Meteo API
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&timezone=auto"
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            data = response.json()
            temp_c = int(round(data['current_weather']['temperature']))
            weathercode = data['current_weather']['weathercode']
            
            conditions = {
                0: "☀️ Clear Sky", 1: "🌤️ Mostly Clear", 2: "⛅ Partly Cloudy",
                3: "☁️ Overcast", 45: "🌫️ Foggy", 48: "🌫️ Foggy",
                51: "🌧️ Light Drizzle", 53: "🌧️ Drizzle", 55: "🌧️ Heavy Drizzle",
                61: "🌧️ Light Rain", 63: "🌧️ Rain", 65: "🌧️ Heavy Rain",
                71: "❄️ Light Snow", 73: "❄️ Snow", 75: "❄️ Heavy Snow",
                80: "🌧️ Light Rain Showers", 81: "🌧️ Rain Showers", 82: "🌧️ Heavy Rain Showers",
                95: "⛈️ Thunderstorm", 96: "⛈️ Thunderstorm", 99: "⛈️ Thunderstorm"
            }
            condition = conditions.get(weathercode, "🌡️ Unknown")
            return f"{temp_c}°C", condition
    except Exception as e:
        print(f"Weather API error: {e}")
    
    # FALLBACK 1: wttr.in
    try:
        url = f"https://wttr.in/{city}?format=%t"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            temp_str = response.text.strip()
            return temp_str, "🌡️ Live"
    except:
        pass
    
    # FALLBACK 2: Hardcoded Hyderabad weather
    # You can change these values to match the current weather
    return "32°C", "☀️ Clear Sky"

# ============================================================
# 3. HIJRI DATE (Primary + Secondary APIs)
# ============================================================
@st.cache_data(ttl=3600)
def get_hijri_date_dynamic():
    # PRIMARY: Get current Hijri date from Aladhan timings endpoint
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=1"
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                hijri = data['data']['date']['hijri']
                return f"{hijri['day']} {hijri['month']['en']} {hijri['year']} AH"
    except Exception as e:
        print(f"Primary Hijri API error: {e}")
    
    # SECONDARY: Use the current date endpoint
    try:
        url = "https://api.aladhan.com/v1/currentDate"
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                hijri = data['data']['hijri']
                return f"{hijri['day']} {hijri['month']['en']} {hijri['year']} AH"
    except Exception as e:
        print(f"Secondary Hijri API error: {e}")
    
    # TERTIARY: Use Aladhan's calendar endpoint for today's date
    try:
        today = datetime.now()
        date_str = today.strftime("%d-%m-%Y")
        url = f"https://api.aladhan.com/v1/gToH/{date_str}"
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                hijri = data['data']['hijri']
                return f"{hijri['day']} {hijri['month']['en']} {hijri['year']} AH"
    except Exception as e:
        print(f"Tertiary Hijri API error: {e}")
    
    # Ultimate fallback
    return "27 Rabi' al-Awwal 1448 AH"

# ============================================================
# 4. PRAYER TIMES
# ============================================================
@st.cache_data(ttl=3600)
def get_prayer_data():
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=1&school=1"
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            res = response.json()['data']
            timings = res['timings']
            return timings
    except Exception as e:
        print(f"Prayer API error: {e}")
    return None

def parse_time(time_str):
    return datetime.strptime(time_str.split(" ")[0], "%H:%M")

def format_12hr(dt_obj):
    return dt_obj.strftime("%I:%M %p")

def add_minutes(dt_obj, mins):
    return dt_obj + timedelta(minutes=mins)

# ============================================================
# 5. FETCH ALL DATA
# ============================================================
now_hyd = datetime.now(pytz.timezone("Asia/Kolkata"))
current_time_dt = datetime.strptime(now_hyd.strftime("%H:%M:%S"), "%H:%M:%S")

# Get weather
temp_display, condition = get_live_temp()

# Get Hijri date
hijri_date = get_hijri_date_dynamic()

# Get prayer times
timings = get_prayer_data()

if timings:
    fajr_start = parse_time(timings['Fajr'])
    sunrise = parse_time(timings['Sunrise'])
    dhuhr = parse_time(timings['Dhuhr'])
    asr = parse_time(timings['Asr'])
    maghrib = parse_time(timings['Maghrib'])
    isha = parse_time(timings['Isha'])
else:
    sunrise = parse_time("06:22")
    maghrib = parse_time("18:32")
    fajr_start = parse_time("05:00")
    dhuhr = parse_time("12:00")
    asr = parse_time("16:00")
    isha = parse_time("19:30")

# ============================================================
# 6. FIXED "ROUND OF TIMINGS" FOR HYDERABAD
# ============================================================

# ---- FAJR (Fixed) ----
fajr_azan = "05:15 AM"
fajr_jamaat = "05:30 AM"
fajr_azan_dt = datetime.strptime(fajr_azan, "%I:%M %p")
fajr_jamaat_dt = datetime.strptime(fajr_jamaat, "%I:%M %p")

# ---- ZUHR (Fixed) ----
zuhr_azan = "12:45 PM"
zuhr_jamaat = "01:15 PM"
zuhr_azan_dt = datetime.strptime(zuhr_azan, "%I:%M %p")
zuhr_jamaat_dt = datetime.strptime(zuhr_jamaat, "%I:%M %p")

# ---- ASR (Fixed) ----
asr_azan = "04:30 PM"
asr_jamaat = "05:00 PM"
asr_azan_dt = datetime.strptime(asr_azan, "%I:%M %p")
asr_jamaat_dt = datetime.strptime(asr_jamaat, "%I:%M %p")

# ---- MAGHRIB (Dynamic - depends on sunset) ----
maghrib_azan = format_12hr(maghrib)
maghrib_jamaat = format_12hr(add_minutes(maghrib, 3))
maghrib_azan_dt = datetime.strptime(maghrib_azan, "%I:%M %p")
maghrib_jamaat_dt = datetime.strptime(maghrib_jamaat, "%I:%M %p")

# ---- ISHA (Fixed) ----
isha_azan = "07:45 PM"
isha_jamaat = "08:00 PM"
isha_azan_dt = datetime.strptime(isha_azan, "%I:%M %p")
isha_jamaat_dt = datetime.strptime(isha_jamaat, "%I:%M %p")

# ---- JUMU'AH (Fixed) ----
jumaa_azan = "12:30 PM"
jumaa_jamaat = "01:30 PM"
jumaa_azan_dt = datetime.strptime(jumaa_azan, "%I:%M %p")
jumaa_jamaat_dt = datetime.strptime(jumaa_jamaat, "%I:%M %p")

# ---- Solar / Spiritual times (dynamic) ----
zawal_dt = add_minutes(dhuhr, -10)
zawal_str = format_12hr(zawal_dt)
ishraq_str = format_12hr(add_minutes(sunrise, 15))
chast_str = format_12hr(add_minutes(sunrise, 120))
sunrise_str = format_12hr(sunrise)

# ---- JAMA'AT LIST for Countdown ----
is_friday = (now_hyd.weekday() == 4)
jamaat_schedule = [
    ("FAJR", fajr_jamaat_dt),
    ("JUMAA" if is_friday else "ZUHR", jumaa_jamaat_dt if is_friday else zuhr_jamaat_dt),
    ("ASR", asr_jamaat_dt),
    ("MAGHRIB", maghrib_jamaat_dt),
    ("ISHA", isha_jamaat_dt)
]

# ---- COUNTDOWN & SMART BEEP ----
countdown_msg = None
trigger_beep = False

for name, j_dt in jamaat_schedule:
    j_time_today = datetime.strptime(j_dt.strftime("%H:%M:00"), "%H:%M:%S")
    diff_seconds = (j_time_today - current_time_dt).total_seconds()
    if 0 < diff_seconds <= 60:
        countdown_msg = f"⏳ {name} JAMA'AT IN {int(diff_seconds)} SECONDS"
        break
    elif diff_seconds == 0 or diff_seconds == 1:
        is_night_time = current_time_dt >= parse_time("20:00") or current_time_dt <= parse_time("04:30")
        is_friday_khutbah = is_friday and (parse_time("12:30") <= current_time_dt <= parse_time("14:00"))
        if not is_night_time and not is_friday_khutbah:
            trigger_beep = True
        break

# ============================================================
# 7. CINEMATIC SKY BACKGROUND
# ============================================================
def get_sky_gradient():
    t = current_time_dt.time()
    fajr_t = fajr_start.time()
    sunrise_t = sunrise.time()
    dhuhr_t = dhuhr.time()
    asr_t = asr.time()
    maghrib_t = maghrib.time()
    isha_t = isha.time()

    if t < fajr_t:
        return "radial-gradient(circle at bottom, #0b1120 0%, #020617 100%)"
    elif fajr_t <= t < sunrise_t:
        return "radial-gradient(circle at bottom, #fef08a 0%, #f59e0b 40%, #1e293b 100%)"
    elif sunrise_t <= t < dhuhr_t:
        return "radial-gradient(circle at top, #38bdf8 0%, #0284c7 70%, #0c4a6e 100%)"
    elif dhuhr_t <= t < asr_t:
        return "radial-gradient(circle at top, #e0f2fe 0%, #7dd3fc 60%, #0284c7 100%)"
    elif asr_t <= t < maghrib_t:
        return "radial-gradient(circle at bottom, #fdba74 0%, #ea580c 50%, #431407 100%)"
    elif maghrib_t <= t < isha_t:
        return "radial-gradient(circle at bottom, #fca5a5 0%, #dc2626 40%, #450a0a 100%)"
    else:
        return "radial-gradient(circle at bottom, #172554 0%, #020617 100%)"

bg_style = get_sky_gradient()

# ============================================================
# 8. DYNAMIC BISMILLAH COLOR
# ============================================================
def get_bismillah_color():
    t = current_time_dt.time()
    sunrise_t = sunrise.time()
    maghrib_t = maghrib.time()
    
    if sunrise_t <= t < maghrib_t:
        return "#fbbf24", "0 0 40px rgba(251, 191, 36, 0.8)"
    elif (t >= sunrise_t and t < sunrise_t + timedelta(hours=1)) or \
         (t >= maghrib_t - timedelta(hours=1) and t < maghrib_t):
        return "#f59e0b", "0 0 40px rgba(245, 158, 11, 0.9)"
    else:
        return "#34d399", "0 0 18px #34d399aa"

bismillah_color, bismillah_shadow = get_bismillah_color()

# ============================================================
# 9. CSS THEME VARIABLES
# ============================================================
card_bg = "linear-gradient(135deg, rgba(15, 23, 42, 0.75), rgba(11, 15, 25, 0.8))"
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

# ============================================================
# 10. ROTATING NAMES (99 Names of Allah & Prophet)
# ============================================================
names_of_allah = [
    ("الرَّحْمَنُ", "AR-RAHMAAN"), ("الرَّحِيمُ", "AR-RAHEEM"), ("الْمَلِكُ", "AL-MALIK"),
    ("الْقُدُّوسُ", "AL-QUDDUS"), ("السَّلاَمُ", "AS-SALAM"), ("الْمُؤْمِنُ", "AL-MU’MIN"),
    ("الْمُهَيْمِنُ", "AL-MUHAYMIN"), ("الْعَزِيزُ", "AL-AZIZ"), ("الْجَبَّارُ", "AL-JABBAR"),
    ("الْمُتَكَبِّرُ", "AL-MUTAKABBIR"), ("الْخَالِقُ", "AL-KHAALIQ"), ("الْبَارِئُ", "AL-BAARI"),
    ("الْمُصَوِّرُ", "AL-MUSAWWIR"), ("الْغَفَّارُ", "AL-GHAFFAR"), ("الْقَهَّارُ", "AL-QAHHAR"),
    ("الْوَهَّابُ", "AL-WAHHAAB"), ("الرَّزَّاقُ", "AR-RAZZAAQ"), ("الْفَتَّاحُ", "AL-FATTAAH"),
    ("الْعَلِيمُ", "AL-‘ALEEM"), ("الْقَابِضُ", "AL-QAABID"), ("الْبَاسِطُ", "AL-BAASIT"),
    ("الْخَافِضُ", "AL-KHAAFIDH"), ("الرَّافِعُ", "AR-RAAFI’"), ("الْمُعِزُّ", "AL-MU’IZZ"),
    ("الْمُذِلُّ", "AL-MUZIL"), ("السَّمِيعُ", "AS-SAMEE’"), ("الْبَصِيرُ", "AL-BASEER"),
    ("الْحَكَمُ", "AL-HAKAM"), ("الْعَدْلُ", "AL-‘ADL"), ("اللَّطِيفُ", "AL-LATEEF"),
    ("الْخَبِيرُ", "AL-KHABEER"), ("الْحَلِيمُ", "AL-HALEEM"), ("الْعَظِيمُ", "AL-‘AZEEM"),
    ("الْغَفُورُ", "AL-GHAFOOR"), ("الشَّكُورُ", "ASH-SHAKOOR"), ("الْعَلِيُّ", "AL-‘ALEE"),
    ("الْكَبِيرُ", "AL-KABEER"), ("الْحَفِيظُ", "AL-HAFEEDH"), ("الْمُقِيتُ", "AL-MUQEET"),
    ("الْحَسِيبُ", "AL-HASEEB"), ("الْجَلِيلُ", "AL-JALEEL"), ("الْكَرِيمُ", "AL-KAREEM"),
    ("الرَّقِيبُ", "AR-RAQEEB"), ("الْمُجِيبُ", "AL-MUJEEB"), ("الْوَاسِعُ", "AL-WAASI’"),
    ("الْحَكِيمُ", "AL-HAKEEM"), ("الْوَدُودُ", "AL-WADUD"), ("الْمَجِيدُ", "AL-MAJEED"),
    ("الْبَاعِثُ", "AL-BA’ITH"), ("الشَّهِيدُ", "ASH-SHAHEED"), ("الْحَقُّ", "AL-HAQQ"),
    ("الْوَكِيلُ", "AL-WAKEEL"), ("الْقَوِيُّ", "AL-QAWIYY"), ("الْمَتِينُ", "AL-MATEEN"),
    ("الْوَلِيُّ", "AL-WALIYY"), ("الْحَمِيدُ", "AL-HAMEED"), ("الْمُحْصِي", "AL-MUHSEE"),
    ("الْمُبْدِئُ", "AL-MUBDI"), ("الْمُعِيدُ", "AL-MUEED"), ("الْمُحْيِي", "AL-MUHYI"),
    ("الْمُمِيتُ", "AL-MUMEET"), ("الْحَيُّ", "AL-HAYY"), ("الْقَيُّومُ", "AL-QAYYOOM"),
    ("الْوَاجِدُ", "AL-WAAJID"), ("الْمَاجِدُ", "AL-MAAJID"), ("الْوَاحِدُ", "AL-WAAHID"),
    ("الْأَحَدُ", "AL-AHAD"), ("الصَّمَدُ", "AS-SAMAD"), ("الْقَادِرُ", "AL-QADEER"),
    ("الْمُقْتَدِرُ", "AL-MUQTADIR"), ("الْمُقَدِّمُ", "AL-MUQADDIM"), ("الْمُؤَخِّرُ", "AL-MU’AKHKHIR"),
    ("الْأَوَّلُ", "AL-AWWAL"), ("الْآخِرُ", "AL-AAKHIR"), ("الظَّاهِرُ", "AZ-ZAAHIR"),
    ("الْبَاطِنُ", "AL-BAATIN"), ("الْوَالِي", "AL-WAALI"), ("الْمُتَعَالِي", "AL-MUTA’ALI"),
    ("الْبَرُّ", "AL-BARR"), ("التَّوَابُ", "AT-TAWWAB"), ("الْمُنْتَقِمُ", "AL-MUNTAQIM"),
    ("الْعَفُوُّ", "AL-‘AFUWW"), ("الرَّؤُوفُ", "AR-RA’OOF"), ("مَالِكُ الْمُلْكِ", "MAALIK-UL-MULK"),
    ("ذُو الْجَلَالِ وَالْإِكْرَامِ", "DHUL-JALAALI WAL-IKRAAM"), ("الْمُقْسِطُ", "AL-MUQSIT"),
    ("الْجَامِعُ", "AL-JAAMI’"), ("الْغَنِيُّ", "AL-GHANIYY"), ("الْمُغْنِي", "AL-MUGHNI"),
    ("الْمَانِعُ", "AL-MANI’"), ("الضَّارُّ", "AD-DHARR"), ("النَّافِعُ", "AN-NAFI’"),
    ("النُّورُ", "AN-NUR"), ("الْهَادِي", "AL-HAADI"), ("الْبَدِيعُ", "AL-BADEE’"),
    ("الْبَاقِي", "AL-BAAQI"), ("الْوَارِثُ", "AL-WAARITH"), ("الْرَّشِيدُ", "AR-RASHEED"),
    ("الصَّبُورُ", "AS-SABOOR")
]

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

rotation_colors = ["#34d399", "#38bdf8", "#f59e0b", "#f43f5e", "#a78bfa", "#fbbf24", "#6ee7b7", "#60a5fa", "#f87171", "#c084fc"]
epoch_seconds = int(time.time())
allah_index = (epoch_seconds // 10) % len(names_of_allah)
muhammad_index = (epoch_seconds // 10) % len(names_of_muhammad)
color_index = (epoch_seconds // 10) % len(rotation_colors)
muhammad_color_index = ((epoch_seconds // 10) + 5) % len(rotation_colors)
active_allah_ar, active_allah_en = names_of_allah[allah_index]
active_muhammad_ar, active_muhammad_en = names_of_muhammad[muhammad_index]
active_item_color = rotation_colors[color_index]
active_muhammad_color = rotation_colors[muhammad_color_index]

# ============================================================
# 11. DYNAMIC CSS + SKY BACKGROUND
# ============================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Orbitron:wght@700;900&display=swap');

    .stApp {{
        background: {bg_style};
        color: {text_primary};
        transition: background 2s ease;
    }}
    header, footer {{visibility: hidden;}}
    .block-container {{ padding-top: 0.5rem !important; padding-bottom: 0rem !important; }}

    .bismillah-static-container {{
        width: 100%; text-align: center; padding: 10px 0 25px 0; margin-bottom: 10px;
    }}
    .bismillah-text {{
        font-family: 'Amiri', serif; font-size: 3.6rem; font-weight: 700;
        color: {bismillah_color}; text-shadow: {bismillah_shadow}; direction: rtl; line-height: 1.3; margin: 0;
        transition: color 2s ease, text-shadow 2s ease;
    }}
    .allah-name-box, .muhammad-name-box {{
        background: {card_bg}; backdrop-filter: blur(12px); border: 1px solid {card_border};
        box-shadow: {card_shadow}; border-radius: 16px; padding: 10px; text-align: center; margin-bottom: 12px;
        animation: nameMagnify 1.8s ease-in-out infinite alternate;
    }}
    .allah-arabic-display {{
        font-family: 'Amiri', serif; font-size: 2.7rem; font-weight: 700;
        color: {active_item_color}; direction: rtl; text-shadow: 0 0 15px {active_item_color}88;
    }}
    .muhammad-arabic-display {{
        font-family: 'Amiri', serif; font-size: 2.7rem; font-weight: 700;
        color: {active_muhammad_color}; direction: rtl; text-shadow: 0 0 15px {active_muhammad_color}88;
    }}
    .allah-english-display, .muhammad-english-display {{
        font-size: 1.2rem; font-weight: 700; color: {text_primary}; margin-top: 4px;
    }}
    @keyframes nameMagnify {{
        0% {{ transform: scale(1); }}
        100% {{ transform: scale(1.08); box-shadow: 0 0 25px {active_item_color}66; }}
    }}
    [data-testid="stImage"] img {{
        height: 620px !important; object-fit: cover !important; border-radius: 20px !important;
        border: 2px solid {card_border}; box-shadow: {card_shadow};
    }}
    .clock-box {{
        background: {card_bg}; backdrop-filter: blur(12px); border: 1px solid {card_border};
        box-shadow: {card_shadow}; border-radius: 20px; padding: 12px; text-align: center; margin-bottom: 12px;
    }}
    .clock-time {{
        font-family: 'Orbitron', monospace; font-size: 4.8rem; font-weight: 900;
        color: {clock_color}; text-shadow: 0 0 20px {clock_color}aa; line-height: 1; margin: 6px 0;
    }}
    .clock-date {{ font-size: 1.6rem; color: {text_primary}; font-weight: 700; }}
    .hijri-date {{ font-size: 1.7rem; color: {hijri_color}; font-weight: 800; }}
    
    /* Weather Display */
    .weather-box {{
        display: inline-block;
        background: {card_bg};
        backdrop-filter: blur(10px);
        border: 1px solid {card_border};
        border-radius: 12px;
        padding: 8px 16px;
        margin-top: 4px;
        text-align: center;
    }}
    .weather-temp {{
        font-family: 'Orbitron', monospace;
        font-size: 1.25rem;
        font-weight: 700;
        color: {led_amber};
    }}
    .weather-condition {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {text_secondary};
        margin-left: 8px;
    }}

    .solar-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }}
    .solar-card {{
        background: {card_bg}; backdrop-filter: blur(10px); border: 1px solid {card_border};
        box-shadow: {card_shadow}; border-radius: 12px; padding: 6px; text-align: center;
    }}
    .solar-title {{ font-size: 0.8rem; color: {text_secondary}; font-weight: 700; }}
    .solar-time {{ font-family: 'Orbitron', monospace; font-size: 1.15rem; color: {led_amber}; font-weight: 700; }}
    .table-box {{ background: {card_bg}; backdrop-filter: blur(14px); border: 1px solid {card_border}; box-shadow: {card_shadow}; border-radius: 20px; padding: 10px 15px; }}
    .timing-table {{ width: 100%; border-collapse: collapse; }}
    .timing-table th {{ color: {text_secondary}; font-size: 1.1rem; padding-bottom: 6px; border-bottom: 2px solid {card_border}; text-align: center; }}
    .timing-table td {{ padding: 8px 4px; text-align: center; font-family: 'Orbitron', monospace; font-size: 1.4rem; border-bottom: 1px solid {card_border}; }}
    .led-green {{ color: {led_green}; font-weight: 800; }}
    .led-amber {{ color: {led_amber}; font-weight: 800; }}
    .arabic-text {{ font-family: 'Amiri', serif !important; font-size: 1.6rem !important; color: {hijri_color}; }}

    .countdown-box {{
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.9), rgba(185, 28, 28, 0.95));
        border: 2px solid #f87171; box-shadow: 0 0 25px rgba(239, 68, 68, 0.8);
        border-radius: 12px; padding: 8px; text-align: center; margin-bottom: 10px;
        animation: pulse 1s infinite alternate;
    }}
    .countdown-text {{ font-family: 'Orbitron', monospace; font-size: 1.4rem; font-weight: 900; color: #ffffff; letter-spacing: 1px; }}
    @keyframes pulse {{ 0% {{ transform: scale(0.99); opacity: 0.9; }} 100% {{ transform: scale(1.01); opacity: 1; }} }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 12. BISMILLAH HEADER
# ============================================================
st.markdown("""
<div class="bismillah-static-container">
    <div class="bismillah-text">بِسْمِ ٱللَّٰهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 13. TICKER (Continuous Scrolling with Zoom Effect)
# ============================================================
duas_list = [
    "لَا إِلٰهَ إِلَّا اللهُ مُحَمَّدٌ رَسُولُ اللهِ",
    "لَا إِلٰهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ يُحْيِي وَيُمِيتُ وَهُوَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ",
    "سُبْحَانَ اللهِ وَالْحَمْدُ لِلَّهِ وَلَا إِلٰهَ إِلَّا اللهُ وَاللهُ أَكْبَرُ",
    "سُبْحَانَ اللهِ وَبِحَمْدِهِ سُبْحَانَ اللهِ الْعَظِيمِ وَبِحَمْدِهِ أَسْتَغْفِرُ اللهَ",
    "رَبِّ اغْفِرْ لَنَا وَتُبْ عَلَيْنَا إِنَّكَ أَنْتَ التَّوَّابُ الرَّحِيمُ",
    "اللَّهُمَّ صَلِّ عَلَى سَيِّدِنَا مُحَمَّدٍ اللَّهُمَّ صَلِّ عَلَيْهِ وَآلِهِ وَصَحْبِهِ وَسَلَّمْ",
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

ticker_colors = ["#34d399", "#38bdf8", "#f59e0b", "#f43f5e", "#a78bfa"]
colored_duas = []
kalima_color_index = (now_hyd.minute // 2) % len(ticker_colors)
active_kalima_color = ticker_colors[kalima_color_index]

for i, dua in enumerate(duas_list):
    c = ticker_colors[i % len(ticker_colors)]
    if i == 0:
        colored_duas.append(f"<span class='dua-item' style='color: {active_kalima_color}; font-size: 2.6rem; font-weight: 800;'>{dua}</span>")
    else:
        colored_duas.append(f"<span class='dua-item' style='color: {c};'>{dua}</span>")

separator_icon = "<span class='ticker-sep'>🕋</span>"
single_pass_str = f" {separator_icon} ".join(colored_duas)
gap_spacer = "<span style='display: inline-block; width: 250px;'></span>"

ticker_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&display=swap');
        body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
        .ticker-container {{
            width: 100%; border-top: 1px solid {ticker_border}; border-bottom: 1px solid {ticker_border};
            background: {ticker_bg}; backdrop-filter: blur(8px); padding: 20px 0;
            overflow-x: auto; white-space: nowrap; display: flex; align-items: center;
            direction: ltr; cursor: pointer; user-select: none; scrollbar-width: none;
        }}
        .ticker-container::-webkit-scrollbar {{ display: none; }}
        .ticker-text {{ font-family: 'Amiri', serif; font-size: 2.2rem; font-weight: 700; padding-right: 2rem; display: inline-block; }}
        .dua-item {{ display: inline-block; margin: 0 60px; padding: 10px 0; transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1), text-shadow 0.3s ease; transform-origin: center center; }}
        .dua-item.zoomed {{ transform: scale(1.35); text-shadow: 0 0 20px rgba(255, 255, 255, 0.7); }}
        .ticker-sep {{ display: inline-block; margin: 0 30px; font-size: 1.8rem; vertical-align: middle; }}
    </style>
</head>
<body>
    <div class="ticker-container" id="ticker">
        <div class="ticker-text" id="content">{gap_spacer} {single_pass_str}</div>
    </div>
    <script>
        const container = document.getElementById('ticker');
        const content = document.getElementById('content');
        const duaItems = document.querySelectorAll('.dua-item');
        let isPaused = false; const scrollSpeed = 0.8;
        const maxScroll = content.scrollWidth - container.clientWidth;
        const savedPos = localStorage.getItem('mosque_ticker_pos_ltr');
        container.scrollLeft = savedPos !== null ? parseFloat(savedPos) : maxScroll;
        container.addEventListener('mouseenter', () => {{ isPaused = true; }});
        container.addEventListener('mouseleave', () => {{ isPaused = false; }});
        container.addEventListener('mousedown', () => {{ isPaused = true; }});
        container.addEventListener('mouseup', () => {{ isPaused = false; }});
        function checkZoomEffect() {{
            const centerPoint = window.innerWidth / 2;
            duaItems.forEach(item => {{
                const rect = item.getBoundingClientRect();
                if (rect.left <= centerPoint && rect.right >= centerPoint) {{ item.classList.add('zoomed'); }}
                else {{ item.classList.remove('zoomed'); }}
            }});
        }}
        function step() {{
            if (!isPaused) {{
                container.scrollLeft -= scrollSpeed;
                localStorage.setItem('mosque_ticker_pos_ltr', container.scrollLeft);
                if (container.scrollLeft <= 0) {{ container.scrollLeft = content.scrollWidth - container.clientWidth; }}
                checkZoomEffect();
            }}
            requestAnimationFrame(step);
        }}
        requestAnimationFrame(step);
    </script>
</body>
</html>
"""
components.html(ticker_html, height=110)

# ============================================================
# 14. MAIN LAYOUT (3 Columns)
# ============================================================
col_left, col_center, col_right = st.columns([1.2, 2.6, 1.2])

# ---- LEFT COLUMN: Prophet's Name + Madina ----
with col_left:
    st.markdown(f"""
    <div class="muhammad-name-box">
        <div class="muhammad-arabic-display">{active_muhammad_ar}</div>
        <div class="muhammad-english-display">{active_muhammad_en} ﷺ</div>
    </div>
    """, unsafe_allow_html=True)
    st.image("Madina.jpg", use_container_width=True)

# ---- CENTER COLUMN: Clock, Weather, Prayers ----
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
            osc.type = 'sine'; osc.frequency.value = 1000; gain.gain.value = 0.8;
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start(); setTimeout(function() { osc.stop(); }, 1200);
        </script>
        """
        components.html(beep_html, height=0, width=0)

    st.markdown(f"""
    <div class="clock-box">
        <div class="clock-date">{date_str}</div>
        <div class="hijri-date">{hijri_date}</div>
        <div class="clock-time">{time_str}</div>
        <div class="weather-box">
            <span class="weather-temp">{temp_display}</span>
            <span class="weather-condition">{condition}</span>
        </div>
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
        {"event": "🌆 MAGHRIB", "azaan": maghrib_azan, "jamaat": maghrib_jamaat, "arabic": "مَغْرِب"},
        {"event": "🌃 ISHA", "azaan": isha_azan, "jamaat": isha_jamaat, "arabic": "عِشَاء"},
        {"event": "🕌 JUMAA", "azaan": jumaa_azan, "jamaat": jumaa_jamaat, "arabic": "جُمُعَة"}
    ]

    table_rows = ""
    for row in prayers_data:
        table_rows += f"<tr><td style='text-align: left; font-weight: 700;'>{row['event']}</td><td class='led-amber'>{row['azaan']}</td><td class='led-green'>{row['jamaat']}</td><td class='arabic-text'>{row['arabic']}</td></tr>"

    st.markdown(f"""
    <div class="table-box">
        <table class="timing-table">
            <thead><tr><th style="text-align: left;">PRAYER</th><th>AZAN</th><th>JAMA'AT</th><th>ARABIC</th></tr></thead>
            <tbody>{table_rows}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ---- RIGHT COLUMN: Allah's Name + Kaaba ----
with col_right:
    st.markdown(f"""
    <div class="allah-name-box">
        <div class="allah-arabic-display">{active_allah_ar}</div>
        <div class="allah-english-display">{active_allah_en}</div>
    </div>
    """, unsafe_allow_html=True)
    st.image("Kaaba.jpg", use_container_width=True)

# ============================================================
# 15. CONTINUOUS REFRESH
# ============================================================
time.sleep(1)
st.rerun()