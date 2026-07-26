import { describe, expect, it } from "vitest";
import { baggagePreviewPrice, formatMoney, normalizePnr, validateContactInput } from "./utils";

describe("formatMoney", () => {
  it("formats ruble cents for RU locale", () => {
    expect(formatMoney(3500)).toContain("35");
  });
});

describe("baggagePreviewPrice", () => {
  it("calculates first piece price", () => {
    expect(baggagePreviewPrice(1, 20)).toBe(3500);
  });

  it("adds extra piece and overweight fees", () => {
    expect(baggagePreviewPrice(2, 25)).toBe(8500);
  });
});

describe("normalizePnr", () => {
  it("trims and uppercases input in normal mode", () => {
    expect(normalizePnr(" tc1001 ")).toBe("TC1001");
  });
});

describe("validateContactInput", () => {
  it("accepts valid email and phone", () => {
    expect(validateContactInput("valid@example.test", "+79991234567")).toEqual([]);
  });

  it("returns both validation errors", () => {
    expect(validateContactInput("bad", "12")).toHaveLength(2);
  });
});
