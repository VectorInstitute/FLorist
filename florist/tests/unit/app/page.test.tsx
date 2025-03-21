import "@testing-library/jest-dom";
import { describe, it, expect } from "@jest/globals";
import { render } from "@testing-library/react";

import Home from "../../../app/page";

describe("Home page", () => {
    it("renders correctly", () => {
        const { container } = render(<Home />);
        const element = container.querySelector("h1.home-page-title");
        expect(element).toBeInTheDocument();
        expect(element).toHaveTextContent("FLorist");
        const paragraph = container.querySelector("p.home-page-paragraph");
        expect(paragraph).toBeInTheDocument();
    });
});
