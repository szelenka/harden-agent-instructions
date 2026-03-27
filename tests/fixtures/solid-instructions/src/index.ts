import express from "express";
import { invoiceRouter } from "./routes/invoices";
import { webhookRouter } from "./routes/webhooks";
import { logger } from "./internal/logger";

const app = express();
app.use(express.json());
app.use("/invoices", invoiceRouter);
app.use("/webhooks", webhookRouter);

const port = process.env.PORT || 3000;
app.listen(port, () => logger.info({ port }, "server started"));
