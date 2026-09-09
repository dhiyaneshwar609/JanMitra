import os
import sys
import time
import wave
import json
import tempfile

# Force UTF-8 stdout encoding for Windows console support
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import sounddevice as sd
import numpy as np
import speech_recognition as sr

# Try importing Vosk for 100% Offline Speech Recognition
try:
    import vosk
    vosk.SetLogLevel(-1)
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

# =========================================================================
# ALL-INDIA GOVERNMENT SCHEMES COMPREHENSIVE KNOWLEDGE BASE (MULTIDOMAIN)
# =========================================================================
SCHEMES_DATABASE = {
    # 🌾 AGRICULTURE & FARMERS
    "pm_kisan": {
        "category": "🌾 Agriculture & Farmers",
        "title": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "keywords": ["pm kisan", "kisan", "farmer", "agriculture", "6000", "pmkisan", "vivasayi"],
        "eligibility": "All landholding farmer families across India (cultivable land registered in their name).",
        "benefit": "Financial benefit of Rs 6,000 per year transferred in 3 equal installments of Rs 2,000 directly into bank accounts.",
        "documents": "Aadhaar Card, Land Holding Documents (Patta/Chitta), Bank Passbook linked with Aadhaar.",
        "apply": "Apply at PM-KISAN Portal (pmkisan.gov.in) or nearby CSC (Common Service Center)."
    },
    "fasal_bima": {
        "category": "🌾 Agriculture & Farmers",
        "title": "PM Fasal Bima Yojana (PMFBY - Crop Insurance)",
        "keywords": ["fasal", "bima", "crop insurance", "harvest loss", "drought insurance", "flood crop"],
        "eligibility": "Farmers growing notified crops in notified areas (both sharecroppers & tenant farmers eligible).",
        "benefit": "Financial coverage & insurance against crop loss due to natural calamities, pests & diseases. Low premium (1.5% to 2%).",
        "documents": "Aadhaar Card, Land Records, Sowing Certificate from Village Administrative Officer (VAO), Bank Passbook.",
        "apply": "Apply online at pmfby.gov.in or through bank branches / CSCs."
    },
    "kisan_credit_card": {
        "category": "🌾 Agriculture & Farmers",
        "title": "Kisan Credit Card (KCC) Scheme",
        "keywords": ["kcc", "kisan credit", "farmer loan", "agri loan", "low interest loan"],
        "eligibility": "Farmers, individual/joint borrowers, tenant farmers, sharecroppers, and SHGs.",
        "benefit": "Access to short-term credit loans up to Rs 3 Lakhs at subsidized interest rates (effective interest 4% per annum with prompt repayment).",
        "documents": "Identity proof, Address proof, Land ownership documents, Passport size photos.",
        "apply": "Visit any commercial bank, RRB, or Cooperative Bank branch."
    },

    # 🏥 HEALTHCARE & MEDICAL
    "ayushman_bharat": {
        "category": "🏥 Healthcare & Medical",
        "title": "Ayushman Bharat (PM-JAY - Pradhan Mantri Jan Arogya Yojana)",
        "keywords": ["ayushman", "bharat", "pmjay", "health insurance", "5 lakh", "hospital free", "medical insurance"],
        "eligibility": "Poor, vulnerable families identified under SECC database and senior citizens aged 70+ (no income cap for 70+).",
        "benefit": "Free health cover of up to Rs 5 Lakhs per family per year for secondary and tertiary care hospitalization across India.",
        "documents": "Aadhaar Card, Ration Card / SECC verification, Ayushman Card.",
        "apply": "Check eligibility at pmjay.gov.in or visit any empaneled government/private hospital."
    },
    "tn_cmchis": {
        "category": "🏥 Healthcare & Medical",
        "title": "TN Chief Minister's Comprehensive Health Insurance Scheme (CMCHIS)",
        "keywords": ["cmchis", "tn health", "maruthuva kappeedus", "chief minister insurance", "tn hospital"],
        "eligibility": "Families residing in Tamil Nadu with annual income less than Rs 1.20 Lakhs.",
        "benefit": "Cashless medical treatment up to Rs 5 Lakhs per family per year in empaneled hospitals across Tamil Nadu.",
        "documents": "Aadhaar Card, Income Certificate, Family Smart Ration Card.",
        "apply": "Apply at District Collectorate or e-Sevai centers across Tamil Nadu."
    },
    "jan_aushadhi": {
        "category": "🏥 Healthcare & Medical",
        "title": "Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)",
        "keywords": ["janaushadhi", "jan aushadhi", "cheap medicine", "generic medicine", "low cost pharmacy"],
        "eligibility": "Open to all citizens of India.",
        "benefit": "High quality generic medicines and surgical items available at 50% to 90% lower prices compared to branded medicines.",
        "documents": "Doctor's prescription.",
        "apply": "Visit any Jan Aushadhi Kendra pharmacy near you (find at janaushadhi.gov.in)."
    },

    # 👩 WOMEN & CHILD EMPOWERMENT
    "sukanya_samriddhi": {
        "category": "👩 Women & Child Welfare",
        "title": "Sukanya Samriddhi Yojana (SSY - Girl Child Savings)",
        "keywords": ["sukanya", "samriddhi", "ssy", "girl child", "daughter savings", "post office girl"],
        "eligibility": "Parents/guardians of a girl child below 10 years of age (maximum 2 accounts per family).",
        "benefit": "Highest tax-free interest rate (currently 8.2% p.a.) with Tax deduction under Sec 80C. Maturity at 21 years or marriage after 18.",
        "documents": "Girl child Birth Certificate, Parent Aadhaar Card, Address proof, Photo.",
        "apply": "Open at any Post Office or authorized commercial bank."
    },
    "matru_vandana": {
        "category": "👩 Women & Child Welfare",
        "title": "Pradhan Mantri Matru Vandana Yojana (PMMVY - Maternity Benefit)",
        "keywords": ["pmmvy", "matru", "vandana", "pregnant", "maternity", "mother cash", "delivery benefit"],
        "eligibility": "Pregnant women and lactating mothers for the first live child (and second child if girl child).",
        "benefit": "Direct cash benefit of Rs 5,000 to Rs 6,000 transferred in bank account to meet nutrition & healthcare needs.",
        "documents": "Mother Aadhaar Card, MCP (Mother & Child Protection) Card, Bank Passbook.",
        "apply": "Apply through Anganwadi Center or online at pmmvy.wcd.gov.in."
    },
    "lakhpati_didi": {
        "category": "👩 Women & Child Welfare",
        "title": "Lakhpati Didi Scheme",
        "keywords": ["lakhpati", "didi", "shg", "women entrepreneur", "self help group women", "women business"],
        "eligibility": "Women associated with Women Self-Help Groups (SHGs) under Deendayal Antyodaya Yojana - NRLM.",
        "benefit": "Skill development training (micro-enterprises, LED bulb making, drone operation, agriculture) to enable earn Rs 1 Lakh+ annually.",
        "documents": "Aadhaar Card, SHG Membership proof, Bank Account.",
        "apply": "Register through local SHG / Block Development Office (BDO)."
    },

    # 💼 EMPLOYMENT, BUSINESS & SKILL LOANS
    "pm_mudra": {
        "category": "💼 Employment & Business",
        "title": "PM Mudra Yojana (PMMY - Business Loans)",
        "keywords": ["mudra", "loan", "business loan", "shishu", "kishor", "tarun", "collateral free loan", "shop loan"],
        "eligibility": "Non-corporate, non-farm small/micro enterprises (shopkeepers, artisans, small traders, startups).",
        "benefit": "Collateral-free loans up to Rs 10 Lakhs in 3 categories: Shishu (up to Rs 50k), Kishor (Rs 50k to 5L), Tarun (Rs 5L to 10L).",
        "documents": "Business Plan/Proposal, Aadhaar Card, PAN Card, Bank Statement (6 months), Business proof.",
        "apply": "Apply at any bank branch or online at udyamimitra.in."
    },
    "pm_vishwakarma": {
        "category": "💼 Employment & Business",
        "title": "PM Vishwakarma Scheme (Artisans & Craftsmen)",
        "keywords": ["vishwakarma", "artisan", "craftsman", "carpenter", "tailor", "blacksmith", "toolkit 15000"],
        "eligibility": "Traditional artisans & craftsmen working with hands/tools (18 traditional trades like carpenter, blacksmith, tailor, weaver, potter).",
        "benefit": "PM Vishwakarma Certificate, 5-7 days basic skill training with Rs 500/day stipend, Rs 15,000 Toolkit Incentive, & low-interest 5% collateral-free loans (up to Rs 3 Lakhs).",
        "documents": "Aadhaar Card, Bank Account details, Ration Card, Trade Proof.",
        "apply": "Apply at nearest CSC (Common Service Center) or online at pmvishwakarma.gov.in."
    },
    "mgnrega": {
        "category": "💼 Employment & Business",
        "title": "MGNREGA (Mahatma Gandhi National Rural Employment Guarantee Act)",
        "keywords": ["mgnrega", "100 days", "rural work", "nrega", "job card", "guaranteed employment"],
        "eligibility": "Adult members of rural households willing to do unskilled manual work.",
        "benefit": "Statutory guarantee of 100 days of wage employment per financial year at fixed state daily wages paid directly into bank account.",
        "documents": "Job Card application, Aadhaar Card, Bank Passbook, Passport photo.",
        "apply": "Apply at Gram Panchayat office."
    },
    "pm_svanidhi": {
        "category": "💼 Employment & Business",
        "title": "PM SVANidhi Scheme (Street Vendor Loan)",
        "keywords": ["svanidhi", "street vendor", "pavement vendor", "vendor loan", "10000 loan"],
        "eligibility": "Street vendors engaged in vending in urban areas.",
        "benefit": "Collateral-free working capital micro-loans of Rs 10,000 (1st tranche), Rs 20,000 (2nd tranche), and Rs 50,000 (3rd tranche) with 7% interest subsidy.",
        "documents": "Vending Certificate / Urban Local Body ID Card, Aadhaar Card, Bank Passbook.",
        "apply": "Apply online at pmsvanidhi.mohua.gov.in or at nearby bank branch."
    },

    # 🏡 HOUSING & SHELTER
    "pm_awas_yojana": {
        "category": "🏡 Housing & Shelter",
        "title": "PM Awas Yojana (PMAY - Free Pucca House Scheme)",
        "keywords": ["pm awas", "pmay", "housing scheme", "house subsidy", "home loan subsidy", "free house"],
        "eligibility": "Homeless families or families living in kutcha/dilapidated houses (Gramin & Urban streams).",
        "benefit": "Financial assistance of Rs 1.20 Lakh to Rs 1.30 Lakh for rural house construction, or interest subsidy up to Rs 2.67 Lakhs on home loans for urban poor.",
        "documents": "Aadhaar Card, Income Certificate, Land ownership proof / Job card, Bank Account details.",
        "apply": "Apply at Gram Panchayat / Municipal Corporation office or online at pmaymis.gov.in."
    },

    # 👴 PENSIONS & SOCIAL SECURITY
    "atal_pension": {
        "category": "👴 Pension & Social Security",
        "title": "Atal Pension Yojana (APY - Guaranteed Pension)",
        "keywords": ["atal pension", "apy", "pension scheme", "monthly pension", "old age security"],
        "eligibility": "All Indian citizens between 18 to 40 years of age having a bank account.",
        "benefit": "Guaranteed minimum monthly pension of Rs 1,000, Rs 2,000, Rs 3,000, Rs 4,000, or Rs 5,000 per month after age 60 based on contribution.",
        "documents": "Aadhaar Card, Mobile Number, Savings Bank Account.",
        "apply": "Apply through internet banking or visit your bank/post office branch."
    },

    # 💳 BANKING & FINANCIAL INCLUSION
    "jan_dhan": {
        "category": "💳 Financial Inclusion",
        "title": "PM Jan Dhan Yojana (PMJDY - Zero Balance Account)",
        "keywords": ["jan dhan", "zero balance", "bank account", "pmjdy", "rupay card", "accident insurance"],
        "eligibility": "Any Indian citizen without a basic bank account (aged 10+).",
        "benefit": "Zero balance savings account, free RuPay debit card, Rs 2 Lakh accidental insurance cover, & Rs 10,000 overdraft facility.",
        "documents": "Aadhaar Card or Voter ID / Driving License.",
        "apply": "Open account at any bank branch or Bank Mitra kiosk."
    },

    # 🎓 EDUCATION & SCHOLARSHIPS
    "pudhumai_penn": {
        "category": "🎓 Education & Scholarships",
        "title": "Pudhumai Penn Scheme (Moovalur Ramamirtham Ammaiyar Higher Education Assurance)",
        "keywords": ["pudhumai", "penn", "girl", "female", "moovalur", "1000", "pudumai", "penn scholarship"],
        "eligibility": "Female students who studied from Class 6 to 12 in Tamil Nadu Government Schools.",
        "benefit": "Financial assistance of Rs 1,000 per month directly deposited into student's bank account until completion of UG Degree / Diploma / ITI.",
        "documents": "Govt School Transfer Certificate (Class 6-12), Aadhaar Card, Bank Account details, College Admission Receipt.",
        "apply": "Apply through Penkalvi Portal (penkalvi.tn.gov.in) or via college nodal officer."
    },
    "tamizh_pudhalvan": {
        "category": "🎓 Education & Scholarships",
        "title": "Tamizh Pudhalvan Scheme",
        "keywords": ["tamizh", "pudhalvan", "boy", "male", "boys", "tamil", "pudhalvan scheme"],
        "eligibility": "Male students who studied from Class 6 to 12 in Tamil Nadu Government Schools pursuing higher education.",
        "benefit": "Financial assistance of Rs 1,000 per month directly into student's bank account for purchasing books, laptops, and learning tools.",
        "documents": "Govt School Study Certificate (6-12), Aadhaar Card, Bank Passbook, College Admission Proof.",
        "apply": "Apply through the official TN Higher Education Portal or college portal."
    },
    "naan_mudhalvan": {
        "category": "🎓 Education & Scholarships",
        "title": "Naan Mudhalvan Scheme",
        "keywords": ["naan", "mudhalvan", "skill", "training", "career", "placement", "nan mudhalvan"],
        "eligibility": "School and College students in Tamil Nadu.",
        "benefit": "Free skill development training, competitive exam preparation (UPSC, TNPSC, Banking), career counseling, and job placement assistance.",
        "documents": "Student ID card, Aadhaar, Educational mark sheets.",
        "apply": "Register at www.naanmudhalvan.tn.gov.in."
    },
    "7.5_quota": {
        "category": "🎓 Education & Scholarships",
        "title": "7.5% Government School Preference Quota",
        "keywords": ["7.5", "quota", "reservation", "engineering", "medical", "govt school quota"],
        "eligibility": "Students who studied Class 6 to 12 continuously in Tamil Nadu Government schools.",
        "benefit": "7.5% preferential seat reservation in Engineering (TNEA), Medical (NEET), Agriculture, Veterinary, Law, and Fisheries courses. 100% Tuition, Hostel & Transportation fee waived by TN Govt!",
        "documents": "Bonafide Certificate from Headmaster (Class 6 to 12), Community Certificate, Nativity Certificate.",
        "apply": "Select '7.5% Govt School Quota' option during single-window counseling (e.g., TNEA / TN Medical Admission)."
    },
    "post_matric": {
        "category": "🎓 Education & Scholarships",
        "title": "Post-Matric Scholarship Scheme (SC / ST / SCC)",
        "keywords": ["post", "matric", "sc", "st", "scc", "dalit", "tribal", "postmatric"],
        "eligibility": "SC / ST / Converted Christian SC (SCC) students pursuing post-matriculation / college studies with family annual income under Rs 2.5 Lakhs.",
        "benefit": "100% compulsory non-refundable fees (Tuition fee, Exam fee) reimbursed plus monthly maintenance allowance.",
        "documents": "Income Certificate, Community Certificate, Marksheet, Bank Passbook linked with Aadhaar.",
        "apply": "Apply through TN e-Scholarship portal (tn.gov.in/escholarship) or National Scholarship Portal."
    },
    "pragati": {
        "category": "🎓 Education & Scholarships",
        "title": "AICTE Pragati Scholarship for Girl Students",
        "keywords": ["pragati", "aicte", "girl scholarship", "engineering girl", "diploma girl"],
        "eligibility": "Female students admitted to 1st year of Degree/Diploma technical courses in AICTE-approved institutions. Family income must be under Rs 8 Lakhs/year.",
        "benefit": "Rs 50,000 per annum towards college fee, computer, books, equipment, and hostel expenses.",
        "documents": "Income Certificate, Class 10/12 Marksheet, AICTE college admission letter, Bank Account details.",
        "apply": "Apply online at National Scholarship Portal (scholarships.gov.in)."
    }
}

