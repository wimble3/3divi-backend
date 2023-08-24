after_video_upload_views_funcs = []


def after_video_upload_views(func):
    """Decorator that registers function like event.
    Functions are called video has been uploaded to s3.

    Args:
        func (collections.abc.Callable): Registered function.

    Returns:
        collections.abc.Callable: Initial function without changes.

    """
    if callable(func):
        after_video_upload_views_funcs.append(func)
        return func


def process_after_video_upload_views(filepath):
    """Actions after video has been uploaded.
    Args:
        filepath (dict): filepath

    Returns:
        None:
    """
    for func in after_video_upload_views_funcs:
        if callable(func):
            func(filepath)
