import multi from "@rollup/plugin-multi-entry";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import ignore from "rollup-plugin-ignore";

export default {
  input: "build/packages/**/*.js",
  output: {
    dir: "build",
    format: "es",
  },
  plugins: [
    ignore([
      "@material/mwc-icon/mwc-icon",
      "@material/mwc-list",
      "@material/mwc-menu",
      "@material/mwc-ripple/mwc-ripple",
    ]),
    multi({ entryFileName: "index.bundled.js" }),
    nodeResolve(),
  ],
};
