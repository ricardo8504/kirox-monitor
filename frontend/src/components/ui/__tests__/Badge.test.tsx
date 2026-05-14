import { render, screen } from "@testing-library/react";
import { Badge } from "../Badge";

describe("Badge", () => {
  it("renders text", () => {
    render(<Badge>online</Badge>);
    expect(screen.getByText("online")).toBeInTheDocument();
  });

  it("applies success variant class", () => {
    const { container } = render(<Badge variant="success">OK</Badge>);
    expect(container.firstChild).toHaveClass("bg-green-900/50");
  });

  it("applies danger variant class", () => {
    const { container } = render(<Badge variant="danger">Error</Badge>);
    expect(container.firstChild).toHaveClass("bg-red-900/50");
  });
});
