import "@testing-library/jest-dom";
import { fireEvent, render } from "@testing-library/react";
import { describe, it, expect, afterEach } from "@jest/globals";
import { act } from "react-dom/test-utils";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";

import { DEFAULT_USERNAME } from "../../../../../app/login/page";
import ChangePasswordPage from "../../../../../app/login/change-password/page";
import { usePost } from "../../../../../app/hooks";

jest.mock("../../../../../app/hooks");
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

describe("ChangePasswordPage", () => {
    it("Renders correctly", () => {
        setupMocks(null, false, null);
        const { container } = render(<ChangePasswordPage />);

        const pageTitle = container.querySelector("h4#change-password-header");
        expect(pageTitle).toHaveTextContent("Change Password");

        const form = container.querySelector("form#change-password-form");
        const currentPasswordInput = form.querySelector("input#change-password-form-current-password");
        expect(currentPasswordInput).toBeInTheDocument();
        expect(currentPasswordInput).toHaveAttribute("type", "password");
        const newPasswordInput = form.querySelector("input#change-password-form-new-password");
        expect(newPasswordInput).toBeInTheDocument();
        expect(newPasswordInput).toHaveAttribute("type", "password");
        const confirmNewPasswordInput = form.querySelector("input#change-password-form-confirm-new-password");
        expect(confirmNewPasswordInput).toBeInTheDocument();
        expect(confirmNewPasswordInput).toHaveAttribute("type", "password");
        const submitButton = form.querySelector("button#change-password-form-submit");
        expect(submitButton).toHaveClass("bg-gradient-primary");
        expect(submitButton).toHaveTextContent("Change Password");

        expect(container.querySelector("div#change-password-error")).toBeNull();
    });
    it("Disables the submit button when the form is loading", () => {
        setupMocks(null, true, null);
        const { container } = render(<ChangePasswordPage />);

        const form = container.querySelector("form#change-password-form");
        const submitButton = form.querySelector("button#change-password-form-submit");
        expect(submitButton).toHaveClass("bg-gradient-secondary disabled");
        expect(submitButton).toHaveTextContent("Changing Password...");
    });
    it("Displays an error message if there is an error", () => {
        setupMocks(null, false, "Invalid username or password");

        const { container } = render(<ChangePasswordPage />);

        const errorMessage = container.querySelector("div#change-password-error");
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

            render(<ChangePasswordPage />);

            expect(Cookies.get("token")).toBeUndefined();
        });
        it("Sets the token cookie and redirect to the home page if the response contains the token", () => {
            const { routerMock } = setupMocks({ access_token: "test-token" }, false, null);
            expect(Cookies.get("token")).toBeUndefined();

            render(<ChangePasswordPage />);

            expect(Cookies.get("token")).toBe("test-token");
            expect(routerMock.push).toHaveBeenCalledWith("/");
        });
    });

    describe("Form Submission", () => {
        it("Submits the form correctly", async () => {
            const { postMock } = setupMocks(null, false, null);
            const { container } = render(<ChangePasswordPage />);

            const form = container.querySelector("form#change-password-form");

            const currentPasswordInput = form.querySelector("input#change-password-form-current-password");
            const newPasswordInput = form.querySelector("input#change-password-form-new-password");
            const confirmNewPasswordInput = form.querySelector("input#change-password-form-confirm-new-password");
            act(() => {
                fireEvent.change(currentPasswordInput, { target: { value: "current-password" } });
                fireEvent.change(newPasswordInput, { target: { value: "new-password" } });
                fireEvent.change(confirmNewPasswordInput, { target: { value: "new-password" } });
            });

            const submitButton = form.querySelector("button#change-password-form-submit");
            await act(async () => await submitButton.click());

            const formData = new FormData();
            formData.append("grant_type", "password");
            formData.append("username", DEFAULT_USERNAME);
            formData.append("current_password", "595c3e976fe08b24517e583c35b9faef3e8bf103c3355fba7c23f972baee47e8");
            formData.append("new_password", "b8b9f8f23992ebc2617febc03d92ecb1763fba7b77a5d053b69c416bad18a369");
            expect(postMock).toBeCalledWith("/api/server/auth/change_password", formData, null);
        });

        it("Display a password error if the new password and the confirm new password are not the same", async () => {
            const { postMock } = setupMocks(null, false, null);
            const { container } = render(<ChangePasswordPage />);

            const form = container.querySelector("form#change-password-form");

            const currentPasswordInput = form.querySelector("input#change-password-form-current-password");
            const newPasswordInput = form.querySelector("input#change-password-form-new-password");
            const confirmNewPasswordInput = form.querySelector("input#change-password-form-confirm-new-password");
            act(() => {
                fireEvent.change(currentPasswordInput, { target: { value: "current-password" } });
                fireEvent.change(newPasswordInput, { target: { value: "new-password" } });
                fireEvent.change(confirmNewPasswordInput, { target: { value: "wrong-password" } });
            });

            const submitButton = form.querySelector("button#change-password-form-submit");
            await act(async () => await submitButton.click());

            const errorMessage = container.querySelector("div#change-password-error");
            expect(errorMessage).toHaveTextContent("New password and confirm new password do not match.");
            expect(postMock).not.toHaveBeenCalled();
        });
    });
});
