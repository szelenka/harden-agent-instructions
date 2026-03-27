import { Router } from "express";
import { createInvoiceSchema } from "../validators/invoice-schema";
import { InvoiceService } from "../services/invoice-service";

export const invoiceRouter = Router();
const service = new InvoiceService();

invoiceRouter.post("/", async (req, res) => {
  const parsed = createInvoiceSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ errors: parsed.error.issues });
  const invoice = await service.create(parsed.data);
  res.status(201).json(invoice);
});

invoiceRouter.get("/:id", async (req, res) => {
  const invoice = await service.getById(req.params.id);
  if (!invoice) return res.status(404).json({ error: "not found" });
  res.json(invoice);
});
