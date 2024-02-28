import asyncio
import json
import subprocess
import discord
from discord.ext import commands
from discord.ext.tasks import loop
import glob
import os
import re
import requests
import time
from datetime import datetime
import aiohttp
from discord import Embed
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents)

#====================================================================================
#LOAD DATA
with open('config.json') as f:
    config = json.load(f)

dPath = config["docPath"]
sName = config["serverName"]
nChannel = config["notifyChannel"] #channel discord
admin_ds = config["admin"] # Role admin
botToken = config["botToken"]
nSurvivor = config["warga"]
panel = config["panel_url"]
server_id = config["server_id"]
ApiKey = config["apikey"]
ip_address = config["IP_ADDRESS"]
password = config["PASSWORD_RCON"]
gift_restart = config["gif_url_restart"]
gift_running = config["gif_url_running"]

#====================================================================================
#FUNGSI UTAMA POWER RESTART
async def restart_server(server_id):
    power_url = f"{panel}api/client/servers/{server_id}/power"
    payload = {"signal": "restart"}

    headers = {
        'Accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': 'Bearer ' + ApiKey
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(power_url, headers=headers, json=payload) as response:
            try:
                print("Server Start HTTP Status Code:", response.status)
                
                if response.status == 204:
                    success_message = f"Server IndoPZ has been Restarted successfully!\nTunggu Beberapa Menit sampai server benar benar berjalan normal"
                    print(success_message)
                    return success_message
                elif 'application/json' in response.headers.get('content-type', ''):
                    result = await response.json()
                    print("Server Restart Response:", result)  # Print the response content
                    return result
                else:
                    result = await response.text()
                    print("Server Restart Response:", result)  # Print the response content
                    return result
            except Exception as e:
                print(f"Error handling response: {e}")
                return f"Error handling response: {e}"
            
            
async def get_server_status(server_id):
    resources_url = f"{panel}api/client/servers/{server_id}/resources"

    headers = {
        'Accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': 'Bearer ' + ApiKey
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(resources_url, headers=headers) as response:
                print("Server Status HTTP Status Code:", response.status)

                if response.status == 200:
                    result = await response.json()
                    print("Server Status Response:", result)  # Print the response content

                    # Check the server status from the response (modify this condition based on your API response structure)
                    if result.get("attributes", {}).get("current_state", "N/A") == 'running':
                        return "Server is currently running"
                    elif result.get("attributes", {}).get("current_state", "N/A") == 'starting':
                        return "Server is currently starting"
                    else:
                        return "Server status is unknown"

                elif 'application/json' in response.headers.get('content-type', ''):
                    result = await response.json()
                    print("Server Status Response:", result)  # Print the response content
                    return result
                else:
                    result = await response.text()
                    print("Server Status Response:", result)  # Print the response content
                    return result
    except Exception as e:
        print(f"Error handling response: {e}")
        return f"Error handling response: {e}"

#=====================================================================================
#CHECK SERVER SETIAP 5 MENIT
@loop(minutes=1)
async def modcheck():
    with open(dPath+"Server/"+sName) as file:
        configfile = file.read().splitlines()
        for entry in configfile:
            if entry.startswith('WorkshopItems'):
                workshopIDs = entry[14:].split(";") 

    print("ModCheck")
    data = {}
    data["itemcount"] = str(len(workshopIDs)) # The list of workshop IDs retrieved from the server config previously
    counter = 0

    for entry in workshopIDs: # Adds the workshop entries to an array
        data[f"publishedfileids[{counter}]"] = str(entry)
        counter += 1

    xcheck = requests.post("https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/", data).json()  # Sends the data to steam, recieving all workshop pages and its info back
    checkresults = {}
    for entry in xcheck["response"]["publishedfiledetails"]: # Fetches the specific workshop data we care about into "dictionaries"
        try:
            id = entry["publishedfileid"]
            checkresults[id] = {}  # The ID of the workshop mod, as the base of the "dictionary"
            checkresults[id]["title"] = entry["title"]  # The name of the workshop mod
            checkresults[id]["time_updated"] = entry["time_updated"]
            checkresults[id]["file_size"] = entry["file_size"]  # The last time the mod was updated, in UNIX Epoch time.
        except KeyError:
            continue

    if os.path.isfile("moddata.json") == False:
        print("No moddata.json found, creating file")
        with open("moddata.json", "w+") as f:
            print("Populating file with workshop data")
            json.dump(checkresults, f) # Populate the list by default

    with open ("moddata.json", "r+") as f:  # Loads previously fetched workshop data for comparison
        cacheresult = json.load(f)
        print("Loaded moddata.json")

    for key, value in checkresults.items():  # Run this code for every workshop entry in our "dictionary"
        try:  # Weird method for me to detect if this entry exists or not, if not, probably a new mod
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(f"""[{current_time}] {value["time_updated"]} vs {cacheresult[key]["time_updated"]} [{value["title"]}]""")
        except KeyError:
            continue
        
        try:
            if (value["time_updated"] > cacheresult[key]["time_updated"]) or (value["file_size"] > cacheresult[key]["file_size"]):  # If that value is higher then the one we cached, the mod on the workshop is newer, and has been updated
                print("Detected mod update! ")
                ch = bot.get_channel(nChannel)  # Yell in this Discord channel
				
                #send messgae to ingame========================================================================================================
                command = f"./rcon -a {ip_address} -p {password} \"servermsg \\\"Server Akan Restart otomatis 3 Menit lagi, untuk mod update.\\\"\""
                subprocess.run(command, shell=True, check=True)
                command = f"./rcon -a {ip_address} -p {password} \"save\""
                subprocess.run(command, shell=True, check=True)
                
                embed = Embed(title=f"Mod [ {value['title']} ] Butuh Update!.",
                              description=f"**Server Akan restart otomatis dalam 3 Menit.**",
                              color=0x00FF00)
                await ch.send(f"<@&{nSurvivor}>")
                await ch.send(embed=embed)
                await asyncio.sleep(60) # wait 3 minute
                #=========================================OLD=================================================================================
                #await ch.send(f"""Mod Steam Workshop ` [ {value["title"]} ] ` Butuh Update! <@&{nSurvivor}> . """)
                #await ch.send(f"""Server will be restarted in 3 Minutes for mod update""")
                #await asyncio.sleep(60) # wait 3 minute \n<@&{nSurvivor}>
                
				#send message to discord=======================================================================================================
                
                
                
                
                
                #send messgae to ingame========================================================================================================
                command = f"./rcon -a {ip_address} -p {password} \"servermsg \\\"Server Akan Restart otomatis 2 Menit lagi, untuk mod update.\\\"\""
                subprocess.run(command, shell=True, check=True)
                command = f"./rcon -a {ip_address} -p {password} \"save\""
                subprocess.run(command, shell=True, check=True)
                await asyncio.sleep(60)

                #embed = Embed(title="Server Akan restart otomatis dalam 2 Menit.",
                #            description="",
                #            color=0xFF5733)
                #
                #await ch.send(embed=embed)
                #await asyncio.sleep(60)
				#send message to discord=======================================================================================================
                
                
                
                
                
                
                #send messgae to ingame========================================================================================================
                command = f"./rcon -a {ip_address} -p {password} \"servermsg \\\"Please Logout, Server will be restarted in 1 Minutes.\\\"\""
                subprocess.run(command, shell=True, check=True)
                command = f"./rcon -a {ip_address} -p {password} \"save\""
                subprocess.run(command, shell=True, check=True)
                await asyncio.sleep(60)
                embed = Embed(title="Server Memulai Restart",
                            description="",
                                        color=0xFF5733)
                embed.set_image(url=gift_restart)
                await ch.send(embed=embed)
                #await asyncio.sleep(60)
                #send messgae to ingame========================================================================================================
                
                try:
                    #for restart server
                    command = f"./rcon -a {ip_address} -p {password} \"save\""
                    subprocess.run(command, shell=True, check=True)
                    result = await restart_server(server_id)
                    print(result)
                    #for checking server online
                    while True:
                        server_status = await get_server_status(server_id)
                        
                  
                        if server_status == "Server is currently running":
                            
                            embed = Embed(title="Server sudah Online",
                                          description=" ",
                                          color=0x00FF00)
                            embed.set_image(url=gift_running)
                            await ch.send(f"<@&{nSurvivor}>")
                            await ch.send(embed=embed)
                            
                            print("Server is now running")
                            break
                        elif server_status == "Server is currently starting":
                            print("Server is still starting. Checking again in 1 minute...")
                            await asyncio.sleep(60)
                            
                        elif 'current_state' in server_status and server_status['current_state'] == 'running':
                            print("Server is now running")
                            embed = Embed(title="Server sudah Online",
                                          description=" ",
                                          color=0x00FF00)
                            embed.set_image(url=gift_running)
                            await ch.send(f"<@&{nSurvivor}>")
                            await ch.send(embed=embed)
                            break
                        else:
                            print("Unexpected server status. Exiting loop.")
                            await asyncio.sleep(60)

                    with open("moddata.json", "w") as f:
                        json.dump(checkresults, f)
                        print("Mod Update Success, Thank You ~")
                except subprocess.CalledProcessError as e:
                    print(f"Terjadi kesalahan: hubungi Teknisi Server")
            		
        except KeyError:
            continue

@bot.event
async def on_ready():
    modcheck.start()

bot.run(botToken)