from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from fastai.vision import (
    ImageDataBunch,
    open_image,
    get_transforms,
    models,
    load_learner
)
import torch
from pathlib import Path
from io import BytesIO
import sys
import uvicorn
import aiohttp
import asyncio
import base64

async def get_bytes(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()


templates = Jinja2Templates(directory='/app/templates')
app = Starlette()

learn_flowers = load_learner("/app", file="flowers.pkl")

MAX_SHOW_RESULTS = 5
MIN_PROB_SHOW_RESULT = 0.0001

def ui_response(request, results, image_src, learn, class_names):
    pred_class,pred_idx,outputs = results
    if not class_names:
        class_names = {k: k for k in learn.data.classes}
    pred_class = class_names[str(pred_class)]
    class_names = [class_names[cl] for cl in learn.data.classes]
    probs = dict(zip(class_names, map(float, outputs)))
    del probs[pred_class]
    significant_results = ((k, v) for (k, v) in probs.items() if v >= MIN_PROB_SHOW_RESULT)
    show_results = sorted(significant_results, key = lambda x: -x[1])[:MAX_SHOW_RESULTS]
    context = {'request': request, "result": { "src": image_src, "class": pred_class, "confidence": outputs[pred_idx], "other_results": show_results}}
    return context;

async def run_classify(request, learn, class_names):
    data = await request.form()
    content_type = data["file"].content_type
    bytes = await (data["file"].read())
    image_src = "data:%s;base64,%s" % (content_type, base64.b64encode(bytes).decode())
    return ui_response(request, predict_image_from_bytes(bytes, learn), image_src, learn, class_names)

@app.route("/upload_flower_image", methods=["POST"])
async def upload(request):
    context = await run_classify(request, learn_flowers, None)
    return templates.TemplateResponse('flower.html', context)

def predict_image_from_bytes(bytes, learn):
    img = open_image(BytesIO(bytes))
    return learn.predict(img)

@app.route("/")
def form(request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.route("/model")
def pcb(request):
    return templates.TemplateResponse('model.html', {'request': request})


@app.route("/form")
def redirect_to_homepage(request):
    return RedirectResponse("/")


if __name__ == "__main__":
    if "serve" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8008)
