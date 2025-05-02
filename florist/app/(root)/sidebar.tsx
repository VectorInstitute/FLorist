"use client";

import logo_ct from "../assets/img/logo-ct.png";

import { ReactElement } from "react";

import Image from "next/image";
import { usePathname, redirect } from "next/navigation";
import Link from "next/link";
import Cookies from "js-cookie";

import { useCheckToken } from "../hooks";

export default function Sidebar(): ReactElement {
    const pathname = usePathname();

    useCheckToken();

    // Redirecting to login page if there is no login token or if the token is invalid
    const componentType = typeof window === "undefined" ? "server" : "client";
    if (componentType == "client") {
        const token = Cookies.get("token");
        if (!token) {
            redirect("/login");
        } else {

        }
    }

    return (
        <aside
            className="sidenav navbar navbar-vertical navbar-expand-xs border-0 border-radius-xl my-3 fixed-start ms-3  bg-gradient-dark"
            id="sidenav-main"
        >
            <div className="sidenav-header">
                <i
                    className="fas fa-times p-3 cursor-pointer text-white opacity-5 position-absolute end-0 top-0 d-none d-xl-none"
                    aria-hidden="true"
                    id="iconSidenav"
                ></i>
                <span className="navbar-brand m-0">
                    <Image src={logo_ct} className="navbar-brand-img h-100" alt="main_logo" width={32} height={32} />
                    <span className="ms-1 font-weight-bold text-white">FLorist</span>
                </span>
            </div>
            <hr className="horizontal light mt-0 mb-2" />
            <div className="collapse navbar-collapse  w-auto  max-height-vh-100" id="sidenav-collapse-main">
                <ul className="navbar-nav">
                    <li className="nav-item">
                        <Link
                            className={`nav-link text-white ${pathname === "/" ? "active bg-gradient-primary" : ""}`}
                            href="/"
                            passHref
                        >
                            <div className="text-white text-center me-2 d-flex align-items-center justify-content-center">
                                <i className="material-icons opacity-10">home</i>
                            </div>
                            <span className="nav-link-text ms-1">Home</span>
                        </Link>
                    </li>
                    <li className="nav-item">
                        <Link
                            className={`nav-link text-white ${pathname.startsWith("/jobs") ? "active bg-gradient-primary" : ""}`}
                            href="/jobs"
                            passHref
                        >
                            <div className="text-white text-center me-2 d-flex align-items-center justify-content-center">
                                <i className="material-icons opacity-10">list</i>
                            </div>
                            <span className="nav-link-text ms-1">Jobs</span>
                        </Link>
                    </li>
                </ul>
            </div>
        </aside>
    );
}
