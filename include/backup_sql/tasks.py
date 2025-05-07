import logging
import os
from include.helpers.functions import create_backup_list_path, list_file_in_folder, replace_retention, upload_drive_file
from include.helpers.airflow_var import FOLDER_ID

def _upload_databases():
    
    backup_list_path = create_backup_list_path()

    for file_path in backup_list_path:
        filename = os.path.basename(file_path)
        logging.info(f'Processando arquivo: {filename}')
        
        current_drive_file = list_file_in_folder(filename, FOLDER_ID)
        
        if current_drive_file:     
            replace_retention(filename, current_drive_file)
        
        upload_drive_file(file_path, filename)