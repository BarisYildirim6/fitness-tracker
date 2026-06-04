import { readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const checkOnly = process.argv.includes("--check");
const roots = ["src"];
const extensions = new Set([".css", ".json", ".ts", ".tsx"]);

function extensionOf(path) {
  const index = path.lastIndexOf(".");
  return index === -1 ? "" : path.slice(index);
}

function collectFiles(root) {
  return readdirSync(root).flatMap((entry) => {
    const path = join(root, entry);
    const stat = statSync(path);
    if (stat.isDirectory()) {
      return collectFiles(path);
    }
    return extensions.has(extensionOf(path)) ? [path] : [];
  });
}

const changed = [];

for (const file of roots.flatMap(collectFiles)) {
  const current = readFileSync(file, "utf8");
  const formatted = `${current
    .replace(/\r\n/g, "\n")
    .split("\n")
    .map((line) => line.replace(/[ \t]+$/g, ""))
    .join("\n")
    .replace(/\n*$/g, "")}\n`;

  if (current !== formatted) {
    changed.push(file);
    if (!checkOnly) {
      writeFileSync(file, formatted);
    }
  }
}

if (changed.length > 0) {
  console.error(`${checkOnly ? "Formatting issues found" : "Formatted"}:\n${changed.join("\n")}`);
  if (checkOnly) {
    process.exit(1);
  }
}
