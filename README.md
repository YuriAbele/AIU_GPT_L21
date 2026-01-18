# Заполнить файл .env


# установка и запуск
## 1 вариант
1. Docker-образ например с именем aui_gpt_l21_bot:v1:
docker build -t aui_gpt_l21_bot:v1 .

2. запуск контейнера
docker run --rm --name bot-container-new --env-file .env -v ${PWD}:/app aui_gpt_l21_bot:v1


## 2 вариант
docker-compose up --build


# остановка работы контейнера 
docker stop <container_id>


