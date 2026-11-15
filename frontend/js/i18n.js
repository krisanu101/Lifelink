// Language switch. Screen text is written in English; BN holds the Bangla version of each sentence.
// t("text") translates a label, tm(message) translates messages that come from the server. Made by Krisanu.
let LANG = 'bn';     // Bangla is the default; people can switch to English at any time
try { LANG = localStorage.getItem('ll_lang') || 'bn'; } catch (e) { /* storage may be blocked */ }

const BN = {
  // navigation and general
  'Home': 'হোম', 'Find blood': 'রক্ত খুঁজুন', 'Request blood': 'রক্ত চাই', 'Donor guide': 'ডোনার গাইড', 'Join': 'যোগ দিন', 'Log in': 'লগইন', 'Log out': 'লগআউট',
  'Dashboard': 'ড্যাশবোর্ড', 'Notifications': 'নোটিফিকেশন', 'Close': 'বন্ধ করুন', 'Made by': 'তৈরি করেছেন', 'LifeLink: Blood Donation Network': 'লাইফলিংক: রক্তদান নেটওয়ার্ক',
  'Safe blood, shared quickly. Always follow the medical screening at the blood centre.': 'নিরাপদ রক্ত, দ্রুত পৌঁছে দেওয়া। রক্ত কেন্দ্রের মেডিকেল পরীক্ষা সবসময় মেনে চলুন।',
  // home
  'Bangladesh blood donation network': 'বাংলাদেশের রক্তদান নেটওয়ার্ক', 'Give blood.': 'রক্ত দিন।', 'Save a life today.': 'আজই একটি জীবন বাঁচান।',
  'LifeLink connects donors, patient families and hospitals. Hospitals verify every request, and your phone number stays private until you agree to help.': 'লাইফলিংক ডোনার, রোগীর পরিবার ও হাসপাতালকে যুক্ত করে। হাসপাতাল প্রতিটি অনুরোধ যাচাই করে, আর আপনি রাজি না হওয়া পর্যন্ত আপনার ফোন নম্বর গোপন থাকে।',
  'Become a donor': 'ডোনার হোন', 'Hospital-verified': 'হাসপাতাল-যাচাইকৃত', 'Phone stays private': 'ফোন নম্বর গোপন', 'Works with SMS': 'SMS-এও কাজ করে',
  'Request verified': 'অনুরোধ যাচাই হয়েছে', 'Donor agreed': 'ডোনার রাজি', 'Blood delivered': 'রক্ত পৌঁছেছে', 'Registered donors': 'নিবন্ধিত ডোনার', 'Donations recorded': 'রেকর্ড করা রক্তদান',
  'Partner hospitals': 'অংশীদার হাসপাতাল', 'Requests fulfilled': 'পূরণ হওয়া অনুরোধ', 'How it works': 'কীভাবে কাজ করে', 'Ask for blood': 'রক্ত চান',
  'Fill in the patient, blood group and hospital. It takes about a minute.': 'রোগী, রক্তের গ্রুপ ও হাসপাতাল লিখুন। প্রায় এক মিনিট লাগে।',
  'Hospital verifies': 'হাসপাতাল যাচাই করে', 'The hospital confirms the request and alerts eligible donors nearby.': 'হাসপাতাল অনুরোধ নিশ্চিত করে এবং কাছের যোগ্য ডোনারদের জানায়।',
  'Donors respond': 'ডোনাররা সাড়া দেন', 'Donors who agree share their contact with you, and the donation is recorded.': 'যে ডোনাররা রাজি হন তাঁরা আপনাকে যোগাযোগের তথ্য দেন, আর রক্তদান রেকর্ড হয়।',
  'Why people trust LifeLink': 'মানুষ কেন লাইফলিংকে ভরসা করে', 'Verified requests': 'যাচাইকৃত অনুরোধ', 'Private by design': 'শুরু থেকেই গোপনীয়তা', 'Smart matching': 'স্মার্ট ম্যাচিং',
  'Live blood stock': 'রক্তের লাইভ স্টক', 'SMS and app alerts': 'SMS ও অ্যাপ অ্যালার্ট', 'Thalassemia care': 'থ্যালাসেমিয়া সেবা',
  'A hospital confirms every request before any donor is contacted, so fake requests never reach you.': 'কোনো ডোনারকে জানানোর আগে হাসপাতাল প্রতিটি অনুরোধ নিশ্চিত করে, তাই ভুয়া অনুরোধ আপনার কাছে পৌঁছায় না।',
  'Your phone number stays hidden until you agree to help with a specific request.': 'নির্দিষ্ট কোনো অনুরোধে সাহায্য করতে রাজি না হওয়া পর্যন্ত আপনার ফোন নম্বর লুকানো থাকে।',
  'Donors are matched by blood group and area, and only people who are eligible today are asked.': 'রক্তের গ্রুপ ও এলাকা মিলিয়ে ডোনার বাছা হয়, আর শুধু আজ যাঁরা রক্ত দিতে যোগ্য তাঁদেরই জানানো হয়।',
  'See which hospitals have blood in stock right now and how long it stays fresh.': 'এখন কোন হাসপাতালে রক্ত আছে এবং কতদিন সতেজ থাকবে তা দেখুন।',
  'Donors get a notification and a text message, so help can arrive even without internet.': 'ডোনাররা নোটিফিকেশন ও টেক্সট মেসেজ পান, তাই ইন্টারনেট ছাড়াও সাহায্য পৌঁছাতে পারে।',
  'Hospitals can plan regular transfusions in advance and keep a group of regular donors.': 'হাসপাতাল আগে থেকেই নিয়মিত রক্তসঞ্চালনের পরিকল্পনা করতে এবং নিয়মিত ডোনারের দল রাখতে পারে।',
  'Who can give blood to whom': 'কে কাকে রক্ত দিতে পারে', 'Each row shows a patient blood group and the donor groups that can safely give to them.': 'প্রতিটি সারিতে রোগীর রক্তের গ্রুপ এবং যে ডোনার গ্রুপগুলো নিরাপদে রক্ত দিতে পারে তা দেখানো হয়েছে।',
  'Patient group': 'রোগীর গ্রুপ', 'Can receive from': 'যাঁদের কাছ থেকে নিতে পারে', 'Ready to help?': 'সাহায্য করতে প্রস্তুত?', 'Register in two minutes and be there when someone needs you.': 'দুই মিনিটে নিবন্ধন করুন, কারও প্রয়োজনে পাশে থাকুন।',
  // find / request
  'Find blood in stock': 'স্টকে থাকা রক্ত খুঁজুন', 'Choose a blood group to see hospitals that have it right now. Always call the hospital before you travel.': 'রক্তের গ্রুপ বেছে নিন, এখন কোন হাসপাতালে আছে দেখুন। যাওয়ার আগে সবসময় হাসপাতালে ফোন করে নিন।',
  'units of {g}': '{g} গ্রুপের ব্যাগ', 'Fresh for about {n} days': 'আরও প্রায় {n} দিন সতেজ', 'No hospital has this blood group in stock right now. Send a request and donors will be alerted.': 'এই গ্রুপের রক্ত এখন কোনো হাসপাতালের স্টকে নেই। অনুরোধ পাঠান, ডোনারদের জানানো হবে।',
  'Patient name': 'রোগীর নাম', 'Blood group': 'রক্তের গ্রুপ', 'Units needed': 'কত ব্যাগ লাগবে', 'Urgency': 'জরুরি অবস্থা', 'Normal': 'সাধারণ', 'Urgent': 'জরুরি', 'Critical': 'অতি জরুরি', 'Hospital': 'হাসপাতাল', 'Area': 'এলাকা',
  'Needed by (optional)': 'কবের মধ্যে লাগবে (ঐচ্ছিক)', 'Contact phone': 'যোগাযোগের ফোন', 'Note (optional)': 'নোট (ঐচ্ছিক)', 'Send request': 'অনুরোধ পাঠান',
  'Request sent and verified.': 'অনুরোধ পাঠানো ও যাচাই হয়েছে।', 'Request sent. The hospital will verify it shortly.': 'অনুরোধ পাঠানো হয়েছে। হাসপাতাল শীঘ্রই যাচাই করবে।',
  'Please log in or create a free account so the hospital can reach you.': 'হাসপাতাল যেন আপনার সাথে যোগাযোগ করতে পারে, তাই লগইন করুন বা বিনামূল্যে অ্যাকাউন্ট খুলুন।', 'Create account': 'অ্যাকাউন্ট খুলুন',
  'The hospital verifies your request first. Then eligible donors are alerted.': 'আগে হাসপাতাল আপনার অনুরোধ যাচাই করবে। তারপর যোগ্য ডোনারদের জানানো হবে।',
  // guide
  'Typical rules are shown here. The doctor at the blood centre makes the final decision.': 'এখানে সাধারণ নিয়ম দেওয়া আছে। চূড়ান্ত সিদ্ধান্ত নেন রক্ত কেন্দ্রের ডাক্তার।', 'Who can donate': 'কারা রক্ত দিতে পারেন',
  'Age {a} to {b} years': 'বয়স {a} থেকে {b} বছর', 'Weight at least {w} kg (some centres accept 45 kg)': 'ওজন কমপক্ষে {w} কেজি (কিছু কেন্দ্রে ৪৫ কেজিও চলে)', 'Feeling healthy, with no fever or infection': 'সুস্থ বোধ করছেন, জ্বর বা সংক্রমণ নেই',
  'About {m} months since your last donation (women: about {f} months)': 'শেষ রক্তদানের পর প্রায় {m} মাস পার (নারীদের ক্ষেত্রে প্রায় {f} মাস)', 'Before you donate': 'রক্ত দেওয়ার আগে', 'After you donate': 'রক্ত দেওয়ার পরে', 'Common questions': 'সাধারণ প্রশ্ন',
  'Eat a healthy meal and do not donate on an empty stomach.': 'পুষ্টিকর খাবার খান, খালি পেটে রক্ত দেবেন না।', 'Drink plenty of water.': 'প্রচুর পানি পান করুন।', 'Sleep well the night before.': 'আগের রাতে ভালো ঘুমান।', 'Bring a photo ID if you have one.': 'ছবিসহ পরিচয়পত্র থাকলে সঙ্গে আনুন।',
  'Rest for 10 to 15 minutes and have a snack.': '১০ থেকে ১৫ মিনিট বিশ্রাম নিন এবং হালকা কিছু খান।', 'Drink extra fluids for the rest of the day.': 'দিনের বাকি সময় বেশি করে তরল পান করুন।', 'Avoid heavy exercise until the next day.': 'পরের দিন পর্যন্ত ভারী ব্যায়াম এড়িয়ে চলুন।', 'Keep the bandage on for a few hours.': 'কয়েক ঘণ্টা ব্যান্ডেজ রেখে দিন।',
  'Does donating blood make me weak?': 'রক্ত দিলে কি দুর্বল হয়ে যাব?', 'Most healthy donors feel fine. Drink water, eat well and rest a little afterwards.': 'সুস্থ ডোনারদের বেশিরভাগই ভালো থাকেন। পানি পান করুন, ভালো খান ও একটু বিশ্রাম নিন।',
  'How much blood is taken?': 'কতটুকু রক্ত নেওয়া হয়?', 'A standard donation is about one bag (350 to 450 ml), and the body replaces it over the following weeks.': 'একবারে প্রায় এক ব্যাগ (৩৫০ থেকে ৪৫০ মিলি) নেওয়া হয়, পরের কয়েক সপ্তাহে শরীর তা পূরণ করে নেয়।',
  'Is it safe?': 'এটা কি নিরাপদ?', 'Yes. New sterile equipment is used for each donor, and a doctor checks you first.': 'হ্যাঁ। প্রতিজন ডোনারের জন্য নতুন জীবাণুমুক্ত সরঞ্জাম ব্যবহার হয়, আর আগে ডাক্তার আপনাকে পরীক্ষা করেন।',
  'Will my blood be tested?': 'আমার রক্ত কি পরীক্ষা করা হবে?', 'Yes. Donated blood is tested for infections such as hepatitis B and C, HIV, syphilis and malaria.': 'হ্যাঁ। দান করা রক্ত হেপাটাইটিস বি ও সি, এইচআইভি, সিফিলিস ও ম্যালেরিয়ার মতো সংক্রমণের জন্য পরীক্ষা করা হয়।',
  'Can I be paid for blood?': 'রক্তের জন্য কি টাকা পাওয়া যায়?', 'No. Paid donation is discouraged because it can make blood less safe. LifeLink is for voluntary donors only.': 'না। টাকার বিনিময়ে রক্তদান নিরুৎসাহিত করা হয় কারণ এতে রক্ত কম নিরাপদ হতে পারে। লাইফলিংক শুধু স্বেচ্ছাসেবী ডোনারদের জন্য।',
  // auth
  'Welcome back': 'আবার স্বাগতম', 'Email': 'ইমেইল', 'Password': 'পাসওয়ার্ড', 'New here?': 'নতুন?', 'Create an account': 'অ্যাকাউন্ট খুলুন', 'Create your account': 'আপনার অ্যাকাউন্ট খুলুন',
  'Blood donor': 'রক্তদাতা', 'Patient family': 'রোগীর পরিবার', 'Hospital staff': 'হাসপাতাল কর্মী', 'Give blood and get alerts when someone nearby needs you.': 'রক্ত দিন এবং কাছে কারও দরকার হলে অ্যালার্ট পান।', 'Ask for blood for a patient.': 'রোগীর জন্য রক্ত চান।',
  'Verify requests and manage stock (needs admin approval).': 'অনুরোধ যাচাই ও স্টক পরিচালনা করুন (অ্যাডমিনের অনুমোদন লাগবে)।', 'Your hospital': 'আপনার হাসপাতাল', 'My hospital is not listed': 'আমার হাসপাতাল তালিকায় নেই', 'Hospital name': 'হাসপাতালের নাম', 'Hospital area': 'হাসপাতালের এলাকা',
  'Gender': 'লিঙ্গ', 'Male': 'পুরুষ', 'Female': 'নারী', 'Date of birth': 'জন্ম তারিখ', 'Weight (kg)': 'ওজন (কেজি)', 'Last donation (leave empty if never)': 'শেষ রক্তদান (কখনো না দিলে ফাঁকা রাখুন)', 'Health check: tick any that apply to you': 'স্বাস্থ্য পরীক্ষা: যেগুলো আপনার ক্ষেত্রে সত্য তাতে টিক দিন',
  'Tattoo, piercing or surgery in the last 6 months': 'গত ৬ মাসে ট্যাটু, নাক-কান ফোঁড়ানো বা অস্ত্রোপচার', 'Fever or infection right now': 'এখন জ্বর বা সংক্রমণ আছে', 'Pregnant or breastfeeding': 'গর্ভবতী বা বুকের দুধ খাওয়াচ্ছেন', 'History of hepatitis B or C, or HIV': 'হেপাটাইটিস বি/সি বা এইচআইভির ইতিহাস',
  'I agree that my phone number is shown only to a requester after I accept their request.': 'আমি রাজি যে আমি অনুরোধ গ্রহণ করলে তবেই আমার ফোন নম্বর অনুরোধকারীকে দেখানো হবে।', 'Full name': 'পুরো নাম', 'Phone': 'ফোন', 'Password (8+ characters)': 'পাসওয়ার্ড (৮+ অক্ষর)',
  'Account created. An administrator will approve it soon.': 'অ্যাকাউন্ট খোলা হয়েছে। অ্যাডমিন শীঘ্রই অনুমোদন দেবেন।', 'Welcome to LifeLink!': 'লাইফলিংকে স্বাগতম!', 'No notifications yet.': 'এখনো কোনো নোটিফিকেশন নেই।',
  // dashboards: common
  'Request': 'অনুরোধ', 'Requests': 'অনুরোধ', 'Details': 'বিস্তারিত', 'Close request': 'অনুরোধ বন্ধ করুন', 'Request closed.': 'অনুরোধ বন্ধ করা হয়েছে।', '{n} of {m} units received': '{m} ব্যাগের মধ্যে {n} ব্যাগ পাওয়া গেছে', '{n} donor(s) agreed': '{n} জন ডোনার রাজি', '{n} unit(s)': '{n} ব্যাগ',
  'Donors': 'ডোনার', 'Phone numbers appear only after a donor accepts, and each view is recorded.': 'ডোনার রাজি হলেই ফোন নম্বর দেখা যায়, আর প্রতিটি দেখা রেকর্ড হয়।', 'No donors have been alerted yet.': 'এখনো কোনো ডোনারকে জানানো হয়নি।', 'You have not made any requests yet.': 'আপনি এখনো কোনো অনুরোধ করেননি।',
  'Hello, {name}': 'হ্যালো, {name}', 'Your blood requests': 'আপনার রক্তের অনুরোধ', 'New request': 'নতুন অনুরোধ',
  // donor
  'You can donate today': 'আপনি আজ রক্ত দিতে পারবেন', 'Thank you for being ready to help.': 'সাহায্য করতে প্রস্তুত থাকার জন্য ধন্যবাদ।', 'Not available to donate yet': 'এখনো রক্ত দেওয়া সম্ভব নয়', 'donations recorded': 'রক্তদান রেকর্ড করা হয়েছে', 'Next donation possible on {d}': 'পরবর্তী রক্তদান সম্ভব: {d}',
  'Available for requests': 'অনুরোধের জন্য উপলব্ধ', '{n} years': '{n} বছর', 'Requests for me': 'আমার জন্য অনুরোধ', 'My donations': 'আমার রক্তদান', 'My requests': 'আমার অনুরোধ', 'needed at {h}': '{h}-এ দরকার', 'I can help': 'আমি সাহায্য করতে পারি', 'Not now': 'এখন না',
  'No requests for you right now. We will alert you here and by SMS.': 'এই মুহূর্তে আপনার জন্য কোনো অনুরোধ নেই। আমরা এখানে ও SMS-এ জানাব।', 'Your donations will appear here after a hospital records them.': 'হাসপাতাল রেকর্ড করলে আপনার রক্তদান এখানে দেখা যাবে।', 'View': 'দেখুন',
  'You are available for requests.': 'আপনি এখন অনুরোধের জন্য উপলব্ধ।', 'You will not receive new requests.': 'আপনি আর নতুন অনুরোধ পাবেন না।', 'Thank you! The requester can now contact you.': 'ধন্যবাদ! অনুরোধকারী এখন আপনার সাথে যোগাযোগ করতে পারবেন।', 'Noted.': 'ঠিক আছে।',
  'Certificate of appreciation': 'প্রশংসাপত্র', 'donated blood at {h} on {d} and helped save lives.': '{d} তারিখে {h}-এ রক্ত দিয়ে জীবন বাঁচাতে সাহায্য করেছেন।', 'Print': 'প্রিন্ট',
  // hospital
  'Hospital dashboard': 'হাসপাতাল ড্যাশবোর্ড', 'Stock': 'স্টক', 'Record donation': 'রক্তদান রেকর্ড', 'Thalassemia': 'থ্যালাসেমিয়া', 'Verify': 'যাচাই করুন', 'Reject': 'বাতিল করুন', 'Alert top donors': 'সেরা ডোনারদের জানান', 'Matches': 'মিল থাকা ডোনার', 'Issue from stock': 'স্টক থেকে দিন',
  '{a} alerted, {b} agreed': '{a} জনকে জানানো হয়েছে, {b} জন রাজি', '{n} donor(s) alerted.': '{n} জন ডোনারকে জানানো হয়েছে।', 'Blood issued from stock.': 'স্টক থেকে রক্ত দেওয়া হয়েছে।', 'Request verified.': 'অনুরোধ যাচাই হয়েছে।', 'Request rejected.': 'অনুরোধ বাতিল হয়েছে।',
  'No requests for your hospital yet.': 'আপনার হাসপাতালের জন্য এখনো কোনো অনুরোধ নেই।', 'Eligible donors': 'যোগ্য ডোনার', 'No eligible donors found.': 'কোনো যোগ্য ডোনার পাওয়া যায়নি।', 'Phone numbers are hidden until a donor accepts.': 'ডোনার রাজি না হওয়া পর্যন্ত ফোন নম্বর লুকানো থাকে।',
  'Under 5 units is a shortage. Under 4 days to expiry is a warning.': '৫ ব্যাগের কম হলে ঘাটতি। মেয়াদ ৪ দিনের কম থাকলে সতর্কতা।', '{n} days': '{n} দিন', 'Record a donation made at your hospital. This updates the donor, the stock and the request.': 'আপনার হাসপাতালে হওয়া রক্তদান রেকর্ড করুন। এতে ডোনার, স্টক ও অনুরোধ হালনাগাদ হবে।',
  'Donor ID': 'ডোনার আইডি', 'See the ID in Matches': 'আইডি দেখতে "মিল থাকা ডোনার" দেখুন', 'Units': 'ব্যাগ', 'Request number (optional)': 'অনুরোধ নম্বর (ঐচ্ছিক)', 'Donation recorded.': 'রক্তদান রেকর্ড হয়েছে।',
  'Next transfusion: {d}': 'পরবর্তী রক্তসঞ্চালন: {d}', 'every {n} weeks': 'প্রতি {n} সপ্তাহে', 'Regular donors': 'নিয়মিত ডোনার', 'Mark transfusion done': 'রক্তসঞ্চালন সম্পন্ন', 'No regular patients yet.': 'এখনো কোনো নিয়মিত রোগী নেই।', 'Add a regular patient': 'নিয়মিত রোগী যোগ করুন',
  'Next transfusion date': 'পরবর্তী রক্তসঞ্চালনের তারিখ', 'Repeat every (weeks)': 'প্রতি কত সপ্তাহে (সপ্তাহ)', 'Add patient': 'রোগী যোগ করুন', 'Next date updated.': 'পরবর্তী তারিখ হালনাগাদ হয়েছে।', 'New request': 'নতুন অনুরোধ',
  // admin
  'Admin dashboard': 'অ্যাডমিন ড্যাশবোর্ড', 'Approvals': 'অনুমোদন', 'Users': 'ব্যবহারকারী', 'Reports': 'রিপোর্ট', 'Audit log': 'অডিট লগ', 'SMS log': 'SMS লগ', 'Approve': 'অনুমোদন দিন', 'Account approved.': 'অ্যাকাউন্ট অনুমোদিত হয়েছে।', 'Nothing is waiting for approval.': 'অনুমোদনের অপেক্ষায় কিছু নেই।',
  'Blood still needed': 'এখনো যত রক্ত দরকার', 'Blood in stock': 'স্টকে থাকা রক্ত', 'Requests by status': 'অবস্থা অনুযায়ী অনুরোধ', 'Donations by month': 'মাস অনুযায়ী রক্তদান', 'No donations yet.': 'এখনো কোনো রক্তদান নেই।', 'SMS messages are simulated and only stored here.': 'SMS বার্তা সিমুলেটেড, শুধু এখানে জমা থাকে।',
  // table headers and labels
  'Date': 'তারিখ', 'Certificate': 'সনদ', 'ID': 'আইডি', 'Donor': 'ডোনার', 'Group': 'গ্রুপ', 'Status': 'অবস্থা', 'Expiry': 'মেয়াদ', 'Change': 'পরিবর্তন', 'Name': 'নাম', 'Role': 'ভূমিকা', 'When': 'কখন', 'Who': 'কে', 'Action': 'কাজ', 'Detail': 'বিবরণ', 'Message': 'বার্তা',
  'Pending': 'অপেক্ষমাণ', 'Verified': 'যাচাইকৃত', 'Fulfilled': 'পূরণ হয়েছে', 'Rejected': 'বাতিল', 'Closed': 'বন্ধ', 'Asked': 'জানানো হয়েছে', 'Accepted': 'রাজি', 'Declined': 'রাজি নন', 'Donated': 'রক্ত দিয়েছেন', 'Shortage': 'ঘাটতি', 'OK': 'ঠিক আছে', 'Expiring soon': 'মেয়াদ শেষ হচ্ছে',
  'Admin': 'অ্যাডমিন', 'Requester': 'অনুরোধকারী', 'Something went wrong.': 'কিছু একটা ভুল হয়েছে।',
  // areas
  'Dhanmondi': 'ধানমন্ডি', 'Mirpur': 'মিরপুর', 'Uttara': 'উত্তরা', 'Mohammadpur': 'মোহাম্মদপুর', 'Gulshan': 'গুলশান', 'Banani': 'বনানী', 'Motijheel': 'মতিঝিল', 'Jatrabari': 'যাত্রাবাড়ী', 'Savar': 'সাভার', 'Narayanganj': 'নারায়ণগঞ্জ', 'Gazipur': 'গাজীপুর', 'Chattogram': 'চট্টগ্রাম', 'Sylhet': 'সিলেট', 'Rajshahi': 'রাজশাহী', 'Khulna': 'খুলনা',
  // messages from the server
  'Choose an account type.': 'অ্যাকাউন্টের ধরন বেছে নিন।', 'Enter a valid email address.': 'সঠিক ইমেইল ঠিকানা দিন।', 'Password must be at least 8 characters.': 'পাসওয়ার্ড কমপক্ষে ৮ অক্ষরের হতে হবে।', 'This email is already registered.': 'এই ইমেইল আগেই নিবন্ধিত।', 'Check blood group and gender.': 'রক্তের গ্রুপ ও লিঙ্গ দেখে নিন।',
  'Hospital not found.': 'হাসপাতাল পাওয়া যায়নি।', 'Wrong email or password.': 'ইমেইল বা পাসওয়ার্ড ভুল।', 'Your account is waiting for admin approval.': 'আপনার অ্যাকাউন্ট অ্যাডমিনের অনুমোদনের অপেক্ষায় আছে।', 'Please log in first.': 'আগে লগইন করুন।', 'You do not have access to this.': 'এটি দেখার অনুমতি আপনার নেই।', 'Not found': 'পাওয়া যায়নি',
  'Choose a blood group.': 'রক্তের গ্রুপ বেছে নিন।', 'Units must be between 1 and 10.': 'ব্যাগের সংখ্যা ১ থেকে ১০-এর মধ্যে হতে হবে।', 'Choose an urgency level.': 'জরুরি অবস্থার মাত্রা বেছে নিন।', 'Request not found.': 'অনুরোধ পাওয়া যায়নি।', 'There is nothing to answer for this request.': 'এই অনুরোধে উত্তর দেওয়ার কিছু নেই।',
  'Verify the request first.': 'আগে অনুরোধ যাচাই করুন।', 'Not enough stock.': 'স্টকে যথেষ্ট রক্ত নেই।', 'Donor not found.': 'ডোনার পাওয়া যায়নি।', 'User not found.': 'ব্যবহারকারী পাওয়া যায়নি।', 'Patient not found.': 'রোগী পাওয়া যায়নি।', 'Bad request.': 'অনুরোধটি ঠিক নয়।', 'Something went wrong on the server.': 'সার্ভারে সমস্যা হয়েছে।',
  'Your health answers show a risk, please see a doctor first': 'আপনার স্বাস্থ্যের উত্তরে ঝুঁকি দেখা যাচ্ছে, আগে ডাক্তার দেখান', 'Privacy consent is required': 'গোপনীয়তা সম্মতি দিতে হবে', 'Enter a valid date of birth': 'সঠিক জন্ম তারিখ দিন'
};

