// src/utils/logger.js

export const abenaLogger = {
  logError: (msg) => {
    // You can customize this to write to file or external service later
    console.error("[AbenaError]", msg);
  },

  logActivity: (msg) => {
    console.log("[AbenaActivity]", msg);
  }
};
