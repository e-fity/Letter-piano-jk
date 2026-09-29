# -*- coding: utf-8 -*-
"""一张网页：传简谱图片进来，看识别结果（原位替换图 + 逐音对照表）。

    python webapp.py                # 默认 http://127.0.0.1:8010/
    python webapp.py --port 9000
    python webapp.py --debug        # 改前端代码自动生效

识别本身还是 `jianpu_api.convert()`，这里只做三件事：收图、落盘、把产物端出去。
产物按请求各自一个小目录（`web_out/<id>/`），互不覆盖，想留着就自己去那个目录拿。
"""

import argparse
import glob
import json
import os
import re
import shutil
import threading
import time
import uuid

from flask import Flask, jsonify, request, send_file, send_from_directory

import jianpu_api

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "web")
WORK = os.path.join(HERE, "web_out")
LIB = os.path.join(HERE, "out")          # 已识别转换好的曲库（选择页从这里读）
NOTES_SUFFIX = "_notes.json"
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp")
ID_RE = re.compile(r"[0-9a-f]{12}")

app = Flask(__name__)

# jianpu_api 用的是 ocr_jianpu 的模块全局（底图、缩放倍数），**不是线程安全的**，
# 所以并发的识别请求必须排队。Flask 仍然 threaded=True —— 那样识别跑着的时候，
# 页面照样能取图和下载，不会整站卡住。
_RUN_LOCK = threading.Lock()


def _fail(message, status=400):
    return jsonify({"ok": False, "error": message}), status


@app.get("/")
def index():
    return send_from_directory(WEB, "index.html")


@app.post("/api/convert")
def convert():
    upload = request.files.get("image")
    if upload is None or not upload.filename:
        return _fail("没有收到图片文件。")
    ext = os.path.splitext(upload.filename)[1].lower()
    if ext not in IMAGE_EXTS:
        return _fail(f"不认识 {ext or '（无扩展名）'} 这种文件，"
                     f"请传 {'、'.join(IMAGE_EXTS)}。")

    rid = uuid.uuid4().hex[:12]
    workdir = os.path.join(WORK, rid)
    os.makedirs(workdir, exist_ok=True)
    # 存成固定名：产物名因此可预测，也不用拿上传的文件名去拼路径。
    # 原始文件名只用来在页面上显示，不落进任何路径。
    src = os.path.join(workdir, "upload" + ext)
    upload.save(src)

    started = time.time()
    try:
        with _RUN_LOCK:
            overlay, table, payload = jianpu_api.convert(src, outdir=workdir)
    except Exception as exc:  # noqa: BLE001 —— 读不成的图什么样都有，如实回报给页面
        shutil.rmtree(workdir, ignore_errors=True)
        return _fail(f"这张图没读成。{type(exc).__name__}: {exc}", 500)

    return jsonify({
        "ok": True,
        "id": rid,
        "original_name": os.path.basename(upload.filename),
        "seconds": round(time.time() - started, 1),
        "title": payload["title"],
        "key": payload["key"],
        "meter": payload["meter"],
        "counts": payload["counts"],
        "lines": payload["lines"],
        "overlay_url": f"/files/{rid}/{os.path.basename(overlay)}",
        "source_url": f"/files/{rid}/{os.path.basename(src)}",
        "table_url": f"/files/{rid}/{os.path.basename(table)}",
    })


@app.get("/files/<rid>/<name>")
def files(rid, name):
    if not ID_RE.fullmatch(rid):
        return "没有这个结果。", 404
    # send_from_directory 自己会挡住 `..` 之类的路径穿越，这里不用再拼字符串。
    return send_from_directory(os.path.join(WORK, rid), name)


# ── 选择页：列出已经识别转换好的曲目，选一首看结果 ──────────────────────────

def _song_index():
    """扫 `LIB` 下所有 `<名字>_notes.json`，返回 {名字: 曲目信息}。

    曲名、调号、拍号、音数都从那份 JSON 里读；原图路径取 JSON 的 `source`
    （那是识别时记下的绝对路径，可能已经不在了，所以要 isfile 检查）。
    """
    songs = {}
    for path in sorted(glob.glob(os.path.join(LIB, "*" + NOTES_SUFFIX))):
        base = os.path.basename(path)[:-len(NOTES_SUFFIX)]
        try:
            with open(path, "r", encoding="utf-8") as fp:
                payload = json.load(fp)
        except (OSError, ValueError):
            continue
        src = str(payload.get("source") or "")
        songs[base] = {
            "base": base,
            "title": payload.get("title") or base,
            "key": payload.get("key") or "",
            "meter": payload.get("meter") or "",
            "counts": payload.get("counts") or {},
            "has_original": bool(src) and os.path.isfile(src)
                            and os.path.splitext(src)[1].lower() in IMAGE_EXTS,
            "overlay_url": f"/library/img/{base}/overlay",
            "original_url": f"/library/img/{base}/original",
            "notes_url": f"/library/notes/{base}",
        }
    return songs


@app.get("/library")
def library():
    return send_from_directory(WEB, "library.html")


@app.get("/api/library")
def api_library():
    songs = _song_index()
    return jsonify({"ok": True, "songs": [songs[k] for k in sorted(songs)]})


@app.get("/library/img/<base>/<what>")
def library_img(base, what):
    # 先拿 base 去曲目表里**核对**，核不上就 404 —— 于是 base 永远拼不出路径穿越。
    song = _song_index().get(base)
    if song is None:
        return "曲库里没有这一首。", 404
    if what == "overlay":
        return send_file(os.path.join(LIB, base + "_overlay.png"))
    if what == "original":
        with open(os.path.join(LIB, base + NOTES_SUFFIX), "r", encoding="utf-8") as fp:
            src = str(json.load(fp).get("source") or "")
        if not (src and os.path.isfile(src)):
            return "原图不在原来的位置了（JSON 的 source 指向的路径已经不存在）。", 404
        return send_file(src)
    return "不认识的类型。", 404


@app.get("/library/notes/<base>")
def library_notes(base):
    if _song_index().get(base) is None:
        return "曲库里没有这一首。", 404
    return send_file(os.path.join(LIB, base + NOTES_SUFFIX), as_attachment=True,
                     download_name=base + NOTES_SUFFIX)


def main(argv=None):
    parser = argparse.ArgumentParser(description="传简谱图片进来，看识别结果。")
    parser.add_argument("--port", type=int, default=8010)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--debug", action="store_true", help="改代码自动生效（调试用）")
    args = parser.parse_args(argv)

    os.makedirs(WORK, exist_ok=True)
    print(f"简谱认谱： http://{args.host}:{args.port}/    （结果落在 {WORK}）")
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)


if __name__ == "__main__":
    main()
