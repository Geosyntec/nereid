import celery


def wait_a_sec_and_see_if_we_can_return_some_data(task, timeout=0.2):
    result = None
    try:
        result = task.get(timeout=timeout)
    except celery.exceptions.TimeoutError:
        pass

    return result
