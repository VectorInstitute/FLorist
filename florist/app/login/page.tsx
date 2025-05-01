import { ReactElement } from "react";

import Image from "next/image";

import logo_ct from "../assets/img/logo-ct.png";

export default function LoginPage(): ReactElement {
    return (
        <div className="card z-index-0 fadeIn3 fadeInBottom">
            <div className="card-header p-0 position-relative mt-n4 mx-3 z-index-2">
                <div className="bg-gradient-primary shadow-primary border-radius-lg py-3 pe-1">
                    <h4 id="login-header" className="text-white font-weight-bolder text-center mt-2 mb-0">
                        <Image src={logo_ct} className="navbar-brand-img h-100" alt="main_logo" width={32} height={32} />
                        <span>Log In</span>
                    </h4>
                </div>
            </div>
            <div className="card-body">
                <form role="form" className="text-start">
                    <div className="input-group input-group-outline my-3">
                        <label className="form-label">Password</label>
                        <input type="password" className="form-control"></input>
                    </div>
                    <div className="text-center">
                        <button type="button" className="btn bg-gradient-primary w-100 my-4 mb-2">
                            Sign in
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
