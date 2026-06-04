import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("App", () => {
  it("renders the login route for unauthenticated users", async () => {
    window.history.pushState({}, "", "/");
    const queryClient = new QueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>,
    );

    expect(await screen.findByRole("heading", { name: /log in/i })).toBeInTheDocument();
  });
});
