# Locust general config
ADD_SPAWNING_SUFFIX = False
LOG_STATISTICS_IN_HALF_MINUTE_CHUNKS = False
PERCENTILES_TO_REPORT = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80,
                         0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.888, 0.89, 0.90, 0.91, 0.92, 0.93, 0.94,
                         0.95, 0.96, 0.97, 0.98, 0.99, 0.9973, 0.999, 0.9999, 1.0]

# Thinking Time config
TT_AUTOMATIC_MIN = 0.001
TT_AUTOMATIC_MAX = 0.200
TT_USER_MIN = 1
TT_USER_MAX = 5

# Connection config
NETWORK_TIMEOUT = 120.0
CONNECTION_TIMEOUT = 120.0

# Actor distribution config
EXTERNAL_PERCENTAGE = 60
LOGGED_PERCENTAGE = 35
ADMIN_PERCENTAGE = 5

# Actors train choice config
HS_PERCENTAGE = 20
OTHER_PERCENTAGE = 80

# Probability of simulate new session or choose another behavior without logout
BEHAVIOR_PROBABILITY = 40
RESET_PROBABILITY = 20

# Logging config
LOG_ALL_REQUESTS = True
LOG_FLUSH_INTERVAL = 5

# Stop on request count
STOP_ON_REQUEST_COUNT = True
REQUEST_NUMBER_TO_STOP = 200



HS_TRAIN_TYPE_ID = ["GaoTieOne", "DongCheOne"]
OTHER_TRAIN_TYPE_ID = ["ZhiDa", "TeKuai", "KuaiSu"]

HS_TRIP_LIST = [
    ["nanjing", "zhenjiang", "wuxi", "suzhou", "shanghai"],
    ["nanjing", "shanghai"],
    ["nanjing", "suzhou", "shanghai"],
    ["suzhou", "shanghai"],
    ["shanghai", "suzhou"],
]

OTHER_TRIP_LIST = [
    ["shanghai", "nanjing", "shijiazhuang", "taiyuan"],
    ["nanjing", "xuzhou", "jinan", "beijing"],
    ["taiyuan", "shijiazhuang", "nanjing", "shanghai"],
    ["shanghai", "taiyuan"],
    ["shanghaihongqiao", "jiaxingnan", "hangzhou"],
]

TICKET_STATUS_BOOKED = 0
TICKET_STATUS_PAID = 1
TICKET_STATUS_COLLECTED = 2
TICKET_STATUS_CANCELLED = 4
TICKET_STATUS_EXECUTED = 6
ASSURANCE_TYPES = ["0", "1"]
