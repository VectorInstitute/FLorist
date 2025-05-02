"use client";
import { ReactElement, useState } from "react";

import Image from "next/image";
import { createHash } from "crypto";

import logo_ct from "../assets/img/logo-ct.png";
import { usePost } from "../hooks";

const DEFAULT_USERNAME = "admin";

export default function LoginPage(): ReactElement {
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

    return (
        <div className="card z-index-0 fadeIn3 fadeInBottom">
            <div className="card-header p-0 position-relative mt-n4 mx-3 z-index-2">
                <div className="bg-gradient-primary shadow-primary border-radius-lg py-3 pe-1">
                    <h4 id="login-header" className="text-white font-weight-bolder text-center mt-2 mb-0">
                        <Image src={logo_ct} className="navbar-brand-img h-100" alt="main_logo" width={50} height={50} />
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
                        <button type="submit" className="btn bg-gradient-primary w-100 my-4 mb-2">
                            Sign in
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