SUPPORTED_LANGUAGES = {
    "1": ("English", "en-IN"),
    "2": ("Tamil", "ta-IN"),
    "3": ("Hindi", "hi-IN"),
    "4": ("Telugu", "te-IN"),
    "5": ("Malayalam", "ml-IN"),
    "6": ("Kannada", "kn-IN"),
    "7": ("Auto-Detect (English / Tamil / Hindi)", "auto")
}

def record_audio_until_silence(sample_rate=44100, silence_duration=1.8, max_duration=30):
    """
    Dynamically record from microphone until user stops speaking (Voice Activity Detection).
    """
    print("\n[MIC] Calibrating background noise... Please stay quiet for 0.5 sec.")
    
    calib_frames = []
    chunk_size = int(sample_rate * 0.1)  # 100ms chunks
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
        for _ in range(5):
            data, _ = stream.read(chunk_size)
            calib_frames.append(data)
            
    ambient_noise = np.abs(np.concatenate(calib_frames)).max()
    threshold = max(600, int(ambient_noise * 2.8))
    
    print("[MIC] Listening continuously... Start speaking now! (Auto-stops when you pause)")
    print("-------------------------------------------------------------------------")
    
    frames = []
    silent_chunks = 0
    silence_limit = int(silence_duration / 0.1)
    max_limit = int(max_duration / 0.1)
    total_chunks = 0
    has_started_speaking = False
    
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
        while total_chunks < max_limit:
            data, _ = stream.read(chunk_size)
            frames.append(data)
            total_chunks += 1
            
            vol = np.abs(data).max()
            
            if vol > threshold:
                if not has_started_speaking:
                    print("   [VOICE DETECTED] Listening to your question...")
                    has_started_speaking = True
                silent_chunks = 0
            else:
                if has_started_speaking:
                    silent_chunks += 1
                    if silent_chunks >= silence_limit:
                        print("   [SILENCE DETECTED] Stopped speaking! Processing...")
                        break
                else:
                    if total_chunks > int(6.0 / 0.1):
                        print("   [TIMEOUT] No speech detected. Stopping.")
                        break

    if not frames:
        return None

    audio_bytes = np.concatenate(frames, axis=0).tobytes()
    
    temp_wav = os.path.join(tempfile.gettempdir(), "temp_user_voice.wav")
    with wave.open(temp_wav, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)
        
    return temp_wav

