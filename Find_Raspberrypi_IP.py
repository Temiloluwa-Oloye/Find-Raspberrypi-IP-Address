import re
import subprocess
import sqlite3
import time

# Connect to the database
conn = sqlite3.connect('raspberrypi.db')
c = conn.cursor()

# Create the table if it does not exist
c.execute('''CREATE TABLE IF NOT EXISTS devices
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, ip TEXT)''')

while True:
    # Get the IP addresses of devices on the network
    nmap_output = subprocess.check_output(["sudo", "nmap", "-sP", "-n", "192.168.0.0/16"])
    nmap_output = nmap_output.decode('utf-8')

    # Extract the IP addresses of the devices
    devices = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', nmap_output)

    # Check if each device is a Raspberry Pi and add it to the database if it is
    for device in devices:
        if subprocess.call(["ping", "-c", "1", "-W", "1", device], stdout=subprocess.DEVNULL) == 0:
            hostname = subprocess.check_output(["nmap", "-sL", device])
            hostname = hostname.decode('utf-8')
            if 'raspberry' in hostname.lower() or 'pi' in hostname.lower():
                c.execute("INSERT INTO devices (name, ip) VALUES (?, ?)", ("Raspberry Pi", device))
                print("Raspberry Pi detected at " + device)

    # Commit the changes to the database
    conn.commit()

    # Wait for 1 minute before scanning again
    time.sleep(60)
