from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

def generate_timer_gif(target_time: datetime) -> BytesIO:
    if target_time.tzinfo is None:
        target_time = target_time.replace(tzinfo=timezone.utc)
    else:
        target_time = target_time.astimezone(timezone.utc)

    now = datetime.now(timezone.utc)
    remaining = int((target_time - now).total_seconds())
    start = max(remaining, 0)

    duration = min(start, 60)  # 60 кадров или меньше, если осталось меньше

    width, height = 400, 160

    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font = ImageFont.truetype(font_path, 60)
    except:
        font = ImageFont.load_default()

    frames = []

    # Генерируем кадры с текущего времени down to (start - duration + 1)
    for i in range(start, start - duration, -1):
        seconds_left = i
        days = seconds_left // 86400
        hours = (seconds_left % 86400) // 3600
        minutes = (seconds_left % 3600) // 60
        seconds = seconds_left % 60

        text = f"{days:02}:{hours:02}:{minutes:02}:{seconds:02}"

        img = Image.new('RGB', (width, height), color=(20, 20, 20))
        draw = ImageDraw.Draw(img)

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        draw.text(
            ((width - text_width) / 2, (height - text_height) / 2),
            text,
            font=font,
            fill=(255, 255, 255)
        )

        frames.append(img)

    output = BytesIO()
    frames[0].save(
        output,
        format='GIF',
        save_all=True,
        append_images=frames[1:],
        duration=1000,
        loop=0
    )
    output.seek(0)
    return output




@app.get("/timer.gif")
def timer_gif(to: str = Query(...)):
    try:
        # Поддержка ISO 8601 с "Z"
        target_time = datetime.fromisoformat(to.replace("Z", "+00:00"))
    except ValueError:
        return {"error": "Invalid 'to' datetime format. Use ISO format like 2025-12-31T23:59:59Z"}

    gif_file = generate_timer_gif(target_time)
    return StreamingResponse(gif_file, media_type="image/gif")
