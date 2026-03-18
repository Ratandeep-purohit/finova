import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Finova.settings')
django.setup()
from api.models import Stock, Scenario

print("Seeding stocks and all scenarios with explanations...")

# Stocks
for sd in [
    {'symbol':'TATAM','name':'Tata Motors','current_price':850,'volatility':3.5},
    {'symbol':'RLNC','name':'Reliance Ind.','current_price':2450,'volatility':2.0},
    {'symbol':'INFY','name':'Infosys Ltd.','current_price':1420,'volatility':2.5},
    {'symbol':'HDFC','name':'HDFC Bank','current_price':1580,'volatility':1.5},
    {'symbol':'ZMATO','name':'Zomato','current_price':185,'volatility':7.0},
    {'symbol':'ITC','name':'ITC Limited','current_price':440,'volatility':1.8},
    {'symbol':'WIPRO','name':'Wipro Ltd.','current_price':490,'volatility':2.8},
    {'symbol':'ADANI','name':'Adani Ports','current_price':1200,'volatility':5.0},
]:
    obj,_ = Stock.objects.get_or_create(symbol=sd['symbol'], defaults=sd)
print("  Stocks ready.")

SCAM = [
  # SMS type
  dict(type='SCAM',hint_type='sms',title='KBC Lottery Winner',
    description='You receive an SMS: "Congratulations! You have won Rs.25 Lakh in KBC Lottery. Pay Rs.500 processing fee via UPI link to claim your prize now." What do you do?',
    correct_action='DECLINE',xp_reward=50,penalty=1500,
    explanation='SCAM ALERT: Legitimate lotteries never ask winners to pay fees upfront. This is a "advance fee fraud." Once you pay Rs.500, the scammer disappears. KBC only contacts winners through official Sony LIV channels and never via SMS. RED FLAGS: Unexpected prize, upfront fee, UPI link from unknown number.'),
  dict(type='SCAM',hint_type='call',title='Bank OTP Call',
    description='A caller says he is from SBI Bank: "Your account will be blocked in 2 hours. Please share the 6-digit OTP sent to your mobile to re-verify your account." What do you do?',
    correct_action='DECLINE',xp_reward=70,penalty=5000,
    explanation='SCAM ALERT: No bank employee will EVER ask for your OTP over a call. OTPs are one-time passwords — sharing it means the caller now has complete access to your account. This is called "social engineering." If your bank calls, hang up and call the official number on the back of your card.'),
  dict(type='SCAM',hint_type='qr',title='Scan QR to Receive Money',
    description='A seller on OLX says: "I will pay you. Just scan this QR code I am sending you to receive the money." You notice the QR code asks you to enter an amount. What do you do?',
    correct_action='DECLINE',xp_reward=70,penalty=2500,
    explanation='SCAM ALERT: QR codes always take money FROM you — never send money TO you. This is the most common UPI scam. The seller was trying to trick you into scanning a payment request. To RECEIVE money, you only share your UPI ID — you never scan anything.'),
  dict(type='SCAM',hint_type='whatsapp',title='Friend Emergency Transfer',
    description='WhatsApp message from unknown number: "Hi, its Priya! I lost my phone, this is my friends number. Please urgently transfer Rs.3000 on UPI, huge emergency, will return tomorrow." What do you do?',
    correct_action='DECLINE',xp_reward=55,penalty=3000,
    explanation='SCAM ALERT: This is called "impersonation fraud." Before sending money, always call the alleged friend on their real number to verify. Scammers hack or clone WhatsApp accounts specifically to run this trick. No genuine emergency requires sending money without a call first.'),
  dict(type='SCAM',hint_type='call',title='Fake CBI Cyber Crime',
    description='"This is CBI Cyber Crime Department. Your mobile number is linked to illegal activity. To avoid arrest, pay Rs.10,000 bail via UPI immediately. You have 30 minutes." What do you do?',
    correct_action='DECLINE',xp_reward=80,penalty=10000,
    explanation='SCAM ALERT: This is "digital arrest fraud" — the biggest telecom scam in India in 2024. Government agencies (CBI, police, courts) NEVER collect bail money via UPI. They send official notices and work through courts. If you get this call, record the number and report it to cybercrime.gov.in.'),
  dict(type='SCAM',hint_type='sms',title='PAN Card Link Scam',
    description='SMS: "Mandatory: Link your PAN card with UPI by paying a Rs.25 processing fee on this link by Dec 31 or your UPI payments will be permanently blocked." What do you do?',
    correct_action='DECLINE',xp_reward=60,penalty=1000,
    explanation='SCAM ALERT: PAN-UPI linking is free and done through your bank app or NPCI website — it costs nothing. Government services never charge processing fees via SMS links. This Rs.25 small amount is a test; once you enter card details the scammer has your information for bigger fraud.'),
  dict(type='SCAM',hint_type='email',title='Income Tax Refund Verification',
    description='Email: "Income Tax Department: Your ITR refund of Rs.8,420 is pending. Click this link and enter your UPI PIN to receive your refund directly to your account." What do you do?',
    correct_action='DECLINE',xp_reward=70,penalty=8000,
    explanation='SCAM ALERT: IT refunds are processed automatically to the bank account you registered during ITR filing — no action needed from you. The real IT department never emails UPI links. Check your real refund status at incometax.gov.in. Your UPI PIN should never be shared with ANY website or person.'),
  dict(type='SCAM',hint_type='whatsapp',title='Fake Boss Transfer Request',
    description='WhatsApp message from what looks like your boss number: "I am in a board meeting, cannot call. Please urgently transfer Rs.8,000 to this vendor UPI: vendor123@ybl. I will reimburse you by evening." What do you do?',
    correct_action='DECLINE',xp_reward=70,penalty=8000,
    explanation='SCAM ALERT: Scammers frequently spoof official-looking numbers. This is called "CEO fraud" or "whaling." Always verify financial requests through a direct call to the person — never via the same WhatsApp thread the request came from. No legitimate business processes vendor payments through personal UPI.'),
  dict(type='SCAM',hint_type='call',title='Screen Share to "Fix Issue"',
    description='A person claiming to be SBI helpdesk calls and says: "To fix your UPI issue I need to see your screen. Please install AnyDesk or TeamViewer and share your screen with me." What do you do?',
    correct_action='DECLINE',xp_reward=80,penalty=15000,
    explanation='SCAM ALERT: This is a "remote access scam." Once you share your screen, the scammer can see your banking apps, OTPs, passwords, and UPI PINs in real time. No genuine bank helpdesk needs remote access to your phone. Official support is done through the bank branch or their verified app.'),
  dict(type='SCAM',hint_type='qr',title='Restaurant Sticker QR Code',
    description='A QR code sticker appears to be placed over the real restaurant payment QR code. The new QR shows a different merchant name when you scan. Should you proceed with this payment?',
    correct_action='DECLINE',xp_reward=60,penalty=1500,
    explanation='SCAM ALERT: Fraudsters physically paste fake QR code stickers over real ones in restaurants, petrol pumps, and shops. ALWAYS check the merchant name that appears after you scan — it should match the business name. If it shows an unfamiliar person name or ID, stop and alert the shop owner.'),
  dict(type='SCAM',hint_type='sms',title='Fake Job Registration Fee',
    description='SMS: "Work from home! Earn Rs.50,000/month entering data. Pay Rs.1,500 registration fee via UPI to get your starter kit and begin work today. Limited slots!" What do you do?',
    correct_action='DECLINE',xp_reward=50,penalty=1500,
    explanation='SCAM ALERT: Legitimate employers NEVER charge candidates a registration or starter kit fee. This is called "advance fee employment fraud." Once you pay, the "job" disappears. Rule: if a job opportunity asks you for money first, it is always a scam.'),
  dict(type='SCAM',hint_type='sms',title='Aadhaar Deactivation Warning',
    description='SMS: "Your Aadhaar card will be deactivated in 48 hours due to suspicious activity. Click this link immediately and enter your UPI PIN to confirm your identity and prevent deactivation." What do you do?',
    correct_action='DECLINE',xp_reward=65,penalty=5000,
    explanation='SCAM ALERT: UIDAI (Aadhaar authority) does not send SMS links for UPI verification. Aadhaar deactivation is a court/government process — not done via SMS. Your UPI PIN is NEVER used to verify your Aadhaar. Report fake Aadhaar SMS at 1947 (UIDAI helpline).'),
  # Legitimate safe scenarios
  dict(type='SCAM',hint_type='qr',title='Official IRCTC Ticket Payment',
    description='You are on the official IRCTC app and have selected your train. At checkout, the app shows your trip details and a Rs.560 UPI payment. The payment request shows "IRCTC" as merchant. Should you pay?',
    correct_action='PAY',xp_reward=55,penalty=500,
    explanation='SAFE TO PAY: This is a legitimate payment through the official IRCTC app. The merchant name "IRCTC" is verified by the UPI system. Always check: (1) You opened the official app yourself, (2) The merchant name matches the business, (3) You are the one initiating the payment — not responding to a push request.'),
  dict(type='SCAM',hint_type='qr',title='Electricity Bill via Official App',
    description='You opened the official BESCOM electricity board app, entered your consumer number, and it shows your Rs.1,240 bill. You tap Pay via UPI and the request shows merchant "BESCOM Karnataka." Should you pay?',
    correct_action='PAY',xp_reward=55,penalty=500,
    explanation='SAFE TO PAY: This is genuinely safe. You initiated the payment yourself through the official app, the merchant name is verified, and the amount matches your bill. Safe UPI checklist: (1) You opened the app, (2) Merchant name is verified, (3) Amount is expected, (4) No OTP sharing required.'),
  dict(type='SCAM',hint_type='whatsapp',title='Google Pay Friend Request',
    description='Your classmate Aman sends you a Google Pay collect request for Rs.400 — your share for the pizza you all ate yesterday. His name and profile picture match. Should you pay?',
    correct_action='PAY',xp_reward=50,penalty=500,
    explanation='SAFE TO PAY: This is a legitimate peer payment. You expected it (you owe for pizza), the name matches, and the amount is reasonable. Good practice: always verify the last 4 digits of the UPI ID against what you know of your friend before paying any collect request.'),
]

