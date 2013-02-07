import traceback
from djcelery import celery
from django.core.cache import cache
from dotastats.models import MatchHistoryQueue, MatchDetails
from dotastats.json.steamapi import GetMatchDetails, GetMatchHistory
from celery.utils.log import get_task_logger
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

MATCH_FRESHNESS = settings.DOTA_MATCH_REFRESH

LOCK_EXPIRE = 20 * 1

logger = get_task_logger(__name__)

@celery.task(name='tasks.poll_match_history_queue')
def poll_match_history_queue():
    lock_id = "poll_match_history_queue_lock"
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)
    
    if acquire_lock():
        logger.debug("Queue locked.")
        queue_object = None
        force_refresh = False
        try:
            if cache.get(lock_id + '_time') == None:
                GetMatchHistory()
                logger.debug("Ran out of work. Attempting more from history..")
                cache.set(lock_id + '_time', True, LOCK_EXPIRE)
            else:
                try:
                    queue_object = MatchHistoryQueue.objects.latest()
                    logger.debug("Got work from MatchHistoryQueue")
                except ObjectDoesNotExist:
                    queue_object = None
                if queue_object == None:
                        queue_object = MatchDetails.get_refresh()
                        if queue_object:
                            force_refresh = True
                            logger.debug("Got work from stale MatchDetails.")
            if queue_object:
                logger.debug("Attempting to retreive match_id: " + str(queue_object.pk))
                GetMatchDetails(queue_object.pk, force_refresh=force_refresh)
                logger.debug("Retreived and set match_id: " + str(queue_object.pk))
            else:
                logger.debug("No work to be done. Sleeping.")
        except Exception, e:
            logger.error(traceback.format_exc())
            logger.error("Error creating object: " + str(queue_object.pk))
        finally:
            logger.debug("Lock released.")
            release_lock()
            return True
    return False
