import traceback
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from djcelery import celery
from dotastats.models import MatchHistoryQueue, MatchDetails, SteamPlayer
from dotastats.json.steamapi import GetMatchDetails, GetMatchHistory, GetPlayerNames
from celery.utils.log import get_task_logger

MATCH_FRESHNESS = settings.DOTA_MATCH_REFRESH

LOCK_EXPIRE = 20 * 1

logger = get_task_logger(__name__)

@celery.task(name='tasks.poll_steamplayers_queue')
def poll_steamplayers_queue():
    """Celery task that handles the constant background refreshing of SteamPlayers.
    
    This task will take up to 100 old SteamPlayers and update them.
    
    Returns True if work was handled; None if no work to be done.
    """
    account_list = []
    accounts = SteamPlayer.get_refresh()
    for account in accounts:
        account_list.append(account.pk)
    if len(account_list) > 0:
        GetPlayerNames(account_list)
        return True
    return None

@celery.task(name='tasks.poll_match_history_queue')
def poll_match_history_queue():
    """Celery task that handles the constant background loading of matches.
    
    This task will first empty the MatchHistoryQueue, or look for more matches if nothing in queue.
    
    If there is no work at all, it will refresh old MatchDetails according to staleness.
    
    Returns True if work was handled; False if there was an error; None if no work to be done.
    """
    lock_id = "poll_match_history_queue_lock"
    success_value = True
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
                success_value = None
        except Exception, e:
            success_value = False
            logger.error(traceback.format_exc())
            logger.error("Error creating object.")
        finally:
            logger.debug("Lock released.")
            release_lock()
    return success_value
