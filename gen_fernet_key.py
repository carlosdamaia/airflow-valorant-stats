import os
from cryptography.fernet import Fernet

key = Fernet.generate_key()

env_file = '.env'

if os.path.exists(env_file):
    with open(env_file, 'r') as file:
        lines = file.readlines()
        
    updated = False
    with open(env_file, 'w') as file:
        for line in lines:
            if line.startswith("AIRFLOW__CORE__FERNET_KEY="):
                file.write(f'AIRFLOW__CORE__FERNET_KEY={key}\n')
                updated = True
            else:
                file.write(line)
                
        if not updated:
            file.write(f'AIRFLOW__CORE__FERNET_KEY={key}\n')
            
else:
    with open(env_file, 'w') as file:
        file.write(f"AIRFLOW__CORE__FERNET_KEY={key}\n")

print(f"Chave Fernet salva no arquivo {env_file}")