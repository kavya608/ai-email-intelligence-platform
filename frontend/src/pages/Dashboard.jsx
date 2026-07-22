import { useEffect, useState } from "react";
import API from "../api/axios";
import StatCard from "../components/StatCard";
import "../styles/Dashboard.css";
import {
    Mail,
    TriangleAlert,
    Gauge,
    CircleAlert,
    Flame
} from "lucide-react";
import Loader from "../components/Loader";


function Dashboard() {

    const [stats, setStats] = useState(null);


    useEffect(() => {

        API.get("/dashboard/stats")
        .then(response => {
            setStats(response.data);
        })
        .catch(error => {
            console.log(error);
        });

    }, []);


    if (!stats) {
        return <Loader />;
    }

    return (

    <div className="dashboard">

        <div className="dashboard-header">

            <h1>🏠 Dashboard</h1>

            <p>
                Welcome back! Here's an overview of your email intelligence platform.
            </p>

        </div>

        <div className="stats-container">

            <StatCard
                title="Total Emails"
                value={stats.total_emails}
                icon={<Mail size={28} />}
                color="#2563EB"
            />

            <StatCard
                title="Action Needed"
                value={stats.action_needed_emails}
                icon={<TriangleAlert size={28} />}
                color="#EF4444"
            />

            <StatCard
                title="Average Priority"
                value={stats.average_priority}
                icon={<Gauge size={28} />}
                color="#10B981"
            />

            <StatCard
                title="Spam Percentage"
                value={`${stats.spam_percentage}%`}
                icon={<CircleAlert size={28} />}
                color="#F59E0B"
            />

            <StatCard
                title="Urgent Emails"
                value={stats.urgent_emails}
                icon={<Flame size={28} />}
                color="#DC2626"
            />

        </div>

    </div>

);
}


export default Dashboard;