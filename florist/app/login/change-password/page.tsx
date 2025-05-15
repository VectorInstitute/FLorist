"use client";
import { ReactElement, useState, useEffect } from "react";

import Image from "next/image";
import { useRouter } from "next/navigation";

import logo_ct from "../../assets/img/logo-ct.png";
import { usePost } from "../../hooks";
import { setToken, removeToken, hashWord } from "../../auth";
import { DEFAULT_USERNAME } from "../page";

export default function ChangePasswordPage(): ReactElement {
    const router = useRouter();
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmNewPassword, setConfirmNewPassword] = useState("");
    const [passwordError, setPasswordError] = useState<string | null>(null);
    const { post, response, isLoading, error } = usePost();

    async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setPasswordError(null);

        if (isLoading) {
            // Preventing double submit if already in progress
            return;
        }

        if (newPassword !== confirmNewPassword) {
            setPasswordError("New password and confirm new password do not match.");
            return;
        }

        const formData = new FormData();
        formData.append("grant_type", "password");
        formData.append("username", DEFAULT_USERNAME);
        formData.append("current_password", hashWord(currentPassword));
        formData.append("new_password", hashWord(newPassword));

        await post("/api/server/auth/change_password", formData, null);
    }

    useEffect(() => {
        // if no response or isLoading, it means the user just accessed the change password page
        if (!response || !isLoading) {
            // remove the login token from the cookies in that case to log the user out
            removeToken();
        }

        // if there is a response and no error, it means the user has changed
        // the password and logged in successfully
        if (response && !error && !passwordError) {
            // redirect to the home page and store the login token in the cookies
            setToken(response.access_token);
            router.push("/");
        }
    }, [response, isLoading, router, error, passwordError]);

    let button_classes = "btn w-100 my-4 mb-2";
    if (isLoading || response) {
        button_classes += " bg-gradient-secondary disabled";
    } else {
        button_classes += " bg-gradient-primary";
    }

    return (
        <div id="change-password-page">
            <div className="card z-index-0 fadeIn3 fadeInBottom">
                <div className="card-header p-0 position-relative mt-n4 mx-3 z-index-2">
                    <div className="bg-gradient-primary shadow-primary border-radius-lg py-3 pe-1">
                        <h4 id="change-password-header" className="text-white font-weight-bolder text-center mt-2 mb-0">
                            <Image
                                src={logo_ct}
                                className="navbar-brand-img h-100"
                                alt="main_logo"
                                width={50}
                                height={50}
                            />
                            <span>Change Password</span>
                            <div className="spacer"></div>
                        </h4>
                    </div>
                </div>
                <div className="card-body">
                    <form id="change-password-form" onSubmit={onSubmit} role="form" className="text-start">
                        <div className="input-group input-group-outline my-3">
                            <label className="form-label">Current Password</label>
                            <input
                                id="change-password-form-current-password"
                                type="password"
                                className="form-control"
                                value={currentPassword}
                                onChange={(e) => setCurrentPassword(e.target.value)}
                            />
                        </div>
                        <div className="input-group input-group-outline my-3">
                            <label className="form-label">New Password</label>
                            <input
                                id="change-password-form-new-password"
                                type="password"
                                className="form-control"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                            />
                        </div>
                        <div className="input-group input-group-outline my-3">
                            <label className="form-label">Confirm New Password</label>
                            <input
                                id="change-password-form-confirm-new-password"
                                type="password"
                                className="form-control"
                                value={confirmNewPassword}
                                onChange={(e) => setConfirmNewPassword(e.target.value)}
                            />
                        </div>
                        <div className="text-center">
                            <button id="change-password-form-submit" type="submit" className={button_classes}>
                                {isLoading || response ? "Changing Password..." : "Change Password"}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            {error || passwordError ? (
                <div id="change-password-error" className="alert alert-danger text-white" role="alert">
                    <span className="text-sm">{passwordError || "An error occurred. Please try again."}</span>
                </div>
            ) : null}
        </div>
    );
}
