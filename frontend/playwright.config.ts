import { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
  use: {
    baseURL: 'http://localhost:5173', // Adjust if your dev server uses a different port
  },
  webServer: {
    command: 'pnpm run dev',
    port: 5173, // Adjust if your dev server uses a different port
    reuseExistingServer: !process.env.CI,
  },
};

export default config;