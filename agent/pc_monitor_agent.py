#!/usr/bin/env python3
"""PC Monitor local agent. No cloud telemetry; unavailable sensors are explicit."""
from __future__ import annotations
import argparse, asyncio, json, logging, os, platform, socket, threading, time, uuid, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
import psutil

LOG = logging.getLogger("pc-monitor")
CLIENTS: set[Any] = set()
LATEST: dict[str, Any] = {}
DEMO = False
INTERVAL = 1.0
SERIAL_PORT = None
PRESENCE_URL = "https://lpbzjbnymyztshjxrbmc.supabase.co"
PRESENCE_KEY = "sb_publishable_RtbKVnBA45ffDLbSGIU9lQ_pxgjHEpg"
PRESENCE_ID = ""
STARTED_AT = time.time()


def unavailable(reason="Indisponível neste computador."):
    return {"value": None, "status": "unavailable", "message": reason}


def demo_metrics() -> dict[str, Any]:
    t = time.time()
    return {"timestamp": t, "demo": True, "connection": "DEMO", "host": {"name": "PC-DEMO", "os": "Windows 11 (demo)", "cpu": "CPU de demonstração", "uptime": 86400},
      "cpu": {"usage": 42 + int(t * 3) % 18, "temperature": 58, "cores": 8, "threads": 16, "frequency_mhz": 4200},
      "gpu": {"name": "GPU de demonstração", "usage": 37, "temperature": 61, "hotspot": unavailable(), "vram": unavailable()},
      "ram": {"total_gb": 32, "used_gb": 14.2, "available_gb": 17.8, "usage": 44},
      "network": {"download_mbps": 120.4, "upload_mbps": 18.2, "ping_ms": 12, "jitter_ms": 2, "packet_loss": 0, "status": "online"},
      "disks": [], "game": {"name": "Nenhum jogo detectado", "process": None, "elapsed": None},
      "discord": {"status": "indisponível", "call": "Informação indisponível por limitação da API ou do sistema."},
      "temperatures": [], "hottest": {"name": "CPU", "celsius": 58}}


def collect() -> dict[str, Any]:
    if DEMO: return demo_metrics()
    vm = psutil.virtual_memory(); boot = psutil.boot_time()
    cpu = psutil.cpu_percent(interval=None); freq = psutil.cpu_freq()
    disks = []
    for p in psutil.disk_partitions(all=False):
        try:
            u = psutil.disk_usage(p.mountpoint)
            disks.append({"device": p.device, "mount": p.mountpoint, "total_gb": round(u.total/1e9, 2), "used_gb": round(u.used/1e9, 2), "free_gb": round(u.free/1e9, 2), "usage": u.percent})
        except OSError: pass
    procs = []
    for p in psutil.process_iter(["name", "create_time"]):
        try:
            n = p.info["name"] or ""; low = n.lower()
            if any(x in low for x in ("steam", "epic", "game", "valorant", "fortnite", "minecraft", "eldenring")):
                procs.append({"name": n, "since": p.info.get("create_time")})
        except (psutil.NoSuchProcess, psutil.AccessDenied): pass
    net = psutil.net_io_counters(); now = time.time(); prev = getattr(collect, "net_prev", (now, net.bytes_recv, net.bytes_sent)); dt = max(now-prev[0], .1); collect.net_prev = (now, net.bytes_recv, net.bytes_sent)
    cpu_temp = unavailable()
    try:
        temps = psutil.sensors_temperatures(); vals = [x.current for group in temps.values() for x in group if x.current is not None]
        if vals: cpu_temp = {"value": round(max(vals), 1), "status": "ok", "source": "psutil"}
    except (AttributeError, OSError): pass
    return {"timestamp": now, "demo": False, "connection": "LOCAL", "host": {"name": socket.gethostname(), "os": f"{platform.system()} {platform.release()}", "cpu": platform.processor() or "Indisponível neste computador.", "uptime": int(now-boot)},
      "cpu": {"usage": round(cpu, 1), "temperature": cpu_temp, "cores": psutil.cpu_count(False), "threads": psutil.cpu_count(True), "frequency_mhz": round(freq.current, 0) if freq else None},
      "gpu": {"name": unavailable(), "usage": unavailable(), "temperature": unavailable(), "hotspot": unavailable(), "vram": unavailable()},
      "ram": {"total_gb": round(vm.total/1e9, 2), "used_gb": round(vm.used/1e9, 2), "available_gb": round(vm.available/1e9, 2), "usage": vm.percent},
      "network": {"download_mbps": round((net.bytes_recv-prev[1])*8/dt/1e6, 2), "upload_mbps": round((net.bytes_sent-prev[2])*8/dt/1e6, 2), "ping_ms": unavailable(), "jitter_ms": unavailable(), "packet_loss": unavailable(), "status": "online"},
      "disks": disks, "game": {"name": procs[0]["name"] if procs else "Nenhum jogo detectado", "process": procs[0] if procs else None, "elapsed": None},
      "discord": {"status": "aberto" if any("discord" in (p.info.get("name") or "").lower() for p in psutil.process_iter(["name"])) else "fechado", "call": "Informação indisponível por limitação da API ou do sistema."},
      "temperatures": [], "hottest": {"name": "CPU", "celsius": cpu_temp.get("value") if cpu_temp.get("value") else None}}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type="application/json"):
        b = body if isinstance(body, bytes) else body.encode(); self.send_response(code); self.send_header("Content-Type", content_type); self.send_header("Content-Length", str(len(b))); self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path == "/api/metrics": self._send(200, json.dumps(LATEST, ensure_ascii=False))
        elif self.path == "/health": self._send(200, '{"status":"ok"}')
        elif self.path == "/events":
            self.send_response(200); self.send_header("Content-Type", "text/event-stream"); self.send_header("Cache-Control", "no-cache"); self.send_header("Connection", "keep-alive"); self.end_headers()
            try:
                while True: self.wfile.write((f"data: {json.dumps(LATEST, ensure_ascii=False)}\\n\\n").encode()); self.wfile.flush(); time.sleep(INTERVAL)
            except (BrokenPipeError, ConnectionResetError): pass
        else:
            root = Path(__file__).parent.parent / "web" / "index.html"
            self._send(200, root.read_bytes(), "text/html; charset=utf-8")
    def log_message(self, *_): pass


