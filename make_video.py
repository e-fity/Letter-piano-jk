# -*- coding: utf-8 -*-
"""把 `out/<曲名>_notes.json` 渲染成「试演奏」视频（落块 + 合成主旋律）。

布局（按你定的排法）：
  * **7 条车道** = 音级 1~7（左→右）
  * 每条车道横向切成 **4 条**；块宽 = 2 条
  * 音区决定横向偏移（单位=条）：低音 o=-1 → 第 1~2 条，中音 o=0 → 第 2~3 条，
    高音 o=1 → 第 3~4 条。也就是 `offset = o + 1`，同一音级上音区越高块越往右半块。
    7*4 = 28 条刚好装下（音级7 高音 = 第 26~28 条）。
  * 块**高度 = 时值**（跟网页 app 一样：秒 × --second-px）
  * 纵向 = 时间：块从上方落下，**块的底边**碰到「现在」横线 = 这个音该弹的时刻
    （所以长音会从横线往上拖出长条，和网页 app 一致）

音频：主旋律按 `n/o/key` 合成音高，正弦叠谐波 + 包络，再和画面 mux 成 mp4。

用法：
    python make_video.py out/1_notes.json --bpm 100 --stills 8
    python make_video.py out/1_notes.json --bpm 100
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:                                     # noqa: BLE001
    FFMPEG = "ffmpeg"

# ── 取自你网页 app 的视觉常量（game.css）─────────────────────────────
BG        = (11, 13, 18)          # #0b0d12
INK       = (247, 244, 237)       # #f7f4ed
HIT_LINE  = (255, 122, 26)        # #ff7a1a
HIT_SOFT  = (255, 176, 120)       # #ffb078
REG_COLOR = {"low": (97, 216, 151), "middle": (255, 174, 84), "high": (118, 168, 255)}
REG_FILL  = {"low": (23, 59, 43), "middle": (75, 45, 23), "high": (26, 42, 74)}
DEFAULT_TEMPO = 100.0             # 与 jianpu_api.DEFAULT_TEMPO 一致

LANE_COUNT = 7
PARTS_PER_LANE = 4
STRIPS = LANE_COUNT * PARTS_PER_LANE          # 28
TILE_STRIPS = 2                               # 块宽 = 2 条
# 主音阶里 1~7 相对主音的半音数（大调音阶）
RANK_SEMITONES = [0, 2, 4, 5, 7, 9, 11]
PITCH_CLASS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def register_of(o):
    """音区 → 'low' / 'middle' / 'high'（±2/±3 先归到最近的一档）。"""
    if o < 0:
        return "low"
    if o > 0:
        return "high"
    return "middle"


def strip_offset(o):
    """音区 → 横向偏移（单位=条）。低音 0、中音 1、高音 2，即 o+1（夹到 0~2）。"""
    return max(0, min(2, int(o) + 1))


def parse_key(key_mark):
    """`1=C` / `1=♭B` / `1=F#` → 主音的 MIDI 号（中音区，C=60）。"""
    text = (key_mark or "1=C").split("=")[-1].strip()
    text = text.replace("♭", "b").replace("♯", "#").replace("＃", "#")
    base = text[0].upper()
    if base not in PITCH_CLASS:
        base = "C"
    midi = 60 + PITCH_CLASS[base]
    for ch in text[1:]:
        if ch == "#":
            midi += 1
        elif ch in ("b", "B"):
            midi -= 1
    return midi


def midi_of(note, tonic_midi):
    """一个音 → MIDI 号；休止/未识别返回 None。"""
    n = note.get("n")
    if n is None or int(n) == 0:
        return None
    n = int(n)
    o = int(note.get("o", 0) or 0)
    # ±2/±3 没有 7 个新车道，折到 ±1 那一档（和 layering 的 register_of 一致）
    octave = 1 if o > 1 else (-1 if o < -1 else o)
    return tonic_midi + RANK_SEMITONES[n - 1] + 12 * octave


def timeline(score, bpm, lead_in_beats):
    """算出每个音的起止秒（相对视频开头）与画面坐标参数。"""
    sec_per_beat = 60.0 / bpm
    notes, t = [], lead_in_beats * sec_per_beat
    for line in score["lines"]:
        for item in line["notes"]:
            q = float(item.get("q") or 1.0) * sec_per_beat
            notes.append({"item": item, "start": t, "dur": q})
            t += q
    return notes, t, sec_per_beat


@lru_cache(maxsize=64)
def font(size):
    """拉丁字母用的字体（块上的键位字母）。"""
    for name in ("arialbd.ttf", "seguisb.ttf", "arial.ttf", "segoeui.ttf"):
        path = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


@lru_cache(maxsize=16)
def cjk_font(size):
    """**中文**用的字体 —— 必须单独找。用 Arial 画「现在」会得到两个豆腐块 □□，
    因为拉丁字体里没有汉字字形（第一版就踩了）。"""
    for name in ("msyhbd.ttc", "msyh.ttc", "simhei.ttf", "simsun.ttc", "msyhl.ttc"):
        path = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def draw_tile(dr, box, color, fill, current):
    x0, y0, x1, y1 = box
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    radius = max(4, min(int((x1 - x0) * 0.28), int((y1 - y0) * 0.28), 14))
    dr.rounded_rectangle(box, radius=radius, fill=fill,
                         outline=color, width=3 if current else 2)


def render_frame(t, ctx, img, dr):
    """画第 t 秒这一帧（t 是视频时间）。"""
    W, H = ctx["W"], ctx["H"]
    hit_y = ctx["hit_y"]
    v = ctx["px_per_second"]

    dr.rectangle([0, 0, W, H], fill=BG)
    # 车道底色（很淡的竖向分区）
    for lane in range(LANE_COUNT):
        x0 = ctx["margin"] + lane * PARTS_PER_LANE * ctx["strip_w"]
        x1 = x0 + PARTS_PER_LANE * ctx["strip_w"]
        dr.rectangle([x0, 0, x1, H], fill=(17, 21, 30) if lane % 2 else (15, 18, 26))
    # 「现在」横线
    dr.line([0, hit_y, W, hit_y], fill=HIT_LINE, width=3)
    dr.text((10, hit_y - int(H * 0.022)), "现在", font=ctx["f_small"], fill=HIT_SOFT)

    # 块：远的先画，近的后画（挡住远处的）
    visible = []
    for note in ctx["notes"]:
        bottom = hit_y - (note["start"] - t) * v
        top = bottom - note["dur"] * v
        if bottom < -40 or top > H + 40:
            continue
        visible.append((bottom, top, note))
    visible.sort(key=lambda r: -r[0])

    for bottom, top, note in visible:
        item = note["item"]
        if item.get("n") is None or int(item.get("n") or 0) == 0:
            continue                                   # 休止不画块
        x0 = ctx["margin"] + (int(item["n"]) - 1) * PARTS_PER_LANE * ctx["strip_w"] \
            + strip_offset(int(item.get("o", 0) or 0)) * ctx["strip_w"]
        x1 = x0 + TILE_STRIPS * ctx["strip_w"]
        top_c = max(top, ctx["top_clip"])
        bottom_c = min(bottom, H)
        if bottom_c - top_c < 3:
            continue
        reg = register_of(int(item.get("o", 0) or 0))
        current = note["start"] <= t < note["start"] + note["dur"]
        draw_tile(dr, (x0, top_c, x1, bottom_c), REG_COLOR[reg], REG_FILL[reg], current)
        letter = item.get("letter")
        if letter and x1 - x0 >= 16:
            size = max(12, min(int((x1 - x0) * 0.5), 46))
            f = font(size)
            cx = (x0 + x1) / 2
            cy = min(max((top_c + bottom_c) / 2, top_c + size * 0.7), bottom_c - size * 0.7)
            dr.text((cx, cy), str(letter), font=f, fill=INK, anchor="mm",
                    stroke_width=1, stroke_fill=BG)
    return img


def synth(notes, tonic_midi, total, sr=44100):
    """按音高合成主旋律。正弦叠谐波 + 简单包络。"""
    out = np.zeros(int(total * sr) + sr, dtype=np.float32)
    for note in notes:
        midi = midi_of(note["item"], tonic_midi)
        if midi is None:
            continue
        freq = 440.0 * 2 ** ((midi - 69) / 12.0)
        dur = note["dur"] * 0.92                        # 留一点断句
        n = max(int(dur * sr), 1)
        tt = np.arange(n) / sr
        wave_ = sum(a * np.sin(2 * np.pi * freq * h * tt)
                    for h, a in ((1, 1.0), (2, 0.42), (3, 0.18), (4, 0.08)))
        env = np.ones(n, dtype=np.float32)
        att = min(int(0.012 * sr), n)
        env[:att] = np.linspace(0, 1, att)
        dec = np.exp(-tt * 2.6)                          # 缓慢衰减，像敲击后余音
        env *= (0.35 + 0.65 * dec)
        rel = min(int(0.05 * sr), n)
        env[-rel:] *= np.linspace(1, 0, rel)
        s = int(note["start"] * sr)
        seg = wave_ * env * 0.23
        out[s:s + n] += seg[:max(0, len(out) - s)]
    peak = float(np.abs(out).max()) or 1.0
    if peak > 0.95:
        out *= 0.95 / peak
    return out, sr


def write_wav(path, samples, sr):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes())


def build(score_path, args):
    with open(score_path, "r", encoding="utf-8") as fp:
        score = json.load(fp)
    # 拍速优先级：命令行 > JSON 里存的 tempo_qpm > 默认
    bpm = args.bpm or score.get("tempo_qpm") or DEFAULT_TEMPO
    bpm = float(bpm)
    src_note = ("命令行" if args.bpm else
                ("JSON" if score.get("tempo_qpm") else "默认"))
    W, H = (int(v) for v in args.size.lower().split("x"))
    hit_y, top_clip = int(H * args.hit), int(H * 0.02)
    margin = int(W * 0.02)
    # 每秒像素：给了 --second-px 就用它，否则按「线上显示几秒」反算
    px_per_second = args.second_px or ((hit_y - top_clip) / args.lookahead)
    ctx = {
        "W": W, "H": H,
        "hit_y": hit_y,
        "px_per_second": px_per_second,
        "margin": margin,
        "strip_w": (W - 2 * margin) / STRIPS,
        "f_small": cjk_font(max(16, H // 55)),
        "top_clip": top_clip,
    }
    notes, song_end, _spb = timeline(score, bpm, args.lead_in)
    ctx["notes"] = notes
    total = song_end + args.tail_beats * 60.0 / bpm
    tonic = parse_key(score.get("key"))
    print("曲名 %s | %s %s | BPM %g（来自%s）| 音数 %d | 时长 %.1fs（%.1f 分）"
          % (score.get("title"), score.get("key"), score.get("meter"), bpm, src_note,
             len(notes), total, total / 60))
    print("主音 MIDI %d | 画面 %dx%d | 现在线 y=%d | 每秒 %.0fpx"
          % (tonic, W, H, ctx["hit_y"], ctx["px_per_second"]))
    return score, ctx, notes, total, tonic, bpm


def main(argv=None):
    p = argparse.ArgumentParser(description="把逐音 JSON 渲染成「试演奏」视频。")
    p.add_argument("score", help="out/<曲名>_notes.json")
    p.add_argument("-o", "--out", default=None, help="输出 mp4（默认 <曲名>_试演奏.mp4）")
    p.add_argument("--bpm", type=float, default=None,
                   help="拍速（四分音符/分钟）。不给就用 JSON 里的 tempo_qpm，"
                        "再没有就 100（谱面没印 ♩= 时的默认）")
    p.add_argument("--size", default="1080x1920", help="宽x高，默认竖屏 1080x1920")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--hit", type=float, default=0.72, help="「现在」线在画面高度的比例")
    p.add_argument("--lookahead", type=float, default=2.8,
                   help="「现在」线以上显示几秒（默认 2.8s）。像素比例由它反算 —— "
                        "别直接照抄网页 app 的 --second-px=288：那是在它 650px 高的"
                        "线上区域标定的，换到别的分辨率就会要么太空要么挤爆")
    p.add_argument("--second-px", type=float, default=None,
                   help="显式指定每秒像素（给了就忽略 --lookahead）")
    p.add_argument("--lead-in", type=float, default=2.0, help="开头留几拍")
    p.add_argument("--tail-beats", type=float, default=2.0, help="结尾多留几拍")
    p.add_argument("--stills", default=None,
                   help="只出静止帧：给百分比列表如 2,10,30,60（不编码视频）")
    p.add_argument("--no-audio", action="store_true")
    args = p.parse_args(argv)

    score, ctx, notes, total, tonic, bpm = build(args.score, args)

    if args.stills is not None:
        base = os.path.splitext(os.path.basename(args.score))[0].replace("_notes", "")
        for pct in [float(x) for x in args.stills.split(",")]:
            t = total * pct / 100.0
            img = Image.new("RGB", (ctx["W"], ctx["H"]), BG)
            render_frame(t, ctx, img, ImageDraw.Draw(img))
            path = os.path.join(tempfile.gettempdir(), "_still_%s_%g.png" % (base, pct))
            img.save(path)
            print("  静止帧 t=%6.1fs (%g%%)  →  %s" % (t, pct, path))
        return 0

    # 默认按**曲名**命名（"上海滩_试演奏.mp4"），而不是图号（"1_试演奏.mp4"）
    name = str(score.get("title") or "").strip() or \
        os.path.splitext(os.path.basename(args.score))[0].replace("_notes", "")
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    out = args.out or (name + "_试演奏.mp4")
    tmp = tempfile.gettempdir()
    silent = os.path.join(tmp, "_jpk_silent.mp4")
    frames = int(total * args.fps)
    print("开始渲染 %d 帧…" % frames)

    writer = subprocess.Popen(
        [FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", "%dx%d" % (ctx["W"], ctx["H"]), "-r", str(args.fps), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", silent],
        stdin=subprocess.PIPE)
    img = Image.new("RGB", (ctx["W"], ctx["H"]), BG)
    dr = ImageDraw.Draw(img)
    for i in range(frames):
        render_frame(i / args.fps, ctx, img, dr)
        writer.stdin.write(img.tobytes())
        if i and i % (args.fps * 15) == 0:
            print("  %d/%d 帧（%.0fs）" % (i, frames, i / args.fps))
    writer.stdin.close()
    writer.wait()

    if args.no_audio:
        os.replace(silent, out)
        print("完成（无音频）：", os.path.abspath(out))
        return 0

    samples, sr = synth(notes, tonic, total)
    wav = os.path.join(tmp, "_jpk_audio.wav")
    write_wav(wav, samples, sr)
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
                    "-i", silent, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "160k", "-shortest", out], check=True)
    print("完成：", os.path.abspath(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
