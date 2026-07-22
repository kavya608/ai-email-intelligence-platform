import { NavLink } from "react-router-dom";
import {
    LayoutDashboard,
    Mail,
    BarChart3
} from "lucide-react";
import logo from "../assets/logo.png";
import "../styles/Sidebar.css";
function Sidebar() {

    return (


        <div className="sidebar">
            <div className="sidebar-logo">
                <img src={logo} alt="AI Email Logo" />
                <div className="logo-text">
                    <h2>AI Email</h2>
                    <p>Intelligence Platform</p>
                </div>
            </div>

            
            <nav>

                <NavLink to="/" className={({ isActive }) => (isActive ? "active" : "")}>
                    <LayoutDashboard size={20}/>
                    Dashboard
                </NavLink>

                <NavLink to="/emails" className={({ isActive }) => (isActive ? "active" : "")}>
                    <Mail size={20}/>
                    Emails
                </NavLink>

                <NavLink to="/analytics" className={({ isActive }) => (isActive ? "active" : "")}>
                    <BarChart3 size={20}/>
                    Analytics
                </NavLink>

            </nav>

        </div>

    );

}

export default Sidebar;