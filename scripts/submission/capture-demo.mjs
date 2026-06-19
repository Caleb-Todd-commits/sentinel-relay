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

    async function waitForText(text, timeoutMs = 75_000) {
      const deadline = Date.now() + timeoutMs;
      while (Date.now() < deadline) {
        if (await evaluate(`document.body.innerText.includes(${JSON.stringify(text)})`)) return;
        await sleep(350);
      }
      throw new Error(`Timed out waiting for text: ${text}`);
    }

    async function waitForCustomResponses(timeoutMs = 75_000) {
      const deadline = Date.now() + timeoutMs;
      while (Date.now() < deadline) {
        const count = await evaluate(`(() => {
          const match = document.body.innerText.match(/([1-6]) of 6 agents responded/);
          return match ? Number(match[1]) : 0;
        })()`);
        if (count > 0) return count;
        await sleep(500);
      }
      return 0;
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

    await navigate(baseUrl);
    await capture("workspace.png");

    await clickButton("Start investigation");
    await waitForText("Approve scoped containment");
    await capture("approval.png");

    await clickButton("Approve containment →");
    await waitForText("Accountable response");
    await capture("result.png");

    await scrollToText("Describe a security problem");
    const filled = await evaluate(`(() => {
      const textarea = document.querySelector('textarea');
      if (!textarea) return false;
      const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set;
      setter?.call(textarea, "After a Friday configuration deployment, unfamiliar IP addresses accessed our customer export endpoint. We rotated the service credential but need to determine whether records were accessed and which containment steps are safe.");
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
      return true;
    })()`);
    if (!filled) throw new Error("Custom incident textarea was not available.");
    await clickButton("Investigate");
    let customResponses = await waitForCustomResponses();
    if (customResponses === 0) {
      await sleep(12_000);
      await clickButton("Run again");
      customResponses = await waitForCustomResponses();
    }
    if (customResponses === 0) throw new Error("No custom-incident agent returned a response.");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1440,
      height: 1400,
      deviceScaleFactor: 1,
      mobile: false,
    });
    await scrollToText("Describe a security problem");
    await capture("custom-question.png");

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
