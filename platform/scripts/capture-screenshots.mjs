import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";

const outputDir = path.resolve("docs/screenshots");
await fs.mkdir(outputDir, { recursive: true });

const baseUrl = process.env.WEB_URL ?? "http://127.0.0.1:5173";
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 980 } });

async function shot(name) {
  await page.screenshot({ path: path.join(outputDir, name), fullPage: true });
}

await page.goto(baseUrl, { waitUntil: "networkidle" });
await shot("01-login.png");
await page.getByRole("button", { name: "Войти" }).click();
await page.waitForLoadState("networkidle");
await shot("02-search-results.png");
await page.getByRole("button", { name: "Контакты" }).click();
await shot("03-contacts.png");
await page.getByRole("button", { name: "Багаж" }).click();
await shot("04-baggage.png");
await page.getByRole("button", { name: "Возврат" }).click();
await shot("05-refund.png");
await page.getByRole("button", { name: "База знаний" }).click();
await shot("06-knowledge-base.png");
await browser.close();
console.log("Screenshots saved to docs/screenshots");
