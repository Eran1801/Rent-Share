from enum import Enum
import os
from django.utils.safestring import mark_safe

EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_SERVER = os.environ.get('EMAIL_SERVER')
FROM_EMAIL = os.environ.get('COMPANY_EMAIL')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

class Messages(Enum):
    MESSAGE_0 = (
        "שלום %s \n"
        "חוות הדעת שלך התקבלה אצלנו וממתינה לאישור.\n"
        "הודעה נוספת תישלח אלייך במידה וחוות הדעת תאושר.\n"
        "תוכל גם להתעדכן בסטטוס שלה באיזור \"הדירות שלי.\""
    )

    MESSAGE_1 = (
        "שלום %s \n"
        "חוות הדעת שלך אושרה.\n"
        "תודה רבה על תרומתך לקהילה.\n"
        "עכשיו תוכל למצוא אותה באזור חיפוש הדירות."
    )

    MESSAGE_2 = (
        "שלום %s \n"
        "זיהינו אי התאמה בין פרטי הדירה (עיר / רחוב / מספר בניין / דירה) לבין חוזה השכירות.\n"
        "אנא הוסף שנית את חוות הדעת עם הפרטים הנכונים."
    )

    MESSAGE_3 = (
        "שלום %s \n"
        "זיהינו אי התאמה בין תאריכי הכניסה והיציאה שהזנת לבין מה שרשום בחוזה השכירות.\n"
        "אנא הגש את חוות הדעת מחדש עם הפרטים הנכונים."
    )

    MESSAGE_4 = (
        "שלום %s \n"
        "זיהינו אי התאמה בין העלאת הטופס אשר עוזר לנו לאמת שאכן השכרת את הדירה (חוזה שכירות).\n"
        "אנא הגש שוב את חוות הדעת מחדש עם הפרטים הנכונים."
    )

    MESSAGE_5 = (
        "שלום %s \n"
        "זיהינו אי התאמה בין הפרטים בתעודה מזהה שהועלתה בחוות הדעת לבין חוזה השכירות.\n"
        "אנא הגש שוב את חוות הדעת מחדש עם הפרטים הנכונים."
    )

    MESSAGE_6 = (
        "שלום %s \n"
        "זיהינו שפה לא נאותה במתן חוות הדעת שלך.\n"
        "אנא היכנס ל\"דירות שלי\" ועדכן את חוות הדעת על ידי שינוי המלל בתיבת הטקסט ולחיצה על כפתור \"עדכן חוות דעת\"."
    )


    def __str__(self):
        return self.value
    
class Emails(Enum):
    
    FORGET_PASSWORD_SUBJECT = "איפוס סיסמא"
    
    # send email to the company email that a new post was added
    NEW_POST_SEND_TO_ADMIN = f"""
    <html>
        <body>
            <p>New post was added to S3.</p>
            <p>User: %s </p>
        </body>
    </html>
    """
    
    FORGET_PASSWORD_MESSAGE = mark_safe(f"""
    <html>
        <body>
            <p dir="rtl">שלום רב, אימייל זה נשלח מכיוון שרצית לאפס את הסיסמה שלך</p>
            <p dir="rtl">קוד האימות שלך הוא: <b> %s </b><br>
                הקוד תקף ל-5 דקות.
            </p>
        </body>
    </html>
    """)
