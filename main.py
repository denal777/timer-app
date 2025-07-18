from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

# Функция генерации таймера-гифки
def generate_timer_gif(target_time: datetime) -> BytesIO:
    duration = 60  # секунд
    now = datetime.utcnow()
    remaining = int((target_time - now).total_seconds())
    start = min(max(remaining, 0), 60)  # от 0 до 60 секунд

    frames = []
    font = ImageFont.load_default()
    size = (200, 80)

    for i in range(start, max(start - 60, -1), -1):
        img = Image.new('RGB', size, color=(20, 20, 20))
        draw = ImageDraw.Draw(img)

        # Формат отображения времени
        text = f"{i:02d} sec"
        w, h = draw.textsize(text, font=font)
        draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, font=font, fill=(255, 255, 255))

        frames.append(img)

    # Сохраняем как GIF в память
    gif_bytes = BytesIO()
    frames[0].save(
        gif_bytes,
        format='GIF',
        save_all=True,
        append_images=frames[1:],
        duration=1000,  # 1 секунда на кадр
        loop=0
    )
    gif_bytes.seek(0)
    return gif_bytes

# Роут для генерации gif
@app.get("/timer.gif")
def timer_gif(to: str = Query(...)):
    try:
        target_time = datetime.fromisoformat(to.replace("Z", "+00:00"))
    except ValueError:
        return {"error": "Invalid 'to' datetime format. Use ISO format like 2025-12-31T23:59:59Z"}

    gif_file = generate_timer_gif(target_time)
    return StreamingResponse(gif_file, media_type="image/gif")