def recognize_speech_offline_vosk(wav_file_path):
    """
    100% OFFLINE Speech Recognition using local Vosk AI Model
    """
    if not VOSK_AVAILABLE:
        print("[OFFLINE ENGINE] Vosk library is not installed.")
        return None
        
    try:
        model_path = os.path.join(os.path.dirname(__file__), "model")
        if os.path.exists(model_path):
            model = vosk.Model(model_path)
        else:
            model = vosk.Model(lang="en-us")
            
        rec = vosk.KaldiRecognizer(model, 44100)
        
        with wave.open(wav_file_path, "rb") as wf:
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                rec.AcceptWaveform(data)
                
        res = json.loads(rec.FinalResult())
        text = res.get("text", "").strip()
        return text if text else None
    except Exception as e:
        print(f"[OFFLINE ENGINE NOTICE] Offline model loading or transcription notice: {e}")
        return None

def recognize_speech(wav_file_path, engine_mode="offline", lang_code="en-IN"):
    """
    Convert WAV audio file to text using either 100% OFFLINE Vosk engine or ONLINE Google Speech API
    """
    if engine_mode == "offline":
        print("[ENGINE] Running 100% OFFLINE Speech Recognition (Vosk AI)...")
        text = recognize_speech_offline_vosk(wav_file_path)
        if text:
            return text, "offline"
        print("[NOTICE] Offline recognition produced no text. Trying online engine fallback...")
        
    # Online Google Speech API Engine
    print(f"[ENGINE] Running ONLINE Speech Recognition ({lang_code})...")
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file_path) as source:
        audio_data = recognizer.record(source)
        
        if lang_code != "auto":
            try:
                text = recognizer.recognize_google(audio_data, language=lang_code)
                return text, lang_code
            except Exception:
                return None, lang_code
        else:
            for code in ["en-IN", "ta-IN", "hi-IN"]:
                try:
                    text = recognizer.recognize_google(audio_data, language=code)
                    if text:
                        return text, code
                except Exception:
                    continue
            return None, "auto"

