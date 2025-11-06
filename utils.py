import os
import shutil
import logging

logger = logging.getLogger(__name__)


def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def cleanup_old_builds(user_id):
    if not os.path.exists('builds'):
        return
    
    for file in os.listdir('builds'):
        if file.startswith(f'user_{user_id}_') or file.startswith(f'app_{user_id}_'):
            path = os.path.join('builds', file)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                logger.info(f"Cleaned: {path}")
            except Exception as e:
                logger.error(f"Cleanup error {path}: {str(e)}")


def cleanup_session():
    session_files = ['bot_session.session', 'bot_session.session-journal']
    for session_file in session_files:
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                logger.info(f"Removed: {session_file}")
            except Exception as e:
                logger.error(f"Could not remove {session_file}: {str(e)}")
