import logo_ct from "../assets/img/logo-ct.png";

import { ReactElement } from "react";
import Image from "next/image";

export default function Home(): ReactElement {
    return (
        <div>
            <h1 className="home-page-title">
                <Image src={logo_ct} className="navbar-brand-img h-100" alt="main_logo" width={80} height={80} />
                <span className="ms-1 font-weight-bold">FLorist</span>
            </h1>
            <p className="home-page-paragraph">
                FLorist is a platform to launch and monitor Federated Learning (FL) training jobs.
            </p>
            <p className="home-page-paragraph">
                Its goal is to bridge the gap between state-of-the-art FL algorithm implementations and their
                applications by providing a system to easily kick off, orchestrate, manage, collect, and summarize the
                results of FL4Health training jobs.
            </p>
            <p className="home-page-paragraph">
                You can start a new training job by going to the <span className="font-weight-bold">Jobs</span> page and
                clicking the <span className="font-weight-bold">New Job</span> button.
            </p>
        </div>
    );
}
