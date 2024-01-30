import { defineConfig, splitVendorChunkPlugin } from "vite";
// import nodePolyfills from "rollup-plugin-polyfill-node";
import analyze from "rollup-plugin-analyzer";

export default defineConfig({
  // plugins: [react()],
  root: "src",
  base: "/app", // makes assets relative rather than absolute
  plugins: [splitVendorChunkPlugin()],
  build: {
    outDir: "../dist",
    emptyOutDir: true,
    rollupOptions: {
      plugins: [
        // Enable rollup polyfills plugin
        // used during production bundling
        // nodePolyfills({ include: null }),
        // analyze({ limit: 20 }),
      ],
    },
  },
});
