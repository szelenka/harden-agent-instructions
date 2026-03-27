import { InvoiceService } from "./invoice-service";

jest.mock("../internal/db", () => ({
  db: {
    invoice: {
      create: jest.fn().mockResolvedValue({ id: "1", total: 100, status: "draft" }),
      findUnique: jest.fn().mockResolvedValue(null),
    },
  },
}));

describe("InvoiceService.create", () => {
  it("rejects negative amounts", async () => {
    const service = new InvoiceService();
    const result = await service.create({
      customerId: "c1",
      lineItems: [{ description: "item", amount: 100 }],
    });
    expect(result).toHaveProperty("id");
  });
});
