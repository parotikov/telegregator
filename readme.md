# Telegregator
Телегрегатор - агрегатор телеграм-каналов.
Он умеет подписываться на каналы и группы (даже закрытые), и объединять их в общую ленту. Мы называем это поток (feed).
Для того, чтобы Телегретатор начал формировать поток, достаточно переслать ему сообщение из канала.

Еще Телегрегатор умеет фильтровать сообщения из оригинальных каналов по стоп-словам, избавляя вас от надоедливой рекламы

## Требования
- python 3.6
- pip
- telethon
- файл requirements.txt

## Установка
- создаем окружение: `python36 -m venv myvenv`
- активируем окружение: `source myvenv/bin/activate`
- устанавливаем зависимости: `pip install --no-cache-dir -r requirements.txt`
- клонируем репозиторий
- копируем и заполняем .env настройки. Как получить api id описано здесь: https://telethon.readthedocs.io/en/latest/basic/signing-in.html
- выполняем миграцию: `python database.py`
- запускаем: `python agregator.py`

### Docker (см. известные проблемы внизу)
- `docker build . -t tggt:1.0`
- `docker run --name tggt -v "$PWD":/usr/src/myapp -w /usr/src/myapp -d --restart unless-stopped tggt:1.0 python agregator.py`
или 
- `docker-compose build`
- `docker-compose up -d`

логи посмотреть командой `docker logs -f tggt`

## Использование без докера
Для работы приложения в фоновом режиме можно использовать supervisor, который [нужно предварительно установить и настроить](https://dev.xfor.top/2019-12-gotovim-centos-7-ustanovka-i-nastroyka-supervisord-na-vorker.html)
После установки супервизора, создаем файл `/etc/supervisord.d/telegregator.ini` с содержимым:

```
[program:telegregator]
command=/home/telegregatorbot/venv/bin/python /home/telegregatorbot/agregator.py ; путь к скрипту
process_name=%(program_name)s ; process_name expr (default %(program_name)s)
numprocs=1                    ; number of processes copies to start (def 1)
directory=/home/telegregatorbot/                ; directory to cwd to before exec (def no cwd)
priority=10                  ; the relative start priority (default 999)
autostart=true                ; start at supervisord start (default: true)
autorestart=true              ; retstart at unexpected quit (default: true)
startsecs=1                  ; number of secs prog must stay running (def. 1)
startretries=3                ; max # of serial start failures (default 3)
user=experiment                   ; setuid to this UNIX account to run the program
redirect_stderr=true          ; redirect proc stderr to stdout (default false)
stdout_logfile=/var/log/telegregator.log        ; stdout log path, NONE for none; default AUTO
stdout_logfile_maxbytes=10MB   ; max # logfile bytes b4 rotation (default 50MB)
stdout_logfile_backups=10     ; # of stdout logfile backups (default 10)
stdout_capture_maxbytes=1MB   ; number of bytes in 'capturemode' (default 0)
stderr_logfile=/var/log/telegregator.log        ; stderr log path, NONE for none; default AUTO
stderr_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
stderr_logfile_backups=10     ; # of stderr logfile backups (default 10)
stderr_capture_maxbytes=1MB   ; number of bytes in 'capturemode' (default 0)
stopsignal=KILL
```

Перезапускаем: `systemctl restart supervisord`

# Известные проблемы
- у одного аккаунта не может быть больше 500 каналов в подписках (ограничения телеграма. пока не знаю, как это обойти)
- когда телегрегатор запущен в докере, то не все каналы пересылаются. пока не разобрался, в чем дело, так что лучше запускать через supervisord
