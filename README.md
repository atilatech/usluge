# Usluge

Usluge is a service for finding service providers.

Usluge means service in Montenegrin.

Try it at http://usluge.io/

## Quickstart

This project was created using [Python Telegram Bot: Your first Bot tutorial](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot).

`python -m venv botenv/`

`source botenv/bin/activate`

`pip install -r requirements.txt`

## Embed the Data
`python bot_helpers/embed.py`

`python bot.py`

## Deployment

This project exists as a bot on a `vps`, run it by `ssh` into the repo

`ssh -i /Users/tomiwa/.ssh/id_rsa_digitalocean root@167.172.106.44 ; cd usluge ; git pull`

### Copy local files to Server

If file is only on local machine:
`scp -i /Users/tomiwa/.ssh/id_rsa_digitalocean /Users/tomiwa/Desktop/tomiwa/code/usluge/.env root@167.172.106.44:/root/usluge`
