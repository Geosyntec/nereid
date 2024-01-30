/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.html", "./src/**/*.js"],
  theme: {
    extend: {
      translate: {
        double: "200%",
        triple: "300%",
        quad: "400%",
        pent: "500%",
        sext: "600%",
        sept: "700%",
        octa: "800%",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
