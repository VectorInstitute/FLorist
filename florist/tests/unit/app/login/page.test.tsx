import "@testing-library/jest-dom";
import { fireEvent, render } from "@testing-library/react";
import { describe, it, expect, afterEach, beforeEach } from "@jest/globals";
import { act } from "react-dom/test-utils";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";

import LoginPage, { DEFAULT_USERNAME } from "../../../../app/login/page";
import { usePost } from "../../../../app/hooks";

jest.mock("../../../../app/hooks");
jest.mock("next/navigation");
afterEach(() => {
    jest.clearAllMocks();
});

function mockUsePost(postMock: jest.Mock, response: Object | null, isLoading: boolean, error: string | null) {
    return {
        post: postMock,
        response: response,
        isLoading: isLoading,
        error: error,
    };
}

function setupMocks(response: Object | null, isLoading: boolean, error: string | null) {
    const postMock = jest.fn();
    usePost.mockImplementation(() => mockUsePost(postMock, response, isLoading, error));

    const routerMock = { push: jest.fn() };
    useRouter.mockImplementation(() => routerMock);
    return { postMock, routerMock };
}

describe("LoginPage", () => {
    it("Renders correctly", () => {
        setupMocks(null, false, null);
        const { container } = render(<LoginPage />);

        const loginTitle = container.querySelector("h4#login-header");
        expect(loginTitle).toHaveTextContent("Log In");

        const loginForm = container.querySelector("form#login-form");
        const passwordInput = loginForm.querySelector("input#login-form-password");
        expect(passwordInput).toBeInTheDocument();
        expect(passwordInput).toHaveAttribute("type", "password");
        const submitButton = loginForm.querySelector("button#login-form-submit");
        expect(submitButton).toHaveClass("bg-gradient-primary");
        expect(submitButton).toHaveTextContent("Log in");

        expect(container.querySelector("div#login-error")).toBeNull();
    });
    it("Disables the submit button when the form is loading", () => {
        setupMocks(null, true, null);
        const { container } = render(<LoginPage />);

        const loginForm = container.querySelector("form#login-form");
        const submitButton = loginForm.querySelector("button#login-form-submit");
        expect(submitButton).toHaveClass("bg-gradient-secondary disabled");
        expect(submitButton).toHaveTextContent("Logging in...");
    });
    it("Displays an error message if there is an error", () => {
        setupMocks(null, false, "Invalid username or password");

        const { container } = render(<LoginPage />);

        const errorMessage = container.querySelector("div#login-error");
        expect(errorMessage).toHaveTextContent("An error occurred. Please try again.");
    });

    describe("Token Handling", () => {
        beforeEach(() => {
            Cookies.remove("token");
        });
        it("Removes the token cookie if it exists", () => {
            Cookies.set("token", "test-token");
            expect(Cookies.get("token")).toBe("test-token");
            setupMocks(null, false, null);

            render(<LoginPage />);

            expect(Cookies.get("token")).toBeUndefined();
        });
        it("Sets the token cookie and redirect to the home page if the response contains the token", () => {
            const { routerMock } = setupMocks({ access_token: "test-token" }, false, null);
            expect(Cookies.get("token")).toBeUndefined();

            render(<LoginPage />);

            expect(Cookies.get("token")).toBe("test-token");
            expect(routerMock.push).toHaveBeenCalledWith("/");
        });
        it("Redirects to the change password page if the response contains the change password flag", () => {
            const { routerMock } = setupMocks(
                { access_token: "test-token", should_change_password: true },
                false,
                null,
            );
            expect(Cookies.get("token")).toBeUndefined();

            render(<LoginPage />);

            expect(routerMock.push).toHaveBeenCalledWith("/login/change-password");
            expect(Cookies.get("token")).toBeUndefined();
        });
    });

    describe("Form Submission", () => {
        it("Submits the form correctly", async () => {
            const { postMock } = setupMocks(null, false, null);
            const { container } = render(<LoginPage />);

            const loginForm = container.querySelector("form#login-form");

            const passwordInput = loginForm.querySelector("input#login-form-password");
            act(() => {
                fireEvent.change(passwordInput, { target: { value: "test-password" } });
            });

            const submitButton = loginForm.querySelector("button#login-form-submit");
            await act(async () => await submitButton.click());

            const formData = new FormData();
            formData.append("grant_type", "password");
            formData.append("username", DEFAULT_USERNAME);
            formData.append("password", "c638833f69bbfb3c267afa0a74434812436b8f08a81fd263c6be6871de4f1265");
            expect(postMock).toBeCalledWith("/api/server/auth/token", formData, null);
        });
    });
});
