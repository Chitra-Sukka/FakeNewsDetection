"""Creates sample test articles in indian_test/real and indian_test/fake.

IMPORTANT: these texts were WRITTEN FOR TESTING (they are not copied from real
newspapers). They check that the pipeline handles Indian vocabulary, Hindi and
Telugu. For a real measurement, also add genuine articles and debunked viral
messages to the same folders (one .txt file each, UTF-8).
Files starting with "hard_" are deliberately tricky.
"""
import os

SAMPLES = {
    # ------------------------------------------------------------ REAL (English)
    "real/en_01_economy.txt": """The central bank on Friday left its key lending rate unchanged, saying inflation had eased but food prices still needed close watching. The governor told reporters after the monetary policy committee meeting that growth remained steady at about 7 per cent and that the bank would act if price pressures returned. Economists said the decision was widely expected, and bond yields barely moved after the announcement.""",
    "real/en_02_kerala_rain.txt": """Heavy rain lashed several districts of Kerala on Wednesday, forcing the state government to close schools in three districts and open relief camps for families living near rivers. A senior official of the disaster management authority said water levels in two rivers were close to the danger mark but were expected to fall by Thursday morning. The chief minister's office said teams of the National Disaster Response Force had been deployed in low-lying areas.""",
    "real/en_03_lok_sabha.txt": """The Lok Sabha on Tuesday passed a bill to simplify rules for small businesses after a debate that lasted nearly four hours. The minister in charge told the House that the amendments would reduce paperwork and cut the time needed to register a new firm. Opposition members said they had concerns about enforcement and demanded that the bill be sent to a standing committee, but the motion was defeated by voice vote.""",
    "real/en_04_cricket.txt": """India beat Australia by six wickets in the second one-day international in Hyderabad on Sunday, taking an unassailable lead in the three-match series. Chasing 248, the home side reached the target with 12 balls to spare after an unbeaten half-century from the captain. The Australian captain said his bowlers had failed to build pressure in the middle overs.""",
    "real/en_05_supreme_court.txt": """The Supreme Court on Monday asked the Centre and all state governments to file a status report within four weeks on the condition of government-run shelter homes. A bench headed by the Chief Justice said the court wanted details of inspections carried out in the last two years. Lawyers for the petitioners told the bench that several homes lacked basic facilities. The matter will be heard again next month.""",
    "real/hard_en_06_flood_story.txt": """Residents wept with relief as rescue boats finally reached the marooned village on Saturday after three days without food or clean water. "We thought nobody would come," said a farmer who had spent two nights on his roof with his family and two goats. Officials said more than 2,000 people had been moved to safety and that relief supplies, including drinking water and medicines, were being sent to the area. Volunteers from nearby towns had been cooking meals since Friday night.""",

    # ------------------------------------------------------------ FAKE (English)
    "fake/en_01_gps_note.txt": """BREAKING NEWS!!! The new Rs 2000 note has a secret nano GPS chip that can track the note even 120 metres below the ground. This is a great step by our government to end black money. Please forward this message to all your friends and family before the media hides this truth. Share it with 10 groups and see how India will change.""",
    "fake/en_02_5g_corona.txt": """URGENT WARNING: Doctors have confirmed that the corona virus is spread by 5G towers and not by people. The government is hiding this truth from you. Stay away from phone towers, and forward this to everyone you love before this message is deleted. Drink hot water with turmeric and lemon every hour and the virus will die in your body within 24 hours, they do not want you to know this.""",
    "fake/en_03_free_recharge.txt": """Great news!! Jio is giving 3 months free recharge to all Indians to celebrate its anniversary. Click on the link below and fill in your details to get your free 399 rupees recharge today only. Share this message with 20 friends on WhatsApp to claim the offer, otherwise your number will be blocked. Hurry up, only a few hours left!""",
    "fake/en_04_unesco_anthem.txt": """Did you know? UNESCO has declared Jana Gana Mana as the best national anthem in the world. This is a proud moment for every Indian and the western media is not showing it to you. Share this with everyone to make sure every Indian knows this before it is too late.""",
    "fake/en_05_whatsapp_charges.txt": """Important message for all WhatsApp users: from tomorrow WhatsApp will start charging 30 paise for every message you send. Only those who forward this message to at least 15 contacts will stay free. Your account will turn blue if you have forwarded it, so do it now and save your money. Please share with all your groups.""",
    "fake/hard_en_06_cash_limit.txt": """The finance ministry will bring in a rule next month that bans all cash payments above Rs 5,000, according to officials familiar with the matter. Shopkeepers who accept larger amounts in cash will be fined, the officials said. Banks have been told to prepare for a surge in digital transactions, and a formal notification is expected within days.""",

    # ------------------------------------------------------------ REAL (Hindi)
    "real/hi_01_weather.txt": """मौसम विभाग ने मंगलवार को जानकारी दी कि अगले तीन दिनों में उत्तर प्रदेश और बिहार के कई जिलों में भारी बारिश हो सकती है। अधिकारियों ने बताया कि निचले इलाकों में रहने वाले लोगों को सुरक्षित स्थानों पर पहुंचाने के लिए प्रशासन ने नावें और राहत दल तैनात कर दिए हैं। मुख्यमंत्री कार्यालय ने कहा कि स्थिति पर लगातार नजर रखी जा रही है और जरूरत पड़ने पर स्कूल बंद किए जाएंगे।""",
    "real/hi_02_court.txt": """सर्वोच्च न्यायालय ने सोमवार को केंद्र सरकार से कहा कि वह सरकारी अस्पतालों में दवाओं की उपलब्धता पर चार सप्ताह के भीतर रिपोर्ट दाखिल करे। मुख्य न्यायाधीश की अध्यक्षता वाली पीठ ने कहा कि अदालत यह जानना चाहती है कि पिछले दो वर्षों में कितने अस्पतालों का निरीक्षण किया गया। याचिकाकर्ताओं के वकील ने पीठ को बताया कि कई अस्पतालों में जरूरी दवाएं उपलब्ध नहीं हैं। मामले की अगली सुनवाई अगले महीने होगी।""",

    # ------------------------------------------------------------ FAKE (Hindi)
    "fake/hi_01_5g_corona.txt": """ज़रूरी सूचना!!! डॉक्टरों ने पुष्टि की है कि कोरोना वायरस 5G टावरों से फैलता है, लेकिन सरकार यह सच्चाई आपसे छिपा रही है। इस संदेश को अपने सभी परिवार और दोस्तों को तुरंत भेजें, इससे पहले कि इसे डिलीट कर दिया जाए। रोज़ गर्म पानी में हल्दी और नींबू पीने से वायरस 24 घंटे में शरीर से खत्म हो जाता है, यह बात कोई आपको नहीं बताएगा।""",
    "fake/hi_02_free_recharge.txt": """बधाई हो!! जियो अपनी सालगिरह पर सभी भारतीयों को 3 महीने का मुफ्त रिचार्ज दे रहा है। नीचे दिए गए लिंक पर क्लिक करके अपनी जानकारी भरें और आज ही अपना मुफ्त रिचार्ज पाएं। इस संदेश को 20 दोस्तों को व्हाट्सऐप पर भेजें, वरना आपका नंबर ब्लॉक हो जाएगा। जल्दी करें, केवल कुछ घंटे बाकी हैं!""",

    # ------------------------------------------------------------ REAL (Telugu)
    "real/te_01_hyderabad_rain.txt": """హైదరాబాద్‌లో మంగళవారం సాయంత్రం భారీ వర్షం కురవడంతో పలు ప్రాంతాల్లో రోడ్లపై నీరు నిలిచింది. వాహనాల రాకపోకలకు తీవ్ర ఇబ్బంది ఏర్పడిందని ట్రాఫిక్ పోలీసులు తెలిపారు. లోతట్టు ప్రాంతాల్లో ఉన్న ప్రజలను సురక్షిత ప్రదేశాలకు తరలించేందుకు అధికారులు చర్యలు చేపట్టారని నగర మేయర్ కార్యాలయం పేర్కొంది. రాబోయే రెండు రోజులు కూడా వర్షాలు కొనసాగే అవకాశం ఉందని వాతావరణ శాఖ హెచ్చరించింది.""",
    "real/te_02_textbooks.txt": """రాష్ట్ర ప్రభుత్వం గురువారం ప్రభుత్వ పాఠశాలల్లో విద్యార్థులకు ఉచిత పాఠ్యపుస్తకాలు అందించే పథకాన్ని మరో రెండు సంవత్సరాలు పొడిగిస్తున్నట్లు ప్రకటించింది. ఈ నిర్ణయంతో సుమారు ముప్పై లక్షల మంది విద్యార్థులకు ప్రయోజనం కలుగుతుందని విద్యాశాఖ మంత్రి విలేకరులతో చెప్పారు. పథకం అమలుకు అవసరమైన నిధులను వచ్చే బడ్జెట్‌లో కేటాయిస్తామని అధికారులు తెలిపారు.""",

    # ------------------------------------------------------------ FAKE (Telugu)
    "fake/te_01_free_recharge.txt": """శుభవార్త!! జియో తన వార్షికోత్సవం సందర్భంగా భారతీయులందరికీ 3 నెలల ఉచిత రీఛార్జ్ ఇస్తోంది. కింద ఉన్న లింక్ మీద క్లిక్ చేసి మీ వివరాలు నింపండి, ఈ రోజే ఉచిత రీఛార్జ్ పొందండి. ఈ సందేశాన్ని 20 మంది స్నేహితులకు వాట్సాప్‌లో పంపండి, లేకపోతే మీ నంబర్ బ్లాక్ అవుతుంది. త్వరగా చేయండి, కొన్ని గంటలు మాత్రమే మిగిలి ఉన్నాయి!""",
    "fake/te_02_5g_corona.txt": """అత్యవసర హెచ్చరిక!!! కరోనా వైరస్ 5G టవర్ల వల్లే వ్యాపిస్తుందని వైద్యులు నిర్ధారించారు, కానీ ప్రభుత్వం ఈ నిజాన్ని మీ నుండి దాచిపెడుతోంది. ఈ సందేశాన్ని తొలగించే ముందే మీ కుటుంబ సభ్యులందరికీ వెంటనే పంపండి. ప్రతిరోజూ వేడి నీటిలో పసుపు, నిమ్మరసం కలిపి తాగితే వైరస్ 24 గంటల్లో శరీరం నుండి పోతుంది, ఈ విషయం మీకు ఎవరూ చెప్పరు.""",
}

for rel_path, text in SAMPLES.items():
    path = os.path.join("indian_test", *rel_path.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")

n_real = sum(1 for k in SAMPLES if k.startswith("real/"))
n_fake = sum(1 for k in SAMPLES if k.startswith("fake/"))
print(f"Created {n_real} real and {n_fake} fake sample articles in the 'indian_test' folder.")
