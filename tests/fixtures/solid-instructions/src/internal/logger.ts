// Minimal structured logger (would use pino in production)
export const logger = {
  info: (data: Record<string, unknown>, msg: string) =>
    console.log(JSON.stringify({ level: "info", msg, ...data })),
  error: (data: Record<string, unknown>, msg: string) =>
    console.error(JSON.stringify({ level: "error", msg, ...data })),
};