def find_matching_scheme(user_query):
    """
    Find best matching scheme across ALL categories based on user query
    """
    if not user_query:
        return None
    
    query_lower = user_query.lower()
    best_match = None
    max_score = 0
    
    for key, data in SCHEMES_DATABASE.items():
        score = 0
        for kw in data["keywords"]:
            if kw in query_lower:
                score += 2
        if score > max_score:
            max_score = score
            best_match = data
            
    return best_match

def display_scheme_info(scheme_data):
    """
    Display structured scheme answer
    """
    if not scheme_data:
        print("\n[BOT RESPONSE]")
        print("Sorry, I could not find a specific government scheme matching your request.")
        print("\nPopular scheme keywords you can ask about:")
        print("  - Farmers   : PM Kisan, Fasal Bima, Kisan Credit Card")
        print("  - Health    : Ayushman Bharat, CMCHIS, Jan Aushadhi")
        print("  - Women     : Sukanya Samriddhi, PM Matru Vandana, Lakhpati Didi")
        print("  - Loans     : PM Mudra Loan, PM Vishwakarma, PM SVANidhi")
        print("  - Housing   : PM Awas Yojana")
        print("  - Pension   : Atal Pension Yojana")
        print("  - Education : Pudhumai Penn, Tamizh Pudhalvan, 7.5 Quota, Naan Mudhalvan")
        return

    print("\n" + "="*70)
    print(f"CATEGORY : {scheme_data['category']}")
    print(f"SCHEME   : {scheme_data['title']}")
    print("="*70)
    print(f"Eligibility  : {scheme_data['eligibility']}")
    print(f"Benefits     : {scheme_data['benefit']}")
    print(f"Documents    : {scheme_data['documents']}")
    print(f"How to Apply : {scheme_data['apply']}")
    print("="*70 + "\n")

