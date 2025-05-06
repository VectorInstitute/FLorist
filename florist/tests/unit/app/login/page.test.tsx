import "@testing-library/jest-dom";
import { render } from "@testing-library/react";
import { describe, it, expect, afterEach } from "@jest/globals";
import { usePost } from "../../../../app/hooks";
import Cookies from "js-cookie";
import LoginPage from "../../../../app/login/page";

jest.mock("../../../../app/hooks");
jest.mock("next/navigation", () => ({
    useRouter: jest.fn(),
}));
afterEach(() => {
    jest.clearAllMocks();
});

function mockUsePost(postMock, isLoading) {
    return {
        post: postMock,
        response: null,
        isLoading: isLoading,
        error: null,
    };
}

function setupMock(isLoading: boolean) {
    const postMock = jest.fn();
    usePost.mockImplementation(() => mockUsePost(postMock, isLoading));
    return postMock;
}

describe("LoginPage", () => {
    it("Renders correctly", () => {
        setupMock(false);
        const { container } = render(<LoginPage />);

        const loginTitle = container.querySelector("h4#login-header");
        expect(loginTitle).toHaveTextContent("Log In");

        const loginForm = container.querySelector("form#login-form");
        const passwordInput = loginForm.querySelector("input#login-form-password");
        expect(passwordInput).toBeInTheDocument();
        expect(passwordInput).toHaveAttribute("type", "password");
        const submitButton = loginForm.querySelector("button#login-form-submit");
        expect(submitButton).toHaveClass("bg-gradient-primary");
    });
    it("Disables the submit button when the form is loading", () => {
        setupMock(true);
        const { container } = render(<LoginPage />);

        const loginForm = container.querySelector("form#login-form");
        const submitButton = loginForm.querySelector("button#login-form-submit");
        expect(submitButton).toHaveClass("bg-gradient-secondary disabled");
    });
    it("Removes the token cookie if it exists", () => {
        Cookies.set("token", "test-token");
        expect(Cookies.get("token")).toBe("test-token");
        setupMock(false);

        render(<LoginPage />);

        expect(Cookies.get("token")).toBeUndefined();
    });
});
