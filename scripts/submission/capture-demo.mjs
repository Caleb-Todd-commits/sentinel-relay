#!/usr/bin/env node

import { spawn } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";

const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const baseUrl = process.argv[2] ?? "https://sentinel-relay-alpha.vercel.app";
const outputDir = path.resolve(process.argv[3] ?? "submission/screenshots");
const port = 9333;
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitForJson(url, attempts = 100) {
  let lastError;
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      const response = await fetch(url);
      if (response.ok) return await response.json();
    } catch (error) {
      lastError = error;
    }
    await sleep(100);
  }
  throw lastError ?? new Error(`Timed out waiting for ${url}`);
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
      const timeout = setTimeout(() => {
        this.waiters.delete(method);
        reject(new Error(`Timed out waiting for ${method}`));
      }, timeoutMs);
      this.waiters.set(method, {
        resolve: (value) => {
          clearTimeout(timeout);
          resolve(value);
        },
      });
    });
  }

  close() {
    this.socket.close();
  }
}

async function main() {
  await fs.mkdir(outputDir, { recursive: true });
  const userDataDir = `/private/tmp/sentinel-relay-cdp-${Date.now()}`;
  const chrome = spawn(
    chromePath,
    [
      "--headless=new",
      "--disable-gpu",
      "--hide-scrollbars",
      "--no-first-run",
      `--remote-debugging-port=${port}`,
      "--remote-debugging-address=127.0.0.1",
      `--user-data-dir=${userDataDir}`,
      "about:blank",
    ],
    { stdio: "ignore" },
  );

  let client;
  try {
    const targets = await waitForJson(`http://127.0.0.1:${port}/json/list`);
    const target = targets.find((item) => item.type === "page");
    if (!target?.webSocketDebuggerUrl) throw new Error("Chrome page target was not available.");

    client = new CdpClient(target.webSocketDebuggerUrl);
    await client.open();
    await client.send("Page.enable");
    await client.send("Runtime.enable");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1440,
      height: 900,
      deviceScaleFactor: 1,
      mobile: false,
    });

    async function navigate(url) {
      const loaded = client.waitFor("Page.loadEventFired");
      await client.send("Page.navigate", { url });
      await loaded;
      await sleep(1800);
    }

    async function evaluate(expression) {
      const result = await client.send("Runtime.evaluate", {
        expression,
        awaitPromise: true,
        returnByValue: true,
        userGesture: true,
      });
      if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
      return result.result?.value;
    }

    async function clickButton(label) {
      const clicked = await evaluate(`(() => {
        const button = [...document.querySelectorAll('button')]
          .find((item) => item.textContent.trim() === ${JSON.stringify(label)} && !item.disabled);
        if (!button) return false;
        button.click();
        return true;
      })()`);
      if (!clicked) throw new Error(`Enabled button not found: ${label}`);
      await sleep(1100);
    }

    async function scrollToText(text) {
      await evaluate(`(() => {
        const node = [...document.querySelectorAll('h1,h2,h3,p,span')]
          .find((item) => item.textContent.trim() === ${JSON.stringify(text)});
        if (!node) return false;
        node.scrollIntoView({ block: 'center', inline: 'nearest' });
        return true;
      })()`);
      await sleep(350);
    }

    async function capture(filename) {
      const { data } = await client.send("Page.captureScreenshot", {
        format: "png",
        fromSurface: true,
        captureBeyondViewport: false,
      });
      await fs.writeFile(path.join(outputDir, filename), Buffer.from(data, "base64"));
    }

    await navigate(`${baseUrl}/war-room`);
    await capture("workflow-00-ready.png");

    await clickButton("Start incident");
    await scrollToText("Band incident room opened");
    await capture("workflow-01-room.png");

    await clickButton("Run next step");
    await clickButton("Run next step");
    await scrollToText("Suspicious token usage identified");
    await capture("workflow-03-evidence.png");

    for (let index = 0; index < 3; index += 1) await clickButton("Run next step");
    await scrollToText("Risk challenges customer-impact claim");
    await capture("workflow-06-challenge.png");

    await clickButton("Run next step");
    await scrollToText("Human approval requested");
    await capture("workflow-07-approval-gate.png");

    await clickButton("Approve containment");
    await scrollToText("Containment approved, disclosure deferred");
    await capture("workflow-08-approved.png");

    await clickButton("Run next step");
    await clickButton("Run next step");
    await scrollToText("Audit-ready report generated");
    await capture("workflow-10-report-ready.png");

    await navigate(`${baseUrl}/report`);
    await capture("workflow-report.png");

    console.log(`Captured workflow screenshots in ${outputDir}`);
  } finally {
    client?.close();
    chrome.kill("SIGTERM");
  }
}

main().catch((error) => {
  console.error(error.stack ?? error.message ?? String(error));
  process.exitCode = 1;
});
