import "@testing-library/jest-dom";
import { fireEvent, render, screen } from "@testing-library/react";

import Home from "../../../app/page";

describe("Home page", () => {
    it("renders correctly", () => {
        const { container } = render(<Home />);
        const span = container.querySelector("span");
        expect(span).toBeInTheDocument();
        expect(span).toHaveTextContent("Content goes here");
    });
});
