"use client";
import { ReactElement, useState } from "react";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { createHash } from "crypto";

import logo_ct from "../assets/img/logo-ct.png";
import { usePost } from "../hooks";
import { setToken, removeToken } from "../auth";

const DEFAULT_USERNAME = "admin";

export default function LoginPage(): ReactElement {
    const router = useRouter();
    const [password, setPassword] = useState("");
    const { post, response, isLoading, error } = usePost();

    async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        if (isLoading) {
            // Preventing double submit if already in progress
            return;
        }

        const formData = new FormData();
        formData.append("grant_type", "password");
        formData.append("username", DEFAULT_USERNAME);
        formData.append("password", createHash("sha256").update(password).digest("hex"));

        await post("/api/server/auth/token", formData, null);
    }

    if (!response || !isLoading) {
        // if no response or isLoading, it means the user just accessed the login page
        // remove the login token from the cookies in that case to log the user out
        removeToken();
    }

    if (response) {
        // if there is a response, it means the user has logged in successfully
        // redirect to the home page and store the login token in the cookies
        setToken(response.access_token);
        router.push("/");
    }

    let button_classes = "btn w-100 my-4 mb-2";
    if (isLoading || response) {
        button_classes += " bg-gradient-secondary disabled";
    } else {
        button_classes += " bg-gradient-primary";
    }

    return (
        <div id="login-page">
            <div className="card z-index-0 fadeIn3 fadeInBottom">
                <div className="card-header p-0 position-relative mt-n4 mx-3 z-index-2">
                    <div className="bg-gradient-primary shadow-primary border-radius-lg py-3 pe-1">
                        <h4 id="login-header" className="text-white font-weight-bolder text-center mt-2 mb-0">
                            <Image
                                src={logo_ct}
                                className="navbar-brand-img h-100"
                                alt="main_logo"
                                width={50}
                                height={50}
                            />
                            <span>Log In</span>
                            <div className="spacer"></div>
                        </h4>
                    </div>
                </div>
                <div className="card-body">
                    <form onSubmit={onSubmit} role="form" className="text-start">
                        <div className="input-group input-group-outline my-3">
                            <label className="form-label">Password</label>
                            <input
                                type="password"
                                className="form-control"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                        <div className="text-center">
                            <button type="submit" className={button_classes}>
                                {isLoading || response ? "Logging in..." : "Log in"}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            {error ? (
                <div id="login-error" className="alert alert-danger text-white" role="alert">
                    <span className="text-sm">An error occurred. Please try again.</span>
                </div>
            ) : null}
        </div>
    );
}
