import { z } from "zod";

export const createInvoiceSchema = z.object({
  customerId: z.string().uuid(),
  lineItems: z
    .array(
      z.object({
        description: z.string().min(1),
        amount: z.number().positive(),
      })
    )
    .min(1),
});
