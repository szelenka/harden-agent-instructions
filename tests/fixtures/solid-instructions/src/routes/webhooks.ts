import { Router } from "express";
import { PaymentService } from "../services/payment-service";

export const webhookRouter = Router();
const payments = new PaymentService();

webhookRouter.post("/payment", async (req, res) => {
  await payments.handleWebhook(req.body);
  res.status(200).end();
});
