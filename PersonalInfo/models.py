from django.db import models
from Users.models import Users

# Create your models here.

class Messages(models.Model):
    user_id = models.CharField(max_length=50, primary_key=True,null=False,blank=False)
    user_message_1 = models.CharField(max_length=200, default="")
    user_message_2 = models.CharField(max_length=200,default="")
    user_message_3 = models.CharField(max_length=200,default="")
    user_message_4 = models.CharField(max_length=200,default="")
    user_message_5 = models.CharField(max_length=200,default="")
    user_message_6 = models.CharField(max_length=200,default="")

'''
מה בעצם הולך להתבצע
המשתמש הולך להגיע לתפריט
בתפריט הוא בוחר את האופציה של ההודעות שלי
ברגע שהוא לוחץ על הכפתור 
תפעל פונקציה שהולכת לעבור על מסד הנתונים של ההודעות ולשלוף משם רק את ההודעות 
שקשורות לאותו משתמש שמחובר

צריך שיהיה טריגר עבור המשתנה של הסטטוס
כל פעם שהוא משתנה יש להפעיל פונקציה שתעדכן את הטבלה של ההודעות
כלומר מוסיף ערך חדש לטבלה של ההודעות
נגיד אם המשתנה סטטוס משתנה ל-1 אז צריך להוסיף ערך חדש לטבלה של ההודעות
וככה גם עבור כל סטטוס אחר


'''