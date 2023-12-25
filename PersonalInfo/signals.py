from django.db.models.signals import post_save
from django.dispatch import receiver
from Posts.models import Post
from .models import Inbox
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@receiver(post_save, sender=Post) # sender it from where the change will be made
def confirmation_status_update(sender, instance, created, **kwargs):

    from PersonalInfo.views import confirmation_status_messages_dict, adding_message_to_inbox

    if created is False:
        # returns a dictionary of fields that have changed since the model was last saved
        changed_fields = instance.get_dirty_fields()
        logger.info(f'Changed fields: {changed_fields}')

        if 'confirmation_status' in changed_fields:
            # get the user that made the change in the database
            user = Inbox.objects.get(user_id = instance.post_user_id)
            logger.info(f'User:{user}')

            # get the confirmation status of the post
            confirmation_status = changed_fields.get('confirmation_status')
            logger.info(f'Confirmation status: {confirmation_status}')

            message = confirmation_status_messages_dict(user.user_id).get(confirmation_status)
            logger.info(f'Message: {message}')

            message_field = f'user_message_{confirmation_status+1}'
            adding_message_to_inbox(user.user_id,message,message_field)
