import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["core/**/*.test.ts", "domains/**/*.test.ts", "tests/**/*.test.ts"],
    environment: "node",
    reporters: "default",
  },
});