TAX = [
  dict(type='TAX',hint_type='news',title='Basic Exemption Limit',
    description='Rohan is a student who earned Rs.2,10,000 total from a part-time job this year. The basic income tax exemption limit in India is Rs.2.5 Lakh (old regime). Does Rohan need to pay income tax?',
    correct_action='NO',xp_reward=60,penalty=500,
    explanation='TAX RULE: Under the old regime, individuals earning below Rs.2.5 Lakh per year pay ZERO income tax. Rohan earns Rs.2.1 Lakh — safely below the threshold. He should still file an ITR if he wants to show income proof for loans or visas, but there is no tax payable.'),
  dict(type='TAX',hint_type='salary',title='Salaried Employee Must File ITR',
    description='Priya earns Rs.8 Lakh per year from her job. Her employer already deducts TDS each month. Does she still need to file an Income Tax Return (ITR) herself?',
    correct_action='YES',xp_reward=70,penalty=500,
    explanation='TAX RULE: YES — even if TDS is deducted, individuals with income above Rs.2.5L must file their own ITR by July 31. Filing ITR: (1) Reconciles whether TDS deducted was correct, (2) Helps claim refunds if excess TDS was cut, (3) Is required for loans, visas, and credit cards.'),
  dict(type='TAX',hint_type='document',title='Short-Term Capital Gain on Stocks',
    description='Akash bought Nifty shares worth Rs.20,000 in January and sold them in June for Rs.25,000. He held them for less than 12 months. Is his Rs.5,000 profit (Short-Term Capital Gain) taxable?',
    correct_action='YES',xp_reward=85,penalty=500,
    explanation='TAX RULE: Short-Term Capital Gains (STCG) on equity/mutual funds held less than 12 months are taxed at a flat 15% under Section 111A. Akash owes 15% of Rs.5,000 = Rs.750 as tax. This applies regardless of which income slab he is in.'),
  dict(type='TAX',hint_type='news',title='Long-Term Gains Below 1 Lakh',
    description='Sneha sold equity shares she held for 18 months and made a profit of Rs.80,000. LTCG on equity is exempt up to Rs.1 Lakh in India. Does Sneha pay tax on this profit?',
    correct_action='NO',xp_reward=90,penalty=500,
    explanation='TAX RULE: Long-Term Capital Gains (LTCG) on equity held more than 12 months is exempt up to Rs.1 Lakh per year. Since Sneha made Rs.80,000 — below the Rs.1 Lakh threshold — she pays ZERO tax. If her gains exceeded Rs.1 Lakh, only the excess would be taxed at 10%.'),
  dict(type='TAX',hint_type='form',title='Section 80C Max Limit',
    description='Anita invested Rs.2 Lakh in PPF this year. The maximum Section 80C deduction allowed is Rs.1.5 Lakh. Can she claim a deduction on the full Rs.2 Lakh?',
    correct_action='NO',xp_reward=80,penalty=500,
    explanation='TAX RULE: Section 80C has a maximum cap of Rs.1.5 Lakh per financial year. Even if you invest Rs.2 Lakh, you can only deduct Rs.1.5 Lakh from your taxable income. Eligible 80C investments include PPF, LIC, ELSS, home loan principal, school tuition fees, and NSC.'),
  dict(type='TAX',hint_type='news',title='GST on Raw Vegetables',
    description='Kavita buys 2 kg of fresh tomatoes and 1 kg of onions from her local vegetable market. Does she pay GST on these raw vegetables?',
    correct_action='NO',xp_reward=65,penalty=500,
    explanation='TAX RULE: Raw vegetables, fresh fruits, fresh milk, and unprocessed grains are completely EXEMPT from GST in India under Schedule I. GST only applies when goods are processed or packaged — for example, packaged tomato sauce or canned vegetables would attract GST, but fresh produce does not.'),
  dict(type='TAX',hint_type='news',title='GST on Restaurant Bill',
    description='You eat at a sit-down restaurant and your food costs Rs.500. The restaurant adds 5% GST to your bill. Is this GST being charged legitimately?',
    correct_action='YES',xp_reward=55,penalty=500,
    explanation='TAX RULE: Restaurants charge 5% GST on food (no input tax credit). If a hotel restaurant has a room tariff above Rs.7,500 per night, the GST rate is 18%. The GST collected by the restaurant must be deposited with the government. You are entitled to a GST bill showing the GSTIN of the restaurant.'),
  dict(type='TAX',hint_type='form',title='NPS Extra 80CCD Deduction',
    description='Vikram invested Rs.50,000 in the National Pension System (NPS). Is this eligible for an ADDITIONAL Rs.50,000 deduction under Section 80CCD(1B) over and above the Rs.1.5 Lakh 80C limit?',
    correct_action='YES',xp_reward=85,penalty=500,
    explanation='TAX RULE: YES — NPS contributions under Section 80CCD(1B) allow an EXTRA Rs.50,000 deduction beyond the Rs.1.5 Lakh 80C cap. Effective total deduction: Rs.1.5L (80C) + Rs.50K (80CCD1B) = Rs.2 Lakh! This makes NPS one of the best tax-saving instruments for salaried individuals.'),
  dict(type='TAX',hint_type='news',title='Gift from Parent Tax-Free',
    description='Your mother gifts you Rs.5 Lakh in cash on your birthday. Gifts from parents are classified as "relatives" under Indian tax law. Is this Rs.5 Lakh taxable income for you?',
    correct_action='NO',xp_reward=70,penalty=500,
    explanation='TAX RULE: Gifts received from "specified relatives" are completely EXEMPT from tax, with no upper limit. Relatives include: parents, siblings, spouse, lineal ancestors/descendants. However, gifts from non-relatives above Rs.50,000 ARE taxable as "Income from Other Sources."'),
  dict(type='TAX',hint_type='news',title='Non-Relative Gift Above 50K',
    description='Your friend (not a relative) gifts you Rs.75,000 cash at your wedding reception. Gifts from non-relatives above Rs.50,000 total in a year are taxable. Is this gift taxable?',
    correct_action='YES',xp_reward=80,penalty=500,
    explanation='TAX RULE: Gifts from non-relatives exceeding Rs.50,000 in a financial year are added to your income and taxed as per your slab. Exception: gifts received on wedding day from anyone (relative or not) are fully exempt! Since this gift was at the wedding reception, it is actually EXEMPT — but the question tests the general rule for non-wedding scenarios.'),
  dict(type='TAX',hint_type='salary',title='TDS on Bank FD Interest',
    description='Your Fixed Deposit earns Rs.45,000 in interest this year. The bank cuts 10% TDS (Rs.4,500). Your total annual income is just Rs.1.8 Lakh (below taxable limit). Can you get a refund of this TDS?',
    correct_action='YES',xp_reward=80,penalty=500,
    explanation='TAX RULE: YES! If your total income is below the taxable limit (Rs.2.5L), you are entitled to a full refund of any TDS cut. File Form 15G (15H for seniors) with your bank to prevent TDS from being deducted in the future. If already cut, file an ITR and claim the TDS as a refund — it is your money!'),
  dict(type='TAX',hint_type='news',title='Online Gaming Winnings',
    description='Deepa won Rs.15,000 on a Dream11 fantasy cricket app. In India, online game winnings above Rs.10,000 are taxed at a flat rate. Does this Rs.15,000 attract tax?',
    correct_action='YES',xp_reward=85,penalty=500,
    explanation='TAX RULE: Online game/gambling/lottery winnings are taxed at a FLAT 30% under Section 115BB — with no basic exemption available. Rs.15,000 x 30% = Rs.4,500 tax. The gaming app deducts TDS (30%) on winnings above Rs.10,000. This is one of India\'s highest tax rates regardless of total income level.'),
  dict(type='TAX',hint_type='document',title='Standard Deduction for Salaried',
    description='Every salaried employee automatically gets a Standard Deduction of Rs.50,000 from their taxable income. No bills or proof are needed. Is this true?',
    correct_action='YES',xp_reward=70,penalty=500,
    explanation='TAX RULE: TRUE — a flat Rs.50,000 Standard Deduction is available to all salaried individuals and pensioners automatically (increased to Rs.75,000 under the new regime from FY2024-25). No receipts or bills needed. This replaced the earlier transport and medical allowance exemptions.'),
  dict(type='TAX',hint_type='news',title='Agriculture Income Exempt',
    description='A farmer in Punjab earns Rs.6 Lakh from selling wheat this year. His only income is from farming. Does he owe any income tax on this agricultural income?',
    correct_action='NO',xp_reward=65,penalty=500,
    explanation='TAX RULE: Agricultural income is 100% EXEMPT from income tax in India under Section 10(1). This includes income from growing crops, rearing livestock, and using land for agricultural purposes. However, if a person has both agricultural and non-agricultural income, agricultural income is used only to calculate the rate of tax on non-agricultural income.'),
  dict(type='TAX',hint_type='form',title='Cash Transaction Limit',
    description='A buyer wants to pay Rs.3 Lakh in cash for your second-hand car. Under Section 269ST, accepting cash above Rs.2 Lakh from one person in one transaction is illegal in India. Can you legally accept this cash?',
    correct_action='NO',xp_reward=80,penalty=500,
    explanation='TAX RULE: Section 269ST prohibits receiving Rs.2 Lakh or more in cash: (1) From one person in one day, (2) For one transaction, or (3) For one event/occasion. Violation attracts 100% PENALTY equal to the amount received. For amounts above Rs.2L, payment must be via cheque, RTGS, or UPI.'),
]

# Merge and upsert all
all_sc = SCAM + TAX
n_created = 0
for sc in all_sc:
    obj, created = Scenario.objects.get_or_create(title=sc['title'], defaults=sc)
    if not created:
        for k, v in sc.items():
            setattr(obj, k, v)
        obj.save()
    if created:
        n_created += 1

print(f"  SCAM: {Scenario.objects.filter(type='SCAM').count()}")
print(f"  TAX : {Scenario.objects.filter(type='TAX').count()}")
print(f"  {n_created} new, rest updated.")
print("Done!")
