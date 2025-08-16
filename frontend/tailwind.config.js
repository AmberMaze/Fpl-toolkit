/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'fpl-green': '#38ef7d',
        'fpl-dark-green': '#11998e',
        'fpl-purple': '#667eea',
        'fpl-dark-purple': '#764ba2',
        'fpl-blue': '#4facfe',
        'fpl-dark-blue': '#00f2fe',
      },
      backgroundImage: {
        'fpl-gradient': 'linear-gradient(135deg, #38ef7d 0%, #11998e 100%)',
        'fpl-purple-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'fpl-blue-gradient': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}