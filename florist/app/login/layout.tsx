import "../assets/css/nucleo-icons.css";
import "../assets/css/nucleo-svg.css";
import "../assets/css/material-dashboard.css?v=3.0.0";
import "../assets/css/florist.css";

import { Metadata } from "next";
import { ReactElement } from "react";
import Script from "next/script";

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
                <div className="page-header align-items-start min-vh-100">
                    <div id="content" className="container my-auto">
                        <div className="row">
                            <div className="col-lg-4 col-md-8 col-12 mx-auto">{children}</div>
                        </div>
                    </div>
                </div>

                <ClientImports />
            </body>
        </html>
    );
}
