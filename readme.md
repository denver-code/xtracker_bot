# tracker bot
This bot created only for personal needs and was written in hour, so code contain some issues, dublicates, and doesn't meet all requirements.  
This will be changed it near feature, as I want to create a global logging-tracker bot, so don't use this bot at production.
# ▹ Installation #
> [!NOTE]  
> For start make sure you have python and redis or docker installed on your machine.
``` Bash
git clone https://github.com/denver-code/xtracker_bot
cd xtracker_bot
```   
Rename ```sample.env -> .env``` and don't forget to change the settings inside.
# ▹ Run using docker #
> [!NOTE]  
> For start make sure you have docker installed on your machine.
``` bash
docker-compose up --build -d
```
# ▹ Run #
> [!NOTE] Make sure you have installed poetry on your machine (pip3 install poetry)
``` Bash
poetry install
poetry run python3 -m bot
```

# Edit project in VS Code
``` bash
poetry install
poetry shell
code .
```