const FIELDS = { name: 'নাম', email: 'ইমেইল', phone: 'ফোন', password: 'পাসওয়ার্ড', blood_group: 'রক্তের গ্রুপ', gender: 'লিঙ্গ', birth_date: 'জন্ম তারিখ', weight: 'ওজন', area: 'এলাকা', patient_name: 'রোগীর নাম', units: 'ব্যাগ', hospital_id: 'হাসপাতাল', donor_id: 'ডোনার আইডি', request_id: 'অনুরোধ নম্বর', delta: 'পরিবর্তন', frequency_weeks: 'সপ্তাহ', next_date: 'তারিখ', new_hospital_name: 'হাসপাতালের নাম', new_hospital_area: 'হাসপাতালের এলাকা' };

// Messages with numbers or names inside.
const BN_RX = [
  [/^Age must be between (\d+) and (\d+)$/, m => 'বয়স ' + m[1] + ' থেকে ' + m[2] + ' বছরের মধ্যে হতে হবে'],
  [/^Weight must be at least (\d+) kg$/, m => 'ওজন কমপক্ষে ' + m[1] + ' কেজি হতে হবে'],
  [/^Next donation possible on (.+)$/, m => 'পরবর্তী রক্তদান সম্ভব: ' + m[1]],
  [/^Please fill in: (.+)$/, m => 'পূরণ করুন: ' + m[1].split(', ').map(f => FIELDS[f] || f).join(', ')],
  [/^You cannot register as a donor right now: (.+)$/, m => 'এখন ডোনার হিসেবে নিবন্ধন করা যাবে না: ' + tm(m[1])],
  [/^You cannot donate right now: (.+)$/, m => 'এখন রক্ত দেওয়া সম্ভব নয়: ' + tm(m[1])],
  [/^This donor cannot donate today: (.+)$/, m => 'এই ডোনার আজ রক্ত দিতে পারবেন না: ' + tm(m[1])],
  [/^New (\w+) request #(\d+): (\S+), (\d+) unit\(s\)\.$/, m => 'নতুন ' + t(cap(m[1])) + ' অনুরোধ #' + m[2] + ': ' + m[3] + ', ' + m[4] + ' ব্যাগ।'],
  [/^Your request #(\d+) was (verified|rejected) by the hospital\.$/, m => 'আপনার অনুরোধ #' + m[1] + ' হাসপাতাল ' + (m[2] === 'verified' ? 'যাচাই করেছে।' : 'বাতিল করেছে।')],
  [/^A donor agreed to help with request #(\d+) \((\S+)\)\. Open the request to see contact details\.$/, m => 'একজন ডোনার অনুরোধ #' + m[1] + ' (' + m[2] + ')-এ সাহায্য করতে রাজি হয়েছেন। যোগাযোগের তথ্য দেখতে অনুরোধটি খুলুন।'],
  [/^A donor accepted request #(\d+)\.$/, m => 'একজন ডোনার অনুরোধ #' + m[1] + ' গ্রহণ করেছেন।'],
  [/^(\S+) blood is needed at (.+) \((\d+) unit\(s\), (\w+)\)\. Please log in to LifeLink to answer\.$/, m => m[2] + '-এ ' + m[1] + ' রক্ত দরকার (' + m[3] + ' ব্যাগ, ' + t(cap(m[4])) + ')। উত্তর দিতে লাইফলিংকে লগইন করুন।'],
  [/^Good news: request #(\d+) has received all the blood it needed\.$/, m => 'সুখবর: অনুরোধ #' + m[1] + ' প্রয়োজনীয় সব রক্ত পেয়েছে।'],
  [/^Thank you for donating blood today\. Your certificate is ready in your dashboard\.$/, () => 'আজ রক্ত দেওয়ার জন্য ধন্যবাদ। আপনার সনদ ড্যাশবোর্ডে প্রস্তুত।'],
  [/^Your account was approved\. You can now use the hospital tools\.$/, () => 'আপনার অ্যাকাউন্ট অনুমোদিত হয়েছে। এখন হাসপাতালের টুল ব্যবহার করতে পারবেন।'],
  [/^New hospital staff account waiting for approval: (.+)$/, m => 'হাসপাতাল কর্মীর নতুন অ্যাকাউন্ট অনুমোদনের অপেক্ষায়: ' + m[1]]
];

// t("text", {name: value}) translates a label and fills in {name} placeholders.
function t(text, vars) {
  let out = (LANG === 'bn' && BN[text]) || text;
  if (vars) for (const key in vars) out = out.split('{' + key + '}').join(vars[key]);
  return out;
}

// tm(message) translates a message that came from the server (it may contain numbers or several parts).
function tm(message) {
  if (LANG !== 'bn' || !message) return message;
  for (const [pattern, build] of BN_RX) { const match = message.match(pattern); if (match) return build(match); }
  if (message.indexOf('; ') > -1) return message.split('; ').map(tm).join('; ');
  return BN[message] || message;
}
