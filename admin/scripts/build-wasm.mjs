import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const here = dirname(fileURLToPath(import.meta.url));
const adminRoot = resolve(here, "..");
const demoRoot = resolve(adminRoot, "..");

function selectedSource() {
  if (process.env.KITU_SOURCE_PATH?.trim())
    return resolve(process.env.KITU_SOURCE_PATH);
  const selectionPath = resolve(demoRoot, ".kitu/source.json");
  const selection = JSON.parse(readFileSync(selectionPath, "utf8"));
  if (typeof selection.path !== "string" || !selection.path.trim()) {
    throw new Error(`${selectionPath} does not contain a Kitu source path`);
  }
  return resolve(selection.path);
}

const source = selectedSource();
const packageScript = resolve(
  source,
  "tools/kitu-web-admin/package/scripts/build-wasm.mjs",
);
const crate = resolve(source, "crates/kitu-osc-ir-wasm");
const output = resolve(adminRoot, "static/kitu-osc-ir-wasm");
if (!existsSync(packageScript))
  throw new Error(`Kitu Admin WASM build script is missing: ${packageScript}`);
const result = spawnSync(process.execPath, [packageScript], {
  env: {
    ...process.env,
    KITU_OSC_IR_WASM_CRATE: crate,
    KITU_ADMIN_WASM_OUT_DIR: output,
  },
  stdio: "inherit",
});
if (result.error) throw result.error;
process.exitCode = result.status ?? 1;
