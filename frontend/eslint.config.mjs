/**
 * FolderChef — ESLint Configuration
 * ====================================
 *
 * ESLint is a tool that checks your JavaScript/TypeScript code for errors
 * and style issues. Think of it as a spell-checker for code.
 *
 * This configuration uses Next.js recommended rules, which include:
 *   - React best practices
 *   - Accessibility checks
 *   - Next.js specific rules
 */

import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
];

export default eslintConfig;
