import { render, screen } from "@testing-library/react";
import { Table } from "../Table";

interface Row {
  id: string;
  name: string;
}

const columns = [
  { key: "name", header: "Name", render: (r: Row) => r.name },
];

const rows: Row[] = [
  { id: "1", name: "Server A" },
  { id: "2", name: "Server B" },
];

describe("Table", () => {
  it("renders headers and rows", () => {
    render(<Table columns={columns} rows={rows} keyFn={(r) => r.id} />);
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Server A")).toBeInTheDocument();
    expect(screen.getByText("Server B")).toBeInTheDocument();
  });

  it("shows empty state when no rows", () => {
    render(
      <Table
        columns={columns}
        rows={[]}
        keyFn={(r) => r.id}
        emptyContent="Nothing here"
      />,
    );
    expect(screen.getByText("Nothing here")).toBeInTheDocument();
  });

  it("shows loading state", () => {
    render(<Table columns={columns} rows={[]} keyFn={(r) => r.id} loading />);
    expect(screen.getByText("Loading…")).toBeInTheDocument();
  });
});
