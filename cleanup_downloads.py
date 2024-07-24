import os
import schedule
import time


def cleanup_downloads():
    downloads_dir = 'downloads'
    current_time = time.time()

    for filename in os.listdir(downloads_dir):
        file_path = os.path.join(downloads_dir, filename)
        try:
            if os.path.isfile(file_path):
                # Check the file's age
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > 86400:  # 24 hours = 86400 seconds
                    os.unlink(file_path)
                    print(f'Deleted {file_path}')
            elif os.path.islink(file_path):
                os.unlink(file_path)
                print(f'Deleted symlink {file_path}')
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
                print(f'Deleted directory {file_path}')
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


# Schedule the cleanup every 24 hours
schedule.every().day.at("00:00").do(cleanup_downloads)

while True:
    schedule.run_pending()
    time.sleep(60)
