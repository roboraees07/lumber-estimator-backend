module.exports = {
  apps: [
    {
      name: "lumber-estimator",
      script: "app.py", 
      cwd: ".",
      interpreter: "python3",
      env: {
        GEMINI_API_KEY: "AIzaSyBR3dEcLQW_efOA2aItE58e9HN9ZIMj1Xg",
        DATABASE_PATH: "data/lumber_estimator.db",
        HOST: "0.0.0.0",
        PORT: "8003",
        LOG_LEVEL: "info",
        CORS_ORIGINS: "http://localhost:3000,http://localhost:8000",
        ENVIRONMENT: "development",
      },
      watch: false,
    },
  ],
};
