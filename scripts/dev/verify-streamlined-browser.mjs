#!/usr/bin/env node

import { spawn } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";

const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const baseUrl = process.argv[2] ?? "http://127.0.0.1:3000";
const outputDir = path.resolve(process.argv[3] ?? "/tmp/sentinel-relay-streamlined-qa");
const port = 9444;
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitForJson(url, attempts = 120) {
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      const response = await fetch(url);
      if (response.ok) return response.json();
    } catch {}
    await sleep(100);
  }
  throw new Error(`Timed out waiting for ${url}`);
}

class CdpClient {
  constructor(url) {
    this.socket = new WebSocket(url);
    this.nextId = 1;
    this.pending = new Map();
    this.waiters = new Map();
  }

  async open() {
    await new Promise((resolve, reject) => {
      this.socket.addEventListener("open", resolve, { once: true });
      this.socket.addEventListener("error", reject, { once: true });
    });
    this.socket.addEventListener("message", (event) => {
      const message = JSON.parse(String(event.data));
      if (message.id) {
        const pending = this.pending.get(message.id);
        if (!pending) return;
        this.pending.delete(message.id);
        if (message.error) pending.reject(new Error(message.error.message));
        else pending.resolve(message.result ?? {});
        return;
      }
      const waiter = this.waiters.get(message.method);
      if (waiter) {
        this.waiters.delete(message.method);
        waiter.resolve(message.params ?? {});
      }
    });
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }

  waitFor(method, timeoutMs = 15000) {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error(`Timed out waiting for ${method}`)), timeoutMs);
      this.waiters.set(method, { resolve: (value) => { clearTimeout(timeout); resolve(value); } });
    });
  }

  close() { this.socket.close(); }
}

async function main() {
  await fs.mkdir(outputDir, { recursive: true });
  const chrome = spawn(chromePath, [
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--no-first-run",
    `--remote-debugging-port=${port}`,
    "--remote-debugging-address=127.0.0.1",
    `--user-data-dir=/private/tmp/sentinel-relay-streamlined-${Date.now()}`,
    "about:blank",
  ], { stdio: "ignore" });

  let client;
  try {
    const targets = await waitForJson(`http://127.0.0.1:${port}/json/list`);
    const target = targets.find((item) => item.type === "page");
    client = new CdpClient(target.webSocketDebuggerUrl);
    await client.open();
    await client.send("Page.enable");
    await client.send("Runtime.enable");
    await client.send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });

    async function evaluate(expression) {
      const result = await client.send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true, userGesture: true });
      if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
      return result.result?.value;
    }

    async function navigate(url) {
      const loaded = client.waitFor("Page.loadEventFired");
      await client.send("Page.navigate", { url });
      await loaded;
      await sleep(1800);
    }

    async function capture(name) {
      const { data } = await client.send("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: false });
      await fs.writeFile(path.join(outputDir, name), Buffer.from(data, "base64"));
    }

    async function click(label) {
      const clicked = await evaluate(`(() => { const buttons = [...document.querySelectorAll('button')].filter((button) => button.textContent.trim() === ${JSON.stringify(label)} && !button.disabled); if (buttons.length !== 1) return buttons.length; buttons[0].click(); return true; })()`);
      if (clicked !== true) throw new Error(`Expected one enabled ${label} button, found ${clicked}`);
    }

    async function waitForText(text, timeoutMs = 35000) {
      const deadline = Date.now() + timeoutMs;
      while (Date.now() < deadline) {
        const found = await evaluate(`document.body.innerText.includes(${JSON.stringify(text)})`);
        if (found) return;
        await sleep(300);
      }
      await capture("timeout.png");
      console.error(await evaluate("document.body.innerText"));
      throw new Error(`Timed out waiting for text: ${text}`);
    }

    await navigate(baseUrl);
    const panelCount = await evaluate(`[...document.querySelectorAll('[data-product-panel]')].filter((node) => { const rect = node.getBoundingClientRect(); const style = getComputedStyle(node); return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden'; }).length`);
    if (panelCount !== 3) throw new Error(`Expected 3 visible product panels, found ${panelCount}`);
    const banned = await evaluate(`['judge','hackathon','band-style','how it works'].filter((term) => document.body.innerText.toLowerCase().includes(term))`);
    if (banned.length) throw new Error(`Found banned visible terms: ${banned.join(", ")}`);
    await capture("idle.png");

    await click("Start investigation");
    await waitForText("Approve scoped containment");
    await capture("approval.png");
    await click("Approve containment");
    await waitForText("Accountable response");
    await capture("complete.png");
    await click("evidence");
    await waitForText("API gateway activity");

    await navigate(`${baseUrl}/war-room`);
    const redirected = await evaluate(`location.pathname === '/' && location.hash === '#investigation'`);
    if (!redirected) throw new Error("Legacy War Room route did not redirect to the workspace.");

    console.log(`Browser verification passed. Screenshots: ${outputDir}`);
  } finally {
    client?.close();
    chrome.kill("SIGTERM");
  }
}

main().catch((error) => {
  console.error(error.stack ?? error.message ?? String(error));
  process.exitCode = 1;
});
