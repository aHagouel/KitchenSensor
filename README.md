# KitchenSensor
Make sure Maui isn't in my kitchen when I'm not at home. 

# PI configuration
1. To ensure shutdown works, must place KitchenSensor/shutdown.py into /etc/rc.local to run at startup
2. To start program automatically on startup, must create startup.service in /etc/systemd/system/ to run KitchenSensor/kitchen.py after network loads. Content of the service file:

```
   [Unit]
   Description=Startup service
   Wants=network-online.target
   After=network.target network-online.target

   [Service]
   Type=oneshot
   ExecStart=/usr/bin/python3 /home/pi/Development/KitchenSensor/kitchen.py &
   RemainAfterExit=yes

   [Install]
   WantedBy=multi-user.target
   ```

