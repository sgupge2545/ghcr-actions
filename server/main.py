from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import time
from fastapi.responses import HTMLResponse
import asyncio
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets


app = FastAPI()

# 簡易キャッシュ
weather_cache = {}

security = HTTPBasic()


class WeatherResponse(BaseModel):
    city: str
    temperature: float
    unit: str


# 都道府県庁所在地の緯度経度マップ
city_coords = {
    "北海道": (43.0642, 141.3469),  # 札幌
    "青森県": (40.8244, 140.7400),  # 青森
    "岩手県": (39.7036, 141.1527),  # 盛岡
    "宮城県": (38.2688, 140.8721),  # 仙台
    "秋田県": (39.7186, 140.1024),  # 秋田
    "山形県": (38.2404, 140.3633),  # 山形
    "福島県": (37.7503, 140.4676),  # 福島
    "茨城県": (36.3418, 140.4468),  # 水戸
    "栃木県": (36.5658, 139.8836),  # 宇都宮
    "群馬県": (36.3911, 139.0608),  # 前橋
    "埼玉県": (35.8569, 139.6489),  # さいたま
    "千葉県": (35.6046, 140.1233),  # 千葉
    "東京都": (35.6895, 139.6917),  # 東京
    "神奈川県": (35.4478, 139.6425),  # 横浜
    "新潟県": (37.9026, 139.0232),  # 新潟
    "富山県": (36.6953, 137.2113),  # 富山
    "石川県": (36.5947, 136.6256),  # 金沢
    "福井県": (36.0652, 136.2216),  # 福井
    "山梨県": (35.6639, 138.5684),  # 甲府
    "長野県": (36.6513, 138.1810),  # 長野
    "岐阜県": (35.3912, 136.7223),  # 岐阜
    "静岡県": (34.9769, 138.3831),  # 静岡
    "愛知県": (35.1802, 136.9066),  # 名古屋
    "三重県": (34.7303, 136.5086),  # 津
    "滋賀県": (35.0045, 135.8686),  # 大津
    "京都府": (35.0214, 135.7556),  # 京都
    "大阪府": (34.6937, 135.5023),  # 大阪
    "兵庫県": (34.6913, 135.1830),  # 神戸
    "奈良県": (34.6851, 135.8048),  # 奈良
    "和歌山県": (34.2260, 135.1675),  # 和歌山
    "鳥取県": (35.5039, 134.2377),  # 鳥取
    "島根県": (35.4723, 133.0505),  # 松江
    "岡山県": (34.6618, 133.9344),  # 岡山
    "広島県": (34.3966, 132.4596),  # 広島
    "山口県": (34.1859, 131.4714),  # 山口
    "徳島県": (34.0658, 134.5593),  # 徳島
    "香川県": (34.3401, 134.0434),  # 高松
    "愛媛県": (33.8416, 132.7657),  # 松山
    "高知県": (33.5597, 133.5311),  # 高知
    "福岡県": (33.5902, 130.4017),  # 福岡
    "佐賀県": (33.2635, 130.3009),  # 佐賀
    "長崎県": (32.7503, 129.8777),  # 長崎
    "熊本県": (32.7898, 130.7417),  # 熊本
    "大分県": (33.2382, 131.6126),  # 大分
    "宮崎県": (31.9111, 131.4239),  # 宮崎
    "鹿児島県": (31.5602, 130.5581),  # 鹿児島
    "沖縄県": (26.2124, 127.6809),  # 那覇
}


@app.get("/api/weather", response_class=HTMLResponse)
async def get_weather_html():
    now = time.time()
    results = []

    async def fetch_weather(city):
        if city in weather_cache and now - weather_cache[city]["timestamp"] < 300:
            return weather_cache[city]["data"]
        lat, lon = city_coords[city]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            data = resp.json()
            temp = data["current_weather"]["temperature"]
            unit = "°C"
        result = WeatherResponse(city=city, temperature=temp, unit=unit)
        weather_cache[city] = {"timestamp": now, "data": result}
        return result

    # 並列で全都道府県の天気を取得
    results = await asyncio.gather(*(fetch_weather(city) for city in city_coords))

    # HTMLを組み立てて返す
    html = """
    <html>
      <body>
        <ul>
    """
    for result in results:
        html += f"<li>{result.city}: {result.temperature} {result.unit}</li>"
    html += """
        </ul>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/api/hello")
def read_root(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "id")
    correct_password = secrets.compare_digest(credentials.password, "pw")
    if not (correct_username and correct_password):
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証情報が正しくありません",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"message": "Hello, World!"}


app.mount("/", StaticFiles(directory="server/dist", html=True), name="static")
