# -*- coding: utf8 -*-
import requests
import json
import time
import random

def login_access_token(user, password):
    url = "https://account.huami.com/v2/client/login"
    data = {
        "country_code": "CN",
        "email": user,
        "password": password,
        "app_name": "com.xiaomi.hm.health",
        "app_version": "5.1.0",
        "device_type": "Android",
        "allow_registration": "false"
    }
    try:
        response = requests.post(url, data=data, timeout=20)
        res = response.json()
        if res.get("token_info"):
            return res["token_info"]["access_token"], "登录成功"
        return None, res.get("message", "登录失败")
    except Exception as e:
        return None, str(e)

def grant_login_tokens(access_token, device_id, is_phone):
    url = "https://api-mifit-cn.huami.com/v1/client/app_login"
    data = {
        "access_token": access_token,
        "device_id": device_id,
        "app_name": "com.xiaomi.hm.health"
    }
    try:
        res = requests.post(url, data=data, timeout=15).json()
        if res.get("login_token") and res.get("app_token"):
            return res["login_token"], res["app_token"], str(res.get("user_id", "")), "success"
        return None, None, None, res.get("message", "授权失败")
    except Exception as e:
        return None, None, None, str(e)

def grant_app_token(login_token):
    url = "https://api-mifit-cn.huami.com/v1/client/refresh_app_token"
    data = {"login_token": login_token}
    try:
        res = requests.post(url, data=data, timeout=15).json()
        if res.get("app_token"):
            return res["app_token"], "success"
        return None, res.get("message", "刷新失败")
    except Exception as e:
        return None, str(e)

def check_app_token(app_token):
    url = f"https://api-mifit-cn.huami.com/v1/user/profile?app_token={app_token}"
    try:
        res = requests.get(url, timeout=10)
        return res.status_code == 200, "ok"
    except:
        return False, "无效"

# ==================== 夜间实时同步上传（仅修改这里） ====================
def post_fake_brand_data(step, app_token, user_id):
    ts = int(time.time() * 1000)
    device_id = f"MI_BAND_{random.randint(10000000,99999999)}"
    step = int(step)

    data_json = {
        "steps": step,
        "calories": round(step * 0.045, 1),
        "distance": round(step * 0.00075, 2),
        "heartRate": random.randint(60, 85),
        "time": ts
    }

    headers = {
        "User-Agent": "MiFit/5.1.0 (Linux; Android 10; K)",
        "apptoken": app_token,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    url = "https://api-mifit-cn.huami.com/v1/data/band_data.json"
    data = {
        "userid": user_id,
        "last_sync_data_time": ts - random.randint(300000, 600000),
        "device_type": 1,
        "last_deviceid": device_id,
        "data_json": json.dumps(data_json, ensure_ascii=False)
    }

    try:
        resp = requests.post(url, data=data, headers=headers, timeout=15)
        result = resp.json()
        if result.get("message") == "success":
            return True, "夜间实时同步成功"
        else:
            return False, result.get("message", "未知错误")
    except Exception as e:
        return False, f"异常：{str(e)}"
