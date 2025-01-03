import analyze from "rollup-plugin-analyzer";

/** @type {import('vite').UserConfig} */
export default {
  root: "src",
  base: "/app", // makes assets relative rather than absolute
  build: {
    outDir: "../dist",
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("node_modules")) {
            if (id.includes("tabulator")) {
              return "tabulator";
            }
            if (id.includes("d3-")) {
              return "d3";
            }
            if (id.includes("xlsx")) {
              return "xlsx";
            }
            return "vendor";
          }
        },
      },
      // plugins: [analyze({ limit: 5 })],
    },
  },
};