def main():
    print("="*70)
    print("       🇮🇳 ALL-INDIA GOVERNMENT SCHEMES VOICE CHATBOT 🇮🇳")
    print("       Multi-Category & 100% OFFLINE AI Assistant")
    print("="*70)

    engine_mode = "offline"  # Default to 100% OFFLINE mode
    current_lang_code = "en-IN"
    current_lang_name = "English (en-IN)"

    while True:
        mode_str = "🔒 100% OFFLINE (Vosk AI)" if engine_mode == "offline" else f"🌐 ONLINE ({current_lang_name})"
        print(f"\n[Speech Engine Mode: {mode_str}]")
        print("Choose Option:")
        print("  [1] 🎤 Speak into Microphone (Dynamic Voice Input)")
        print("  [2] ⌨️  Type your question (Text Input)")
        print("  [3] ⚡ Toggle Speech Engine Mode (100% OFFLINE / ONLINE)")
        print("  [4] 🌐 Select Online Recognition Language")
        print("  [5] 📋 List All Available Scheme Categories")
        print("  [6] ❌ Exit")
        
        choice = input("\nEnter choice (1 to 6): ").strip()
        
        if choice == '1':
            wav_path = record_audio_until_silence()
            if wav_path:
                recognized_text, detected_lang = recognize_speech(wav_path, engine_mode=engine_mode, lang_code=current_lang_code)
                
                if recognized_text:
                    print(f'\n[YOU SAID] "{recognized_text}"')
                    matched_scheme = find_matching_scheme(recognized_text)
                    display_scheme_info(matched_scheme)
                else:
                    print("\n[NOTICE] Could not understand audio clearly. Please try speaking closer to mic or switch engine mode.")
            else:
                print("\n[NOTICE] No audio recorded.")
                
        elif choice == '2':
            user_text = input("\nEnter your question (e.g., PM Kisan, Ayushman Bharat, Mudra loan, Pudhumai Penn): ").strip()
            if user_text:
                matched_scheme = find_matching_scheme(user_text)
                display_scheme_info(matched_scheme)
            else:
                print("[WARNING] Please enter a question.")
                
        elif choice == '3':
            if engine_mode == "offline":
                engine_mode = "online"
                print("✅ Switched to ONLINE Speech Engine (Google Speech API).")
            else:
                engine_mode = "offline"
                print("✅ Switched to 100% OFFLINE Speech Engine (Vosk AI).")
                
        elif choice == '4':
            print("\nSelect Online Speech Recognition Language:")
            for k, (name, code) in SUPPORTED_LANGUAGES.items():
                print(f"  [{k}] {name}")
            lang_choice = input("\nEnter language number (1-7): ").strip()
            if lang_choice in SUPPORTED_LANGUAGES:
                current_lang_name, current_lang_code = SUPPORTED_LANGUAGES[lang_choice]
                print(f"✅ Language updated to: {current_lang_name}")
            else:
                print("⚠️ Invalid selection.")
                
        elif choice == '5':
            print("\n" + "="*70)
            print("📜 ALL AVAILABLE SCHEME CATEGORIES & SCHEMES")
            print("="*70)
            categories = {}
            for k, v in SCHEMES_DATABASE.items():
                cat = v["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(v["title"])
            for cat, scheme_list in categories.items():
                print(f"\n{cat}:")
                for s in scheme_list:
                    print(f"  • {s}")
            print("="*70 + "\n")
            
        elif choice == '6':
            print("\nThank you for using All-India Government Schemes Voice Chatbot! Goodbye!\n")
            break
        else:
            print("[WARNING] Invalid choice. Please choose 1 to 6.")

if __name__ == "__main__":
    main()
