# Smart Pet Feeder - Raspberry Pi Setup Guide

Welcome to the Smart Pet Feeder project! This guide will walk you
through setting up your Raspberry Pi to run the pet feeder web
interface, connect to WiFi, and make the interface accessible via
<http://petfeeder.local:5000>. It also ensures the system auto-starts
after reboot.

## 📦 Requirements

-   Raspberry Pi (any model with WiFi support recommended)
-   MicroSD card (8GB or more)
-   Power supply for Pi
-   USB to Serial or GPIO serial connection to Arduino (e.g., Arduino
    Nano)
-   Internet connection for setup

## 1. 🔧 Initial Raspberry Pi Setup

Flash Raspberry Pi OS using Raspberry Pi Imager.

On first boot, configure:

-   Username and password
-   Connect to WiFi
-   Enable SSH (optional for remote access)

## 2. 🌐 Connect to WiFi (if not set in Imager)

\`\`\`bash sudo raspi-config \# Navigate to: System Options \> Wireless
LAN \# Enter SSID and password 3. 🌍 Set Up Local DNS (petfeeder.local)
Install Avahi to make the Pi accessible via petfeeder.local:

bash Zkopírovat Upravit sudo apt update && sudo apt install avahi-daemon
-y sudo systemctl enable avahi-daemon Ensure your computer is on the
same network. Now you can access the site from your browser:

http://petfeeder.local:5000

4.  🐍 Set Up Python App Clone the repository:

bash Zkopírovat Upravit cd \~/Documents git clone
https://github.com/YOUR_USERNAME/pet_feeder_web.git cd pet_feeder_web
Create virtual environment (optional but recommended):

bash Zkopírovat Upravit sudo apt install python3-venv -y python3 -m venv
venv source venv/bin/activate Install dependencies:

bash Zkopírovat Upravit pip install -r requirements.txt Make sure you
have:

app.py

communicator.py

templates/ folder

schedule.json (can be empty: {})

cat.json (can be empty: {})

5.  🛜 Serial Permissions (optional) If you're using /dev/serial0 or USB
    serial, ensure the user has permissions:

bash Zkopírovat Upravit sudo usermod -a -G dialout \$USER sudo reboot 6.
⚙️ Create a Systemd Service Create a service file to run Flask app at
boot:

bash Zkopírovat Upravit sudo nano /etc/systemd/system/petfeeder.service
Paste:

ini Zkopírovat Upravit \[Unit\] Description=Smart Pet Feeder Web
Interface After=network.target

\[Service\] User=pi WorkingDirectory=/home/pi/Documents/pet_feeder_web
ExecStart=/home/pi/Documents/pet_feeder_web/venv/bin/python3 app.py
Restart=always

\[Install\] WantedBy=multi-user.target Enable and Start the Service:

bash Zkopírovat Upravit sudo systemctl daemon-reexec sudo systemctl
daemon-reload sudo systemctl enable petfeeder.service sudo systemctl
start petfeeder.service To check logs:

bash Zkopírovat Upravit journalctl -u petfeeder.service -f ✅ Done! Your
Smart Pet Feeder web interface is now live and accessible at:

http://petfeeder.local:5000

It will automatically start after reboot or power loss. 🎉

💡 Notes You can modify feeding schedule and cat profile via the web
interface.

Arduino should be connected and running the appropriate sketch to
respond to serial commands.

Make sure /dev/serial0 or /dev/ttyUSB0 matches the device your Arduino
is on.

Happy feeding! 🐾

yaml Zkopírovat Upravit

------------------------------------------------------------------------

If you now want me to save this as an actual `.md` file and give you the
download link, just say the word.
