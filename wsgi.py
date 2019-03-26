import os
import leancloud
from cloud import engine

from shortcut_api import app

APP_ID = os.environ['LEANCLOUD_APP_ID']  # 从 LEANCLOUD_APP_ID 这个环境变量中获取应用 app id 的值
APP_KEY = os.environ['LEANCLOUD_APP_KEY']  # 从 LEANCLOUD_APP_KEY 这个环境变量中获取应用 app key 的值
MASTER_KEY = os.environ['LEANCLOUD_APP_MASTER_KEY']  # 从 LEANCLOUD_APP_MASTER_KEY 这个环境变量中获取应用 master key 的值

leancloud.init(APP_ID, app_key=APP_KEY, master_key=MASTER_KEY)
# 如果需要使用 master key 权限访问 LeanCloud 服务，请将这里设置为 True
leancloud.use_master_key(False)

# http 重定向到 https
app = leancloud.HttpsRedirectMiddleware(app)
app = engine.wrap(app)
application = app
