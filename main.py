from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

def generate_timer_gif(target_time: datetime) -> BytesIO:
    # Приводим target_time к UTC, если нужно
    if target_time.tzinfo is None:
        target_time = target_time.replace(tzinfo=timezone.utc)
    else:
        target_time = target_time.astimezone(timezone.utc)

    now = datetime.now(timezone.utc)
    remaining = int((target_time - now).total_seconds())
    start = min(max(remaining, 0), 60)  # От 0 до 60 секунд

    frames = []
    font = ImageFont.load_default()
    size = (200, 80)

    for i in range(start, max(start - 60, -1), -1):
        img = Image.new('RGB', size, color=(20, 20, 20))
        draw = ImageDraw.Draw(img)
        text = f"{i:02d} sec"
        w, h = draw.textsize(text, font=font)
        draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, font=font, fill=(255, 255, 255))
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
