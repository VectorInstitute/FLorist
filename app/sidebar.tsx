import logo_ct from "./assets/img/logo-ct.png"

import Image from 'next/image'

export default function Sidebar() {
    return (
        <aside className="sidenav navbar navbar-vertical navbar-expand-xs border-0 border-radius-xl my-3 fixed-start ms-3   bg-gradient-dark" id="sidenav-main">
            <div className="sidenav-header">
                <i className="fas fa-times p-3 cursor-pointer text-white opacity-5 position-absolute end-0 top-0 d-none d-xl-none" aria-hidden="true" id="iconSidenav"></i>
                <span className="navbar-brand m-0">
                    <Image src={logo_ct} className="navbar-brand-img h-100" alt="main_logo" width={32} height={32}/>
                    <span className="ms-1 font-weight-bold text-white">FLorist</span>
                </span>
            </div>
            <hr className="horizontal light mt-0 mb-2" />
            <div className="collapse navbar-collapse  w-auto  max-height-vh-100" id="sidenav-collapse-main">
                <ul className="navbar-nav">
                    <li className="nav-item">
                        <a className="nav-link text-white active bg-gradient-primary" href="#">
                            <div className="text-white text-center me-2 d-flex align-items-center justify-content-center">
                                <i className="material-icons opacity-10">home</i>
                            </div>
                            <span className="nav-link-text ms-1">Home</span>
                        </a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link text-white " href="about.html">
                            <div className="text-white text-center me-2 d-flex align-items-center justify-content-center">
                                <b style={{padding: "0 7px"}}>?</b>
                            </div>
                            <span className="nav-link-text ms-1">About</span>
                        </a>
                    </li>
                </ul>
            </div>
        </aside>
    );
}
