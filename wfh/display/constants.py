# define fixed rate for running WFH
INTERVAL = 15
START_TIME = 8
END_TIME = 20

API_HOST = "http://mango.local:8080"

ASSET_PATH = './wfh/assets'
FONT = f"{ASSET_PATH}/fonts/ChickenSoup.otf"
TIMES = {"8:00": f"{ASSET_PATH}/times/8.JPG",
         "10:00": f"{ASSET_PATH}/times/10.JPG",
         "12:00": f"{ASSET_PATH}/times/12.JPG",
         "14:00": f"{ASSET_PATH}/times/2.JPG",
         "16:00": f"{ASSET_PATH}/times/4.JPG",
         "18:00": f"{ASSET_PATH}/times/6.JPG",
         "20:00": f"{ASSET_PATH}/times/8.JPG"
         }
ICONS = {"coffee": f"{ASSET_PATH}/symbols/COFFEE.JPG",
         "login": f"{ASSET_PATH}/symbols/LOGIN.JPG",
         "logoff": f"{ASSET_PATH}/symbols/LOGOFF.JPG",
         "lunch": f"{ASSET_PATH}/symbols/LUNCH.JPG",
         "move": f"{ASSET_PATH}/symbols/MOVE.JPG",
         "pushups": f"{ASSET_PATH}/symbols/PUSHUPS.JPG"
         }
