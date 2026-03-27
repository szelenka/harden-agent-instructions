import { db } from "../internal/db";

interface CreateInvoiceInput {
  customerId: string;
  lineItems: { description: string; amount: number }[];
}

export class InvoiceService {
  async create(input: CreateInvoiceInput) {
    const total = input.lineItems.reduce((sum, li) => sum + li.amount, 0);
    return db.invoice.create({
      data: {
        customerId: input.customerId,
        total,
        status: "draft",
        lineItems: { create: input.lineItems },
      },
      include: { lineItems: true },
    });
  }

  async getById(id: string) {
    return db.invoice.findUnique({ where: { id }, include: { lineItems: true } });
  }
}
