import "../assets/css/nucleo-icons.css";
import "../assets/css/nucleo-svg.css";
import "../assets/css/material-dashboard.css?v=3.0.0";
import "../assets/css/florist.css";

import { Metadata } from "next";
import { ReactElement } from "react";
import Script from "next/script";

import Sidebar from "./sidebar";
import ClientImports from "../client_imports";

export const metadata: Metadata = {
    title: "Florist",
};

export default function RootLayout({ children }: { children: React.ReactNode }): ReactElement {
    return (
        <html lang="en">
            <head>
                {/*     Fonts and icons     */}
                <link
                    rel="stylesheet"
                    type="text/css"
                    href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700,900|Roboto+Slab:400,700"
                />
                {/*     Font Awesome Icons  */}
                <Script src="https://kit.fontawesome.com/42d5adcbca.js" />
                {/*     Material Icons      */}
                <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Round" rel="stylesheet" />
                {/*     Copyright Notice    */}
                <script
                    dangerouslySetInnerHTML={{
                        __html: `
//                             =========================================================
//                             * Material Dashboard 2 - v3.0.0
//                             =========================================================
//
//                             * Product Page: https://www.creative-tim.com/product/material-dashboard
//                             * Copyright 2021 Creative Tim (https://www.creative-tim.com)
//                             * Licensed under MIT (https://www.creative-tim.com/license)
//                             * Coded by Creative Tim
//
//                             =========================================================
//
//                             * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
                `,
                    }}
                />
            </head>
            <body className="g-sidenav-show  bg-gray-200">
                {/* Sidebar */}
                <Sidebar />
                {/* Body */}
                <main className="main-content position-relative max-height-vh-100 h-100 border-radius-lg ">
                    {/* Navbar */}
                    <nav
                        className="navbar navbar-main navbar-expand-lg px-0 mx-4 shadow-none border-radius-xl"
                        id="navbarBlur"
                        navbar-scroll="true"
                    >
                        <div className="container-fluid py-1 px-3">
                            <nav aria-label="breadcrumb">
                                <ol className="breadcrumb bg-transparent mb-0 pb-0 pt-1 px-0 me-sm-6 me-5">
                                    {/* Breadcrumbs */}
                                </ol>
                            </nav>
                            <div className="collapse navbar-collapse mt-sm-0 mt-2 me-md-0 me-sm-4" id="navbar">
                                <div className="ms-md-auto pe-md-3 d-flex align-items-center">
                                    <div className="input-group input-group-outline">{/* Left aligned elements */}</div>
                                </div>
                            </div>
                        </div>
                    </nav>
                    {/* End Navbar */}
                    <div className="container-fluid py-4">
                        <div className="row min-vh-80 h-100">
                            <div className="col-12">{children}</div>
                        </div>
                        {/* Footer */}
                        <footer className="footer pt-5">
                            <div className="container-fluid">
                                <div className="row align-items-center justify-content-lg-between">
                                    <div className="col-lg-6 mb-lg-0 mb-4">
                                        <div className="copyright text-center text-sm text-muted text-lg-start">
                                            {/* Copyright */}
                                        </div>
                                    </div>
                                    <div className="col-lg-6">
                                        <ul className="nav nav-footer justify-content-center justify-content-lg-end">
                                            {/* Bottom right navbar */}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </footer>
                    </div>
                </main>

                <ClientImports />
            </body>
        </html>
    );
}
