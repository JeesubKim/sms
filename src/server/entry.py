"""Server entry point"""

from server.util.config import read_config
from server.sms_server import SMSServer
from server.web_dashboard import SMSDashboard

if __name__ == "__main__":
    config = read_config()
    sms_server = SMSServer(config)  # thread
    sms_server.start()

    sms_web_dashboard = SMSDashboard(config, sms_server)  # thread
    sms_web_dashboard.start()

    sms_server.join()
    sms_web_dashboard.join()

# 1. run server separately
# --> server should read bin logs and initiate the topics
# --> server should serve the tcp socket

# clients (Producer and Consumers) can access the server to produce or consume the messages

# 2. run web server separately
