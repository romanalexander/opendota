from djcelery import celery
from django.core.cache import cache
from dotastats.models import MatchHistoryQueue
from dotastats.json.steamapi import GetMatchDetails, GetMatchHistory
from celery.utils.log import get_task_logger
from django.core.exceptions import ObjectDoesNotExist

LOCK_EXPIRE = 60 * 1

logger = get_task_logger(__name__)

@celery.task(name='tasks.poll_match_history_queue')
def poll_match_history_queue():
    lock_id = "poll_match_history_queue_lock"
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)
    
    try:
        queue_object = MatchHistoryQueue.objects.latest()
    except ObjectDoesNotExist:
        if cache.get(lock_id + 'time') == None:
            GetMatchHistory()
            logger.debug("Ran out of work. Attempting more from history..")
            cache.set(lock_id + 'time', True, 60)
        else:
            logger.debug("No work to be done. Sleeping.")
        return False
    
    if acquire_lock():
        logger.debug("Attempting to retreive match_id: " + str(queue_object.pk))
        try:
            GetMatchDetails(queue_object.pk)
            logger.debug("Retreived and set match_id: " + str(queue_object.pk))
        except:
            logger.debug("Error creating object: " + str(queue_object.pk))
            raise
        finally:
            logger.debug("Lock released.")
            release_lock()
        return True
    return False
