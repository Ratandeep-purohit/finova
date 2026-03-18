from api.models import Scenario

for s in Scenario.objects.all():
    if not s.explanation:
        if s.type == 'SCAM':
            if s.correct_action == 'DECLINE':
                s.explanation = "This was a scam! Scammers create fake urgency or impersonate authorities like banks/police to steal your money. Never share your OTP, click unverified links, or enter your UPI PIN to receive money."
            else:
                s.explanation = "This was a legitimate message. Official bank statements or authorized verified merchants communicate clearly without asking for your sensitive passwords or OTPs directly in a link."
        elif s.type == 'TAX':
            s.explanation = "Tax regulations update frequently. It is important to know which regime (Old vs New) benefits your specific income bracket and exactly which deductions (like 80C) apply to you."
        s.save()
print('Explanations updated successfully!')
