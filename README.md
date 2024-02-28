# auto-restart-project-zomboid
This script is used to detect mod updates and restart automatically, only supported on Pterodactyl

## Required
- server Project Zomboid must be Running at **Pterodactyl**
- Python Lts

## Config.json \ explain
```{
    "docPath"         : "./",                     # Mod ID directory, if dont know, dont change it
    "serverName"      : "pzserver.ini",
    "IP_ADDRESS"      : "serverip:27015",         # server ip Project Zomboid, and **RCON PORT** (not server port)
    "IPSERVER"        : "serverip",               # Server IP Project Zomboid
    "PORT"            : "16261",                  # Server Port
    "PASSWORD_RCON"   : "you_password",           # Set your password at server.ini on your server project zomboid and find RCON password
    "admin"           : 1102032173340573817,      # Discord User ID
    "notifyChannel"   : 1074483557810065501,      # Discord Channel ID
    "warga"           : 1174003582954127410,      # Discord Role ID (who want tag when any update detect)
    "panel_url"       : "https://panel.example.com/", # Panel Pterodactl URL
    "apikey"          : "ptlc_....",              # Create APIKEY at Pterodactyl Panel
    "botToken"        : " ",                      # Discord BOT TOKEN
    "server_id"       : "asfw123",                # Server_ID of your project zomboid server 
    "gif_url_restart" : "https://media1.tenor.com/m/bGCuW8uql2kAAAAC/office-server.gif",     # change this if u need custome message gif
    "gif_url_running" : "https://media1.tenor.com/m/e2VK6sB1TX0AAAAd/online-server.gif"      # change this if u need custome message gif
}
```
## Show up
- Discord Announce
![IndoPZ](https://github.com/alfari24/auto-restart-project-zomboid/blob/main/img/Screenshot%202024-02-28%20082039.png)
![EndZ](https://github.com/alfari24/auto-restart-project-zomboid/blob/main/img/Screenshot%202024-02-28%20082103.png)

- Pterodactyl Running Bot
![Bot](https://github.com/alfari24/auto-restart-project-zomboid/blob/main/img/Screenshot%202024-02-28%20082214.png)
