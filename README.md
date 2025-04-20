# Overengineered Pet Feeder - Raspberry Pi Setup Guide

Welcome to the Smart Pet Feeder project! This guide will walk you through setting up your Raspberry Pi to run the pet feeder web interface, connect to WiFi, and make the interface accessible via [http://petfeeder.local:5000](http://petfeeder.local:5000). It also ensures the system auto-starts after reboot.

## Repository Structure

```
pet_feeder_web/
├── raspberry/   → Python Flask web interface (run this on the Raspberry Pi)
├── arduino/     → Arduino sketch (upload to Arduino Nano)
```

---

## Requirements

- Raspberry Pi (any model with WiFi support recommended)
- MicroSD card (8GB or more)
- Power supply for Pi
- USB to Serial or GPIO serial connection to Arduino (e.g., Arduino Nano)
- Internet connection for setup

## 1. Initial Raspberry Pi Setup

Flash Raspberry Pi OS using Raspberry Pi Imager.

On first boot, configure:

- Username and password
- Connect to WiFi
- Enable SSH (optional for remote access)

## 2. Connect to WiFi (if not set in Imager)

```bash
sudo raspi-config
# Navigate to: System Options > Wireless LAN
# Enter SSID and password
```

## 3. Set Up Local DNS (petfeeder.local)

Install Avahi to make the Pi accessible via petfeeder.local:

```bash
sudo apt update && sudo apt install avahi-daemon -y
sudo systemctl enable avahi-daemon
```

Ensure your computer is on the same network. Now you can access the site from your browser:

[http://petfeeder.local:5000](http://petfeeder.local:5000)

## 4. Set Up Python App

Clone the repository:

```bash
cd ~/Documents
git clone https://github.com/YOUR_USERNAME/Overengineered-Pet-Feeder.git
cd Overengineered-Pet-Feeder/raspberry
```

Make sure you have:

- `app.py`
- `communicator.py`
- `templates/` folder
- `schedule.json` (can be empty: `{}`)
- `cat.json` (can be empty: `{}`)

## 5. Serial Permissions (optional)

If you're using `/dev/serial0` or USB serial, ensure the user has permissions:

```bash
sudo usermod -a -G dialout $USER
sudo reboot
```

## 6. Create a Systemd Service

Create a service file to run Flask app at boot:

```bash
sudo nano /etc/systemd/system/petfeeder.service
```

Paste:

```ini
[Unit]
Description=Smart Pet Feeder Web Interface
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/Documents/Overengineered-Pet-Feeder/raspberry
ExecStart=/home/pi/Documents/Overengineered-Pet-Feeder/raspberry/venv/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and Start the Service:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable petfeeder.service
sudo systemctl start petfeeder.service
```

To check logs:

```bash
journalctl -u petfeeder.service -f
```

## Done!

Your Smart Pet Feeder web interface is now live and accessible at:

[http://petfeeder.local:5000](http://petfeeder.local:5000)

It will automatically start after reboot or power loss.

## Notes

- You can modify feeding schedule and cat profile via the web interface.
- Arduino should be connected and running the appropriate sketch to respond to serial commands.
- Make sure `/dev/serial0` or `/dev/ttyUSB0` matches the device your Arduino is on.

---

## Features

- Web-based feeding schedule
- Automatic weight tracking with 4 load cells
- BMI monitoring & graphing
- Detects when the cat is eating
- OLED display with:
  - Real-time weight
  - Bongo Cat animation
  - Refill and measuring status
- Serial UART communication with simple ACK protocol
- Buzzer warning when food is low (daytime only)

---
