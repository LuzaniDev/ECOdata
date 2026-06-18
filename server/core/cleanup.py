import os


def cleanup_old_files(output_dir: str, days: int = 7):
    import time

    if not os.path.exists(output_dir):
        return 0

    cutoff = time.time() - (days * 86400)
    deleted = 0

    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        if os.path.isfile(filepath):
            if os.path.getmtime(filepath) < cutoff:
                os.remove(filepath)
                deleted += 1

    return deleted