def presence_loop():
    """Register/refresh minimal online presence; no hardware metrics are sent."""
    global PRESENCE_ID
    try:
        path = Path.home() / ".pc-monitor-agent-id"
        if path.exists(): PRESENCE_ID = path.read_text().strip()
        if not PRESENCE_ID:
            PRESENCE_ID = uuid.uuid4().hex + uuid.uuid4().hex
            path.write_text(PRESENCE_ID)
        payload = {"agent_id": PRESENCE_ID, "display_name": socket.gethostname(), "operating_system": f"{platform.system()} {platform.release()}", "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(STARTED_AT)), "last_seen": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "agent_version": "0.2.0"}
        url = PRESENCE_URL.rstrip("/") + "/rest/v1/agent_presence"
        while True:
            payload["last_seen"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            data = json.dumps(payload).encode(); req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type":"application/json", "apikey":PRESENCE_KEY, "Authorization":"Bearer "+PRESENCE_KEY, "Prefer":"resolution=merge-duplicates"})
            try:
                urllib.request.urlopen(req, timeout=8).read()
            except urllib.error.HTTPError as e:
                if e.code not in (409,): LOG.debug("presence HTTP %s", e.code)
            except Exception as e: LOG.debug("presence unavailable: %s", e)
            time.sleep(15)
    except Exception as e: LOG.warning("Presença desativada: %s", e)


def serial_loop():
    if not SERIAL_PORT: return
    try:
        import serial
        with serial.Serial(SERIAL_PORT, 115200, timeout=1) as s:
            while True: s.write((json.dumps(LATEST, ensure_ascii=False)+"\\n").encode()); time.sleep(INTERVAL)
    except Exception as e: LOG.warning("USB indisponível: %s", e)


def main():
    global DEMO, INTERVAL, SERIAL_PORT, LATEST
    ap = argparse.ArgumentParser(); ap.add_argument("--demo", action="store_true"); ap.add_argument("--port", type=int, default=8765); ap.add_argument("--interval", type=float, default=1); ap.add_argument("--serial"); ap.add_argument("--no-presence", action="store_true", help="não registrar presença online"); args = ap.parse_args(); DEMO, INTERVAL, SERIAL_PORT = args.demo, max(.2,args.interval), args.serial
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    def updater():
        global LATEST
        while True:
            LATEST = collect(); time.sleep(INTERVAL)
    threading.Thread(target=updater, daemon=True).start(); threading.Thread(target=serial_loop, daemon=True).start();
    if not args.no_presence: threading.Thread(target=presence_loop, daemon=True).start()
    LOG.info("PC Monitor em http://127.0.0.1:%s (%s)", args.port, "DEMO" if DEMO else "LOCAL")
    ThreadingHTTPServer(("0.0.0.0", args.port), Handler).serve_forever()
if __name__ == "__main__": main()
