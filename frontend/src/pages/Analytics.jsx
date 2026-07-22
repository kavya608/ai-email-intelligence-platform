import StatCard from "../components/StatCard";
import "../styles/Analytics.css";
import { useState, useEffect } from "react";
import axios from "../api/axios";
import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend,
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid
} from "recharts";

import AnalyticsCard from "../components/AnalyticsCard";
import {
    Mail,
    CircleAlert,
    TriangleAlert,
    Gauge
} from "lucide-react";

import Loader from "../components/Loader";

function Analytics() {

    const [stats, setStats] = useState(null);

    useEffect(() => {

        async function fetchStats() {

            const response = await axios.get("/dashboard/stats");

            setStats(response.data);

            console.log(response.data);

        }

        fetchStats();

    }, []);

    if (!stats) {
        return <Loader />;
    }
    const categoryData = Object.entries(stats.category_breakdown).map(
        ([key, value]) => ({
            name: key,
            value: value
        })
    );
    const COLORS = [
        "#2563EB",
        "#10B981",
        "#F59E0B",
        "#EF4444",
        "#8B5CF6"
    ];
    const priorityData = Object.entries(stats.priority_distribution).map(
    ([key, value]) => ({
        range: key,
        emails: value
    })
);
    return (

    <div>

        <div className="page-header">

            <h1>📊 Analytics Dashboard</h1>

            <p>
                AI-powered insights from processed emails
            </p>

        </div>

        <div className="stats-grid">

            <StatCard
                title="Total Emails"
                value={stats.total_emails}
                icon={<Mail size={28} />}
                color="#2563EB"
            />

            <StatCard
                title="Average Priority"
                value={stats.average_priority}
                icon={<Gauge size={28} />}
                color="#10B981"
            />

            <StatCard
                title="Spam %"
                value={`${stats.spam_percentage}%`}
                icon={<CircleAlert size={28} />}
                color="#F59E0B"
            />

            <StatCard
                title="Action Needed"
                value={stats.action_needed_emails}
                icon={<TriangleAlert size={28} />}
                color="#EF4444"
            />

        </div>

        <h2 className="analytics-heading">
            Category Distribution
        </h2>

        <div className="chart-container">

            <ResponsiveContainer width="100%" height={350}>

                <PieChart>

                    <Pie
                        data={categoryData}
                        dataKey="value"
                        nameKey="name"
                        outerRadius={120}
                        label
                    >

                        {categoryData.map((entry, index) => (

                            <Cell
                                key={index}
                                fill={COLORS[index % COLORS.length]}
                            />

                        ))}

                    </Pie>

                    <Tooltip />

                    <Legend />

                </PieChart>

            </ResponsiveContainer>

        </div>

        <h2 className="analytics-heading">
            Priority Distribution
        </h2>

        <div className="chart-container">

            <ResponsiveContainer width="100%" height={350}>

                <BarChart data={priorityData}>

                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis dataKey="range" />

                    <YAxis />

                    <Tooltip />

                    <Legend />

                    <Bar
                        dataKey="emails"
                        fill="#4F46E5"
                    />

                </BarChart>

            </ResponsiveContainer>

        </div>

        <div className="analytics-grid">


            {/* Top Senders */}

            <AnalyticsCard title="📧 Top Senders">

                <table className="sender-table">

                    <thead>

                        <tr>

                            <th>Sender</th>

                            <th>Emails</th>

                        </tr>

                    </thead>

                    <tbody>

                        {stats.top_senders.map((item, index) => (

                            <tr key={index}>

                                <td>{item.sender}</td>

                                <td>{item.count}</td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </AnalyticsCard>

            {/* Upcoming Deadlines */}

            <AnalyticsCard title="📅 Upcoming Deadlines">

                {stats.upcoming_deadlines.length === 0 ? (

                    <p>No upcoming deadlines</p>

                ) : (

                    <table className="sender-table">

                        <thead>

                            <tr>

                                <th>Subject</th>

                                <th>Deadline</th>

                            </tr>

                        </thead>

                        <tbody>

                            {stats.upcoming_deadlines.map((item, index) => (

                                <tr key={index}>

                                    <td>{item.subject}</td>

                                    <td>
                                        {new Date(item.deadline).toLocaleString("en-IN", {
                                            day: "2-digit",
                                            month: "short",
                                            year: "numeric",
                                            hour: "2-digit",
                                            minute: "2-digit"
                                        })}
                                    </td>

                                </tr>

                            ))}

                        </tbody>

                    </table>

                )}

            </AnalyticsCard>

        </div>
        <div className="analytics-grid">

            <AnalyticsCard title="🏢 Top Organizations">

                <table className="sender-table">

                    <thead>

                        <tr>

                            <th>Organization</th>

                            <th>Count</th>

                        </tr>

                    </thead>

                    <tbody>

                        {stats.top_organizations.map((item, index) => (

                            <tr key={index}>

                                <td>{item[0]}</td>

                                <td>{item[1]}</td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </AnalyticsCard>

            <AnalyticsCard title="👥 Top People">

                <table className="sender-table">

                    <thead>

                        <tr>

                            <th>Person</th>

                            <th>Count</th>

                        </tr>

                    </thead>

                    <tbody>

                        {stats.top_people.map((item, index) => (

                            <tr key={index}>

                                <td>{item[0]}</td>

                                <td>{item[1]}</td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </AnalyticsCard>

        </div>

        <div className="analytics-grid">

            <AnalyticsCard title="📍 Top Locations">

                <table className="sender-table">

                    <thead>

                        <tr>

                            <th>Location</th>

                            <th>Count</th>

                        </tr>

                    </thead>

                    <tbody>

                        {stats.top_locations.map((item, index) => (

                            <tr key={index}>

                                <td>{item[0]}</td>

                                <td>{item[1]}</td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </AnalyticsCard>

            <AnalyticsCard title="🔥 Urgent Emails">

                <div className="urgent-card">

                    <h1>{stats.urgent_emails}</h1>

                    <p>Require Immediate Attention</p>

                </div>

            </AnalyticsCard>

        </div>
    
        <div className="analytics-footer">

            Generated using AI Email Intelligence Platform

        </div>
    </div>

);
}

export default Analytics;