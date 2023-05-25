import json
from django.shortcuts import get_object_or_404
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import BroadcastNotification

from celery import Celery, states
from celery.exceptions import Ignore
import asyncio


@shared_task(bind=True,)
def broadcast_notification(self, data):
    try:
        # notification = get_object_or_404(BroadcastNotification, id=data)
        notification = BroadcastNotification.objects.filter(id=int(data))
        if len(notification)>0:
            notification = notification.first()
            channel_layer = get_channel_layer()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(channel_layer.group_send(
                "notification_broadcast",
                {
                    'type': 'send_notification',
                    'message': json.dumps(notification.message)
                }
            ))
            notification.sent = True
            notification.save()
            return 'Done'
        else:
            self.update_state(
                state='FAILURE',
                meta={'exe': "Not Found"}
            )
            raise Ignore()
    except:
        print("faileeeeeeeeeeeeeeeeeeeeed 2")
        self.update_state(
            state='FAILURE',
            meta={
                'exe': "Failed",
                # 'exc_type': type(ex).__name__,
                # 'exc_message': traceback.format_exc().split('\n'),
                # 'custom': '...'
            }
        )
        raise Ignore()

