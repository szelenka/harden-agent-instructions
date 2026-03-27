import { db } from "../internal/db";
import { logger } from "../internal/logger";

export class PaymentService {
  async handleWebhook(payload: { invoiceId: string; status: string }) {
    const invoice = await db.invoice.findUnique({ where: { id: payload.invoiceId } });
    if (!invoice) {
      logger.error({ invoiceId: payload.invoiceId }, "webhook for unknown invoice");
      return;
    }
    await db.invoice.update({
      where: { id: payload.invoiceId },
      data: { status: payload.status === "paid" ? "paid" : "failed" },
    });
  }
